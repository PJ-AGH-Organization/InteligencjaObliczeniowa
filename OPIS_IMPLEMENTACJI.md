# Rolling Ball Navigator — Szczegółowy opis implementacji

## Spis treści

1. [Ogólna koncepcja projektu](#1-ogólna-koncepcja-projektu)
2. [Stałe i parametry świata](#2-stałe-i-parametry-świata)
3. [Układ przeszkód](#3-układ-przeszkód)
4. [Definicja środowiska `RollingBallEnv`](#4-definicja-środowiska-rollingballenv)
   - 4.1 [Przestrzeń obserwacji](#41-przestrzeń-obserwacji)
   - 4.2 [Przestrzeń akcji](#42-przestrzeń-akcji)
5. [Reset epizodu (`reset`)](#5-reset-epizodu-reset)
6. [Krok symulacji (`step`)](#6-krok-symulacji-step)
   - 6.1 [Fizyka ruchu](#61-fizyka-ruchu)
   - 6.2 [Kolizja ze ścianami](#62-kolizja-ze-ścianami)
   - 6.3 [Kolizja z przeszkodami](#63-kolizja-z-przeszkodami)
   - 6.4 [Warunki zakończenia epizodu](#64-warunki-zakończenia-epizodu)
   - 6.5 [Funkcja nagrody](#65-funkcja-nagrody)
7. [Czujniki odległości (Raycasting)](#7-czujniki-odległości-raycasting)
   - 7.1 [Rzut promienia — ściany](#71-rzut-promienia--ściany)
   - 7.2 [Rzut promienia — prostokąt AABB](#72-rzut-promienia--prostokąt-aabb)
8. [Wektor obserwacji — pełny opis](#8-wektor-obserwacji--pełny-opis)
9. [Renderowanie (Pygame)](#9-renderowanie-pygame)
10. [Trening — Soft Actor-Critic (SAC)](#10-trening--soft-actor-critic-sac)
    - 10.1 [Wybór algorytmu](#101-wybór-algorytmu)
    - 10.2 [Hiperparametry SAC](#102-hiperparametry-sac)
    - 10.3 [Callback ewaluacyjny](#103-callback-ewaluacyjny)
    - 10.4 [Artefakty treningu](#104-artefakty-treningu)
11. [Krzywa uczenia](#11-krzywa-uczenia)
12. [Ewaluacja modelu](#12-ewaluacja-modelu)
13. [Wizualizacja wyuczonej polityki](#13-wizualizacja-wyuczonej-polityki)
    - 13.1 [Nagranie wideo (MP4)](#131-nagranie-wideo-mp4)
    - 13.2 [Tryb na żywo (Pygame)](#132-tryb-na-żywo-pygame)
14. [Wyniki](#14-wyniki)
15. [Podsumowanie przepływu danych](#15-podsumowanie-przepływu-danych)

---

## 1. Ogólna koncepcja projektu

**Rolling Ball Navigator** to autorskie środowisko Gymnasium zaimplementowane na potrzeby Projektu 4 z przedmiotu Inteligencja Obliczeniowa.

Zadanie: kulka tocząca się po dwuwymiarowej planszy musi dotrzeć do wyznaczonego celu (grafika z `sprites/goal.png`, skalowana do promienia `GOAL_RADIUS`), omijając sześć statycznych prostokątnych przeszkód. Kulka jest rysowana z `sprites/agent.png`. Agent **nie zna swojej pozycji absolutnej** — nawiguje wyłącznie na podstawie lokalnych obserwacji:

- bieżącej prędkości,
- kierunku wektora do celu,
- odległości do celu,
- ośmiu sensorów radarowych (raycasting) mierzących odległość do najbliższej ściany lub przeszkody w ośmiu kierunkach co 45°.

Środowisko spełnia standardowy interfejs `gym.Env` (`reset`, `step`, `render`, `close`) i jest w pełni kompatybilne z biblioteką `stable-baselines3`.

---

## 2. Stałe i parametry świata

| Stała | Wartość | Opis |
|---|---|---|
| `WORLD_W` | 600.0 px | Szerokość świata |
| `WORLD_H` | 600.0 px | Wysokość świata |
| `BALL_RADIUS` | 12.0 px | Promień kulki |
| `GOAL_RADIUS` | 18.0 px | Promień strefy celu |
| `FRICTION` | 0.92 | Mnożnik tłumienia prędkości (co krok) |
| `FORCE_SCALE` | 0.4 | Skala siły przykładanej przez akcję agenta |
| `V_MAX` | 8.0 px/krok | Maksymalna prędkość kulki (w każdej osi) |
| `MAX_STEPS` | 500 | Maksymalna liczba kroków na epizod |
| `RAY_MAX` | 500.0 px | Maksymalny zasięg promienia czujnika |
| `DIAGONAL` | ≈ 848.5 px | Przekątna świata — używana do normalizacji odległości do celu |
| `RAY_ANGLES` | `[0, 45, 90, 135, 180, 225, 270, 315]` | Kąty czujników radarowych (w stopniach) |

**Prędkość terminalna** (ustalona): przy `FORCE_SCALE = 0.4` i `FRICTION = 0.92` prędkość graniczna wynosi `FORCE_SCALE / (1 − FRICTION) = 0.4 / 0.08 = 5.0 px/krok`, co jest poniżej twardego limitu `V_MAX = 8.0`.

---

## 3. Układ przeszkód

Na planszy znajduje się sześć statycznych, prostokątnych przeszkód (format `(left_x, top_y, width, height)` w pikselach):

| # | left_x | top_y | width | height | Uwagi |
|---|---|---|---|---|---|
| 1 | 80 | 80 | 80 | 200 | wysoka lewa ściana |
| 2 | 280 | 40 | 80 | 160 | środkowy blok górny |
| 3 | 440 | 100 | 100 | 60 | mały prawy blok |
| 4 | 140 | 340 | 160 | 60 | poziomy blok środkowy |
| 5 | 350 | 280 | 60 | 200 | wysoki prawy słup |
| 6 | 460 | 380 | 90 | 130 | prawy dolny blok |

Układ przeszkód jest **stały** (nie losuje się co epizod). Tworzy nietrywialny labirynt wymuszający ominięcie bloków.

---

## 4. Definicja środowiska `RollingBallEnv`

### 4.1 Przestrzeń obserwacji

Wektor obserwacji ma **13 elementów** typu `float32`, wszystkie znormalizowane:

```
observation_space = Box(
    low  = [-1, -1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    high = [ 1,  1,  1,  1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    dtype = float32
)
```

Indeksy 0–4 mają zakres `[-1, 1]` lub `[0, 1]`, indeksy 5–12 (czujniki) mają zakres `[0, 1]`.

### 4.2 Przestrzeń akcji

Wektor akcji ma **2 elementy** typu `float32`:

```
action_space = Box(
    low  = [-1.0, -1.0],
    high = [ 1.0,  1.0],
    dtype = float32
)
```

- `action[0]` = siła w osi X (ujemna — lewo, dodatnia — prawo)
- `action[1]` = siła w osi Y (ujemna — góra, dodatnia — dół, zgodnie z konwencją ekranu)

Akcja **nie jest prędkością** — jest **przyspieszeniem** skalowanym przez `FORCE_SCALE = 0.4`, dodawanym do bieżącej prędkości.

---

## 5. Reset epizodu (`reset`)

Wywołanie `reset()` losuje nowe pozycje startowe kulki i celu przy każdym epizodzie:

1. **Pozycja startowa kulki** — losowana jednostajnie w całym świecie (z marginesem `BALL_RADIUS` od granic), odrzucana jeśli koliduje z którąkolwiek przeszkodą lub ścianą (`_is_free(pos, BALL_RADIUS)`).

2. **Pozycja celu** — losowana tak samo (z marginesem `GOAL_RADIUS`), ale z dodatkowym warunkiem:
   - musi być wolna od przeszkód,
   - odległość od kulki startowej musi być **większa niż 100 px** (zapobiega trywialnym epizodowym).

3. **Zerowanie stanu** — prędkość `_vel = [0, 0]`, licznik kroków `_step_count = 0`.

Oba losowania realizowane są metodą **odrzucania** (pętla `while True` aż do znalezienia wolnego miejsca).

---

## 6. Krok symulacji (`step`)

### 6.1 Fizyka ruchu

Wykonywana w każdym kroku — kolejność operacji:

```python
action = clip(action, -1.0, 1.0)            # obcięcie akcji do [-1, 1]
vel    = clip(vel + action * FORCE_SCALE,    # dodanie przyspieszenia
              -V_MAX, V_MAX)                 # z twardym limitem prędkości
vel   *= FRICTION                            # tłumienie tarcia (0.92 co krok)
pos   += vel                                 # integracja Eulera (Δt = 1 krok)
```

Tarcie modeluje **opór toczenia** — bez akcji agenta kulka stopniowo zwalnia do zera. Mnożnik `0.92` oznacza, że co krok prędkość maleje o 8%.

### 6.2 Kolizja ze ścianami

Po integracji pozycji następuje **odbitowe odbicie** od czterech ścian prostokątnego świata:

- Jeśli kulka wyjdzie poza lewą ścianę: `pos_x = BALL_RADIUS`, `vel_x = abs(vel_x)` (odbicie).
- Jeśli kulka wyjdzie poza prawą ścianę: `pos_x = WORLD_W - BALL_RADIUS`, `vel_x = -abs(vel_x)`.
- Analogicznie dla górnej i dolnej ściany.

Odbicie jest **idealne** (brak utraty energii przy ścianie).

### 6.3 Kolizja z przeszkodami

Dla każdej z sześciu przeszkód wykonywana jest detekcja i rozwiązanie kolizji metodą **circle-vs-AABB**:

1. Znajdź punkt na prostokącie najbliższy środkowi kulki: `(cx, cy) = clip(pos, rect)`.
2. Oblicz odległość `dist` od środka kulki do `(cx, cy)`.
3. Jeśli `dist < BALL_RADIUS` — kolizja:
   - wyznacz normalną powierzchni: `n = (dx/dist, dy/dist)` gdzie `(dx, dy) = pos - (cx, cy)`,
   - przesuń kulkę o `overlap + 0.5` wzdłuż normalnej (depenetracja),
   - odbij składową prędkości wzdłuż normalnej: `vel -= 2 * dot(vel, n) * n` (jeśli kulka poruszała się w kierunku przeszkody).

Brak osobnej kary za uderzenie w przeszkodę — **fizyczne odbicie jest wystarczającym deterrentem**.

### 6.4 Warunki zakończenia epizodu

| Warunek | Flaga | Opis |
|---|---|---|
| `dist ≤ GOAL_RADIUS + BALL_RADIUS` | `terminated = True` | Kulka dotarła do celu — sukces |
| `step_count ≥ MAX_STEPS` (500) | `truncated = True` | Wyczerpano limit kroków — porażka |

Oba warunki są wzajemnie wyłączne w danym kroku (ale `truncated` może nastąpić razem z `terminated` jeśli osiągnie cel dokładnie w 500. kroku).

### 6.5 Funkcja nagrody

```
reward = -0.01 + 0.02 * (prev_dist - dist)
```

oraz przy sukcesie:

```
reward += 50.0
```

Składowe:

| Składowa | Wartość | Rola |
|---|---|---|
| `-0.01` (kara czasowa) | stała, każdy krok | Penalizuje długie epizody, motywuje do dotarcia do celu jak najszybciej |
| `+0.02 * (prev_dist - dist)` (nagroda kształtująca) | zmienna, proporcjonalna do poprawy | Nagradza zbliżanie się do celu, karze oddalanie — gęste sygnały uczące |
| `+50.0` (nagroda terminalna) | tylko przy sukcesie | Silny sygnał za osiągnięcie celu |

**Uwagi projektowe:**

- Współczynnik `0.02` oznacza, że przemieszczenie o 1 px w kierunku celu = nagroda `+0.02`. Przy typowym kroku ~3–5 px nagroda kształtująca wynosi ~`+0.06` do `+0.10` na krok.
- Suma nagrody kształtującej w epizodzie zakończonym sukcesem (po ~123 krokach) wynosi ok. `0.02 * initial_dist − kary_czasowe` ≈ kilka jednostek, co jest dużo mniejsze niż nagroda terminalna 50, więc agent nigdy nie będzie „zawracał" dla dodatkowych kształtujących nagród.
- Brak kary kolizyjnej — fizyczne odbicie jest deterrentem behawioralnym wystarczającym do ominięcia przeszkód.

---

## 7. Czujniki odległości (Raycasting)

Agent posiada **8 czujników odległości** rozmieszczonych co 45° (0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°). Każdy czujnik rzuca promień ze środka kulki i zwraca odległość do pierwszej przeszkody (ściany lub bloku).

Konwencja kątów: 0° = prawo, 90° = góra (oś Y odwrócona — ekran), 180° = lewo, 270° = dół.

### 7.1 Rzut promienia — ściany

```python
dx =  cos(angle_rad)
dy = -sin(angle_rad)   # odwrócenie Y (konwencja ekranu)

t = RAY_MAX
if dx >  1e-9: t = min(t, (WORLD_W - ox) / dx)   # prawa ściana
if dx < -1e-9: t = min(t, -ox / dx)               # lewa ściana
if dy >  1e-9: t = min(t, (WORLD_H - oy) / dy)   # dolna ściana
if dy < -1e-9: t = min(t, -oy / dy)               # górna ściana
```

Gdzie `(ox, oy)` to bieżąca pozycja kulki. Czas `t` to odległość wzdłuż promienia do ściany.

### 7.2 Rzut promienia — prostokąt AABB

Używa standardowego algorytmu **slab method** (przecięcie par połówek-przestrzeni):

```python
t_near = max(t_x_near, t_y_near)
t_far  = min(t_x_far,  t_y_far)

if t_far < t_near or t_near <= 0:
    return RAY_MAX   # brak przecięcia lub prostokąt za kulką
return t_near
```

Obsługuje przypadki degeneracji (promień równoległy do krawędzi AABB).

Wynik każdego czujnika jest **przycięty** do zakresu `[0, RAY_MAX]` i **znormalizowany** przez podzielenie przez `RAY_MAX` przed wstawieniem do wektora obserwacji.

---

## 8. Wektor obserwacji — pełny opis

| Indeks | Symbol | Obliczenie | Zakres | Opis |
|---|---|---|---|---|
| 0 | `vel_x` | `vel[0] / V_MAX` | `[-1, 1]` | Znormalizowana prędkość w osi X |
| 1 | `vel_y` | `vel[1] / V_MAX` | `[-1, 1]` | Znormalizowana prędkość w osi Y |
| 2 | `goal_dx` | `(goal[0] − pos[0]) / dist` | `[-1, 1]` | Składowa X jednostkowego wektora do celu |
| 3 | `goal_dy` | `−(goal[1] − pos[1]) / dist` | `[-1, 1]` | Składowa Y jednostkowego wektora do celu (Y odwrócone) |
| 4 | `goal_dist` | `dist / DIAGONAL` | `[0, 1]` | Znormalizowana odległość do celu (0 = w celu, 1 = przekątna planszy) |
| 5 | `ray_0` | `cast_ray(0°) / RAY_MAX` | `[0, 1]` | Czujnik prawy (0°) |
| 6 | `ray_1` | `cast_ray(45°) / RAY_MAX` | `[0, 1]` | Czujnik prawo-górny (45°) |
| 7 | `ray_2` | `cast_ray(90°) / RAY_MAX` | `[0, 1]` | Czujnik górny (90°) |
| 8 | `ray_3` | `cast_ray(135°) / RAY_MAX` | `[0, 1]` | Czujnik lewo-górny (135°) |
| 9 | `ray_4` | `cast_ray(180°) / RAY_MAX` | `[0, 1]` | Czujnik lewy (180°) |
| 10 | `ray_5` | `cast_ray(225°) / RAY_MAX` | `[0, 1]` | Czujnik lewo-dolny (225°) |
| 11 | `ray_6` | `cast_ray(270°) / RAY_MAX` | `[0, 1]` | Czujnik dolny (270°) |
| 12 | `ray_7` | `cast_ray(315°) / RAY_MAX` | `[0, 1]` | Czujnik prawo-dolny (315°) |

Wszystkie elementy są znormalizowane — sieć neuronowa nie musi samodzielnie uczyć się skalowania.

Indeksy 2–3 razem tworzą **jednostkowy wektor kierunkowy** do celu (długość ≈ 1 przy `dist > 0`). Agent wie więc w którą stronę iść, ale nie gdzie dokładnie jest na planszy.

---

## 9. Renderowanie (Pygame)

Środowisko obsługuje dwa tryby renderowania:

| Tryb | Opis |
|---|---|
| `render_mode="human"` | Okno Pygame wyświetlane na bieżąco @ 30 FPS |
| `render_mode="rgb_array"` | Zwraca klatkę jako `ndarray` kształtu `(600, 600, 3)` |
| `render_mode=None` (domyślny) | Brak renderowania — maksymalna prędkość treningu |

**Elementy wizualne każdej klatki** (zgodnie z `_render_frame` w notebooku):

| Element | Wizualizacja | Opis |
|---|---|---|
| Tło | szachownica kafelków 40×40 px, odcienie brązu `(42,33,24)` / `(50,40,29)`, obramowanie kafelka `(28,20,14)` | Prosta tekstura „podłogi” |
| Obramowanie świata | podwójna ramka `(110,88,64)` oraz `(70,54,38)` | Wewnętrzny obszar gry 600×600 |
| Przeszkody | wypełnienie `(78,64,48)`, kontury i cienie `(108,90,66)` itd. | Sześć prostokątów z listy `OBSTACLES` |
| Promienie czujników | linia `(210,158,38)` | Długość z bieżącej obserwacji (znormalizowana × `RAY_MAX`) |
| Cel | bitmapa `sprites/goal.png` przeskalowana do `(2·GOAL_RADIUS)²` | Pozycja środka: `_goal` |
| Kulka | bitmapa `sprites/agent.png` przeskalowana do `(2·BALL_RADIUS)²` | Pozycja środka: `_pos` |

Kolejność rysowania (od tyłu do przodu): tło → ramy świata → przeszkody → promienie → cel → kulka.

W trybie `"human"` okno Pygame jest tworzone raz (lazy init przy pierwszym `render_mode="human"` i zachowane między krokami). `pygame.Clock.tick(30)` ogranicza FPS do 30.

---

## 10. Trening — Soft Actor-Critic (SAC)

### 10.1 Wybór algorytmu

Użyto algorytmu **Soft Actor-Critic (SAC)** z biblioteki `stable-baselines3`. SAC jest optymalnym wyborem dla:

- **ciągłych przestrzeni akcji** (jak tutaj: `Box([-1,1]²)`),
- środowisk wymagających dobrej **eksploracji** (SAC maksymalizuje entropię polityki),
- zadań z rzadkimi nagrodami (dzięki kształtowaniu nagrody nie jest to tutaj konieczne, ale SAC i tak radzi sobie lepiej niż TD3 czy DDPG w takich warunkach).

SAC jest algorytmem **off-policy** — używa **replay buffer** do wielokrotnego uczenia na tych samych przejściach, co zwiększa efektywność próbkowania.

### 10.2 Hiperparametry SAC

| Hiperparametr | Wartość | Uzasadnienie |
|---|---|---|
| `policy` | `"MlpPolicy"` | Sieć MLP (wejście: obs 13D → wyjście: akcja 2D) |
| `learning_rate` | `3e-4` | Standardowa wartość dla SAC |
| `buffer_size` | `300_000` | Replay buffer na ~600 epizodów — wystarczająco duży |
| `learning_starts` | `5_000` | Pierwsze 5 000 kroków — czysta eksploracja, brak updatów |
| `batch_size` | `256` | Standardowy mini-batch dla SAC |
| `tau` | `0.005` | Miękka aktualizacja target network — powolna, stabilna |
| `gamma` | `0.99` | Horyzont czasowy ~100 kroków — odpowiedni do `MAX_STEPS=500` |
| `ent_coef` | `0.1` (stały) | Wymuszony stały współczynnik entropii — wyłącza auto-tuning |
| `seed` | `42` | Reprodukowalność eksperymentów |
| `total_timesteps` | `500_000` | Łączna liczba kroków treningowych |

**Uwaga o `ent_coef`:** Domyślnie SAC automatycznie dostosowuje współczynnik entropii (`ent_coef="auto"`). Tu jest on zablokowany na `0.1`, co **zapobiega nadmiernemu wzrostowi entropii** na późnym etapie treningu i stabilizuje zbieżność.

**Architektura sieci (domyślna `MlpPolicy`):**

- Actor: `[64, 64]` — dwie ukryte warstwy ReLU, wyjście: `tanh` skalowane do `[-1,1]`
- Critic (×2): `[64, 64]` — dwie oddzielne sieci Q-funkcji (trick podwójnego krytyka)

### 10.3 Callback ewaluacyjny

```python
EvalCallback(
    eval_env,
    best_model_save_path="models/",
    log_path="logs/",
    eval_freq=5_000,
    n_eval_episodes=10,
    deterministic=True,
    render=False,
)
```

| Parametr | Wartość | Opis |
|---|---|---|
| `eval_freq` | `5_000` kroków | Ewaluacja co 5 000 kroków treningowych |
| `n_eval_episodes` | `10` | 10 epizodów ewaluacyjnych przy każdej ewaluacji |
| `deterministic` | `True` | Agent działa bez szumu (greedy) podczas ewaluacji |
| `best_model_save_path` | `"models/"` | Najlepszy model zapisywany jako `models/best_model.zip` |
| `log_path` | `"logs/"` | Logi ewaluacji zapisywane jako `logs/evaluations.npz` |

Łącznie w trakcie 500 000 kroków treningu EvalCallback wywołuje się **100 razy** (co 5 000 kroków), przeprowadzając każdorazowo 10 deterministycznych epizodów.

### 10.4 Artefakty treningu

| Plik | Opis |
|---|---|
| `models/best_model.zip` | Model z najwyższą średnią nagrodą ewaluacyjną |
| `models/rolling_ball_final.zip` | Model z ostatniego kroku treningu |
| `logs/evaluations.npz` | Historia ewaluacji: `timesteps`, `results` (rewards), `ep_lengths` |

---

## 11. Krzywa uczenia

Po zakończeniu treningu wczytywany jest plik `logs/evaluations.npz` i rysowany wykres:

```python
evaluations  = np.load("logs/evaluations.npz")
timesteps    = evaluations["timesteps"]
mean_rewards = evaluations["results"].mean(axis=1)   # średnia po 10 epizodach
std_rewards  = evaluations["results"].std(axis=1)    # odchylenie standardowe
```

Wykres zawiera:
- linię średniej nagrody (kolor `steelblue`),
- przezroczysty (α=0.25) pas ±1 odchylenia standardowego,
- poziomą linię zerową (szara, przerywana),
- osie: X = kroki treningowe, Y = nagroda epizodu.

Wykres zapisywany do `training_curve.png` (150 DPI).

---

## 12. Ewaluacja modelu

Po treningu wczytywany jest model `models/best_model` i uruchamiany deterministycznie na **30 epizodach ewaluacyjnych** z różnymi ziarnami losowości (`seed=ep` dla `ep` w `0..29`):

```python
model = SAC.load("models/best_model")
for ep in range(30):
    obs, _ = eval_env.reset(seed=ep)
    # pętla step() aż do terminated lub truncated
```

Mierzone metryki:

| Metryka | Opis |
|---|---|
| **Skuteczność** | Odsetek epizodów zakończonych przez `terminated` (dotarcie do celu) |
| **Średnia nagroda** | Suma nagród na epizod, uśredniona ± odch. std. |
| **Średnia liczba kroków** | Kroki do zakończenia epizodu (sukces lub truncated), uśrednione ± odch. std. |

**Wyniki (najlepszy model, 30 epizodów):**

| Metryka | Wynik |
|---|---|
| Skuteczność | **100.0%** (30/30 epizodów zakończonych sukcesem) |
| Średnia nagroda | **54.90 ± 1.56** |
| Średnia liczba kroków | **123.3 ± 76.2** |

Wysoka wariancja liczby kroków (76 kroków std) wynika z losowości pozycji startowej i celu — niektóre epizody są bliskie (krótkie trasy), inne wymagają omijania przeszkód (długie trasy).

---

## 13. Wizualizacja wyuczonej polityki

### 13.1 Nagranie wideo (MP4)

Komórka notebooka zapisuje **kilka kolejnych epizodów** w trybie `rgb_array` do pliku `episode.mp4` (`imageio.v2`), 30 FPS, klatka w rozmiarze świata `600×600`:

```python
import imageio.v2 as imageio
from stable_baselines3 import SAC

model   = SAC.load("models/best_model")
rec_env = RollingBallEnv(render_mode="rgb_array")

frames = []
for ep in range(5):
    obs, _ = rec_env.reset(seed=None)
    frames.append(rec_env.render())
    while True:
        action, _ = model.predict(obs, deterministic=True)
        obs, _, terminated, truncated, _ = rec_env.step(action)
        frames.append(rec_env.render())
        if terminated or truncated:
            break
rec_env.close()

imageio.mimwrite("episode.mp4", frames, fps=30)
```

| Parametr | Wartość |
|---|---|
| Format | MP4 (kodek zależny od `imageio`/FFmpeg w środowisku) |
| Rozmiar klatki | 600×600 px (bez dodatkowego skalowania) |
| FPS | 30 |
| Liczba klatek | zmienna — suma długości nagranych epizodów |

### 13.2 Tryb na żywo (Pygame)

Osobna komórka uruchamia **10 kolejnych epizodów** w oknie Pygame w czasie rzeczywistym:

```python
live_env = RollingBallEnv(render_mode="human")
for episode in range(10):
    obs, _ = live_env.reset()
    while True:
        action, _ = model.predict(obs, deterministic=True)
        obs, _, terminated, truncated, _ = live_env.step(action)
        if terminated or truncated:
            break
```

Odtwarzanie @ 30 FPS (wymuszane przez `pygame.Clock`). Zamknięcie okna Pygame lub przerwanie kernela kończy pętlę.

---

## 14. Wyniki

| Metryka | Wartość |
|---|---|
| Łączne kroki treningu | 500 000 |
| Skuteczność (ewaluacja 30 epizodów) | **100%** |
| Średnia nagroda epizodu | **54.90 ± 1.56** |
| Średnia długość epizodu | **123.3 ± 76.2 kroków** |
| Nagranie demonstracyjne | `episode.mp4` — kilka epizodów, długość zależy od trajektorii |

Agent osiąga **100% skuteczność** w docieraniu do celu, radząc sobie z każdym losowym układem startowym i celem na planszy z sześcioma przeszkodami.

---

## 15. Podsumowanie przepływu danych

```
reset()
  │
  ├─ losowanie pos_kulki (brak kolizji z przeszkodami)
  ├─ losowanie pos_celu  (wolne miejsce, dist > 100)
  └─ vel = [0,0], step_count = 0
       │
       ▼
  ┌──────────────────────────────────────────────────┐
  │  krok symulacji (step)                           │
  │                                                  │
  │  akcja agenta [fx, fy] ∈ [-1,1]²                │
  │        ↓                                         │
  │  vel = clip(vel + action*0.4, -8, 8)            │
  │  vel *= 0.92   (tarcie)                          │
  │  pos += vel    (całkowanie Eulera)               │
  │        ↓                                         │
  │  _resolve_walls()      (odbicie od granic)       │
  │  _resolve_obstacle()×6 (odbicie od bloków)       │
  │        ↓                                         │
  │  nagroda = -0.01 + 0.02*(prev_dist - dist)      │
  │  [+ 50 jeśli terminated]                         │
  │        ↓                                         │
  │  obserwacja = [vel/8, vel/8,                     │
  │                goal_dir_x, goal_dir_y,           │
  │                dist/848.5,                       │
  │                ray0..ray7 / 500]                 │
  └──────────────────────────────────────────────────┘
       │
       ▼
  SAC (MlpPolicy 13→[64,64]→2)
  ├─ Actor:  obs → μ,σ → akcja (z reparametryzacją)
  └─ Critic: (obs, akcja) → Q-wartość (×2 sieci)
       │
       ├─ Replay buffer (300 000 przejść)
       ├─ Batch 256, lr=3e-4, τ=0.005
       └─ EvalCallback co 5 000 kroków → best_model.zip
```
