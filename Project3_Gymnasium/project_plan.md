# Finalny plan projektu: Podstawy Gymnasium

## Część 1: Zadanie na 4 punkty — FrozenLake + Q-learning

### Środowisko

`FrozenLake-v1`, wersja `4x4`, `is_slippery=True`.

Krótkie przypomnienie zasad: agent zaczyna w lewym górnym rogu (S), musi dotrzeć do celu (G) w prawym dolnym rogu, omijając dziury (H). Na "lodzie" (F) może się poślizgnąć - przy `is_slippery=True` akcja "idź w prawo" tylko z prawdopodobieństwem 1/3 faktycznie przesuwa w prawo, a z prawdopodobieństwem 2/3 prostopadle (góra/dół). To wprowadza stochastyczność.

- Przestrzeń stanów: `Discrete(16)` — pozycje 0-15 na siatce 4x4
- Przestrzeń akcji: `Discrete(4)` — 0=lewo, 1=dół, 2=prawo, 3=góra
- Nagroda: +1 za dotarcie do celu, 0 wszędzie indziej (rzadka nagroda!)
- Epizod kończy się: dotarcie do G, wpadnięcie w H, lub timeout (100 kroków domyślnie)

### Algorytm: Tabularyczny Q-learning

Wzór aktualizacji (off-policy, bootstrapping):

```
Q(s, a) ← Q(s, a) + α · [r + γ · max_a' Q(s', a') − Q(s, a)]
```

Gdzie:
- α — learning rate (np. 0.1)
- γ — współczynnik dyskontowy (wymagane 0.9)
- r — natychmiastowa nagroda
- max_a' Q(s', a') — najlepsza wartość Q w następnym stanie (off-policy bo zakładamy greedy w przyszłości)

Eksploracja: **ε-greedy** z malejącym ε:
- start: ε = 1.0 (pełna eksploracja)
- koniec: ε = 0.01 (prawie pełna eksploatacja)
- spadek: liniowy lub eksponencjalny przez np. 80% epizodów

### Struktura kodu

```python
import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt

# Hiperparametry
ALPHA = 0.1
GAMMA = 0.9
EPSILON_START = 1.0
EPSILON_END = 0.01
EPSILON_DECAY_EPISODES = 4000
N_EPISODES = 5000

env = gym.make("FrozenLake-v1", is_slippery=True)
n_states = env.observation_space.n
n_actions = env.action_space.n
Q = np.zeros((n_states, n_actions))

rewards_history = []

for episode in range(N_EPISODES):
    state, _ = env.reset()
    epsilon = max(EPSILON_END, 
                  EPSILON_START - (EPSILON_START - EPSILON_END) * episode / EPSILON_DECAY_EPISODES)
    
    total_reward = 0
    done = False
    while not done:
        # ε-greedy
        if np.random.random() < epsilon:
            action = env.action_space.sample()
        else:
            action = np.argmax(Q[state])
        
        next_state, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated
        
        # Q-learning update
        best_next_q = np.max(Q[next_state]) if not terminated else 0
        Q[state, action] += ALPHA * (reward + GAMMA * best_next_q - Q[state, action])
        
        state = next_state
        total_reward += reward
    
    rewards_history.append(total_reward)
```

Ważny szczegół: gdy `terminated=True`, nie ma "następnego stanu" w sensie MDP, więc target to po prostu `r` (bez członu γ·Q). To częsty błąd początkujący - pomylenie `terminated` z `truncated`.

### Krzywa uczenia

Surowa nagroda dla pojedynczego epizodu jest 0 lub 1, więc bezpośredni wykres jest nieczytelny. Należy uśrednić w oknie kroczącym (np. 100 epizodów):

```python
window = 100
moving_avg = np.convolve(rewards_history, np.ones(window)/window, mode='valid')
plt.plot(moving_avg)
plt.xlabel('Epizod')
plt.ylabel('Średni success rate (okno 100)')
plt.title('Krzywa uczenia Q-learning na FrozenLake')
```

Spodziewasz się, że krzywa zacznie od ~0.0, będzie powoli rosnąć i ustabilizuje się w okolicach 0.7-0.75 (przy `is_slippery=True` nigdy nie osiągniesz 100% bo środowisko jest stochastyczne).

### Co opisać w sprawozdaniu (~1 strona)

- Opis środowiska FrozenLake i jego stochastyczności
- Wzór Q-learning z wyjaśnieniem każdego członu
- Strategia eksploracji ε-greedy z malejącym ε
- Hiperparametry użyte w eksperymencie
- Wykres krzywej uczenia z komentarzem
- Wizualizacja nauczonej polityki (strzałki na siatce 4x4) — bardzo efektowne, łatwe do zrobienia

---

## Część 2: Zadanie na 6 punktów — CartPole + Q-learning z dyskretyzacją obserwacji

### Środowisko

`CartPole-v1`. Klasyczny problem balansowania: drążek jest zamocowany przegubem (bez własnego napędu) na wózku, który może się poruszać po torze. Cel: utrzymać drążek pionowo, pchając wózek w lewo lub prawo.

- **Obserwacja**: `Box(4,)` ciągła:
  - pozycja wózka ∈ [-4.8, 4.8] (epizod kończy się przy ±2.4)
  - prędkość wózka ∈ (-∞, +∞) — w praktyce w okolicach ±3
  - kąt drążka ∈ [-0.418, 0.418] rad (epizod kończy się przy ±0.209 rad ≈ ±12°)
  - prędkość kątowa drążka ∈ (-∞, +∞) — w praktyce w okolicach ±3.5
- **Akcja**: `Discrete(2)` — 0=push left, 1=push right (już dyskretna!)
- **Nagroda**: **+1 za każdy krok**, w którym drążek się utrzymał (gęsta nagroda)
- **Epizod kończy się**: kąt drążka przekroczy ±12°, pozycja wózka przekroczy ±2.4, lub osiągnie 500 kroków
- **Maksymalny zwrot**: 500

Dlaczego CartPole jest świetny do tego projektu:
- **Gęsta nagroda** — agent dostaje sygnał feedback w każdym kroku, nie ma problemu rzadkiej nagrody jak w MountainCar
- **Akcje już dyskretne** — nie musisz dyskretyzować akcji, tylko obserwację
- **Brak konieczności reward shapingu** — środowisko działa "out of the box", więc uczysz oryginalnej funkcji celu
- Klasyczny benchmark RL — dobrze udokumentowany, prowadzący doskonale go zna

### Strategia: dyskretyzacja obserwacji

Skoro tabularyczny Q-learning wymaga dyskretnych stanów, musimy "udyskretnić" 4-wymiarową obserwację ciągłą.

**Ważna obserwacja praktyczna**: nie wszystkie wymiary obserwacji są równie ważne. Z doświadczenia społeczności RL: **kąt drążka i prędkość kątowa są dużo ważniejsze** niż pozycja i prędkość wózka. Dlatego rozsądnie jest dać im więcej binów. To ciekawy temat do dyskusji w sprawozdaniu — pokazuje, że dyskretyzacja nie jest "głupim binningiem" tylko wymaga zrozumienia dynamiki problemu.

Drugi praktyczny szczegół: prędkości w CartPole są **teoretycznie nieograniczone** (`-inf, +inf`), więc musisz je przyciąć empirycznie do rozsądnego zakresu. Wartości ±3 dla prędkości wózka i ±3.5 dla prędkości kątowej drążka są standardem w literaturze.

```python
# Granice empiryczne dla każdego wymiaru
state_bounds = [
    (-2.4, 2.4),    # pozycja wózka (granica epizodu)
    (-3.0, 3.0),    # prędkość wózka (przycięcie empiryczne)
    (-0.21, 0.21),  # kąt drążka (~12° w radianach, granica epizodu)
    (-3.5, 3.5),    # prędkość kątowa drążka (przycięcie empiryczne)
]

# Granularność dyskretyzacji - więcej binów dla "ważniejszych" wymiarów
N_BINS = [6, 12, 12, 12]

def discretize(obs):
    indices = []
    for i, (low, high) in enumerate(state_bounds):
        clipped = np.clip(obs[i], low, high)
        # Skala 0..1, potem mnożymy przez liczbę binów
        bin_idx = int((clipped - low) / (high - low) * N_BINS[i])
        bin_idx = min(bin_idx, N_BINS[i] - 1)  # zabezpieczenie przed indeksem max+1
        indices.append(bin_idx)
    return tuple(indices)
```

Q-table jest **wielowymiarowa**: `Q = np.zeros(N_BINS + [n_actions])`, czyli kształtu `(6, 12, 12, 12, 2) = 10368 komórek`. To wciąż rozsądna liczba.

### Eksperyment z trzema współczynnikami dyskontowymi (wymagane na 6 pkt)

Uruchom trening 3 razy z γ ∈ {0.5, 0.9, 0.99}, każdorazowo zapisując krzywą uczenia. Co spodziewać się zaobserwować:

- **γ = 0.5**: agent jest "krótkowzroczny" — słabo wartościuje przyszłe nagrody. W CartPole nawet ten γ powinien dać uczącą się politykę, ale z gorszymi wynikami (kilkadziesiąt-100 kroków średnio). Dlaczego? Bo nawet krótkowzrocznie agent dostrzega, że "zaraz mi się zwali" i próbuje to korygować.
- **γ = 0.9**: standard, powinien dotrzeć do dobrych wyników (200-400 kroków średnio).
- **γ = 0.99**: bardzo dalekowzroczny, powinien uzyskać najlepsze wyniki końcowe (zbliżone do max 500), ale wartości Q rosną mocno (suma wielu kroków po +1), więc uczenie może być wolniejsze i mniej stabilne na początku. Może wymagać niższego α dla pełnej stabilności.

W przeciwieństwie do MountainCar, **wszystkie trzy γ powinny dać uczące się polityki** — to jest lepsze do porównania, bo widzisz ilościowe różnice, a nie binarny wynik (uczy się / nie uczy się).

### Struktura kodu (kluczowe fragmenty)

```python
import gymnasium as gym
import numpy as np

env = gym.make("CartPole-v1")

# Hiperparametry
ALPHA = 0.1
GAMMA = 0.9  # zmieniaj na 0.5 i 0.99 w innych runach
EPSILON_START = 1.0
EPSILON_END = 0.05
N_EPISODES = 2000

# Dyskretyzacja
state_bounds = [(-2.4, 2.4), (-3.0, 3.0), (-0.21, 0.21), (-3.5, 3.5)]
N_BINS = [6, 12, 12, 12]
N_ACTIONS = env.action_space.n  # = 2

def discretize(obs):
    indices = []
    for i, (low, high) in enumerate(state_bounds):
        clipped = np.clip(obs[i], low, high)
        bin_idx = int((clipped - low) / (high - low) * N_BINS[i])
        bin_idx = min(bin_idx, N_BINS[i] - 1)
        indices.append(bin_idx)
    return tuple(indices)

Q = np.zeros(N_BINS + [N_ACTIONS])

rewards_history = []

for episode in range(N_EPISODES):
    obs, _ = env.reset()
    state = discretize(obs)
    epsilon = max(EPSILON_END, EPSILON_START * (1 - episode / N_EPISODES))
    
    total_reward = 0
    done = False
    while not done:
        if np.random.random() < epsilon:
            action = np.random.randint(N_ACTIONS)
        else:
            action = np.argmax(Q[state])
        
        next_obs, reward, terminated, truncated, _ = env.step(action)
        next_state = discretize(next_obs)
        done = terminated or truncated
        
        # Q-learning update
        best_next_q = np.max(Q[next_state]) if not terminated else 0
        Q[state + (action,)] += ALPHA * (reward + GAMMA * best_next_q - Q[state + (action,)])
        
        state = next_state
        total_reward += reward
    
    rewards_history.append(total_reward)
```

Zwróć uwagę na trick z indeksowaniem: `Q[state + (action,)]` — `state` to krotka 4 indeksów, dodajemy do niej akcję jako 5ty indeks, dostajemy pojedynczą wartość Q. Alternatywnie możesz spłaszczyć stan do jednego indeksu, ale wielowymiarowy Q-table jest czytelniejszy.

### Krzywa uczenia

Tu nie potrzebujesz reward shapingu, więc krzywa uczenia jest bezpośrednia: średnia długość epizodu (= suma nagród) w oknie kroczącym 100 epizodów. Spodziewasz się rosnącej krzywej od ~20 (losowa polityka) do ~200-500 zależnie od γ i hiperparametrów.

### Co opisać w sprawozdaniu (~1.5 strony)

- Opis środowiska CartPole, ciągłość przestrzeni obserwacji, dyskretność akcji
- **Strategia dyskretyzacji**: dlaczego nierówny rozkład binów (więcej dla kąta i prędkości kątowej), uzasadnienie granic empirycznych dla nieograniczonych wymiarów
- Algorytm Q-learning (możesz odwołać się do Części 1, ale podkreśl że teraz na dyskretyzowanej przestrzeni o znacznie większej liczbie stanów)
- **Wyniki dla γ ∈ {0.5, 0.9, 0.99}**: 3 krzywe uczenia na jednym wykresie + dyskusja
- Komentarz: dlaczego niski γ daje gorsze wyniki, dlaczego wysoki γ uczy się wolniej

---

## Część 3: Zadanie na 8 punktów — dodanie SARSA i optymalizacja hiperparametrów

### Drugi algorytm: SARSA

SARSA różni się od Q-learning jednym członem aktualizacji:

```
Q(s, a) ← Q(s, a) + α · [r + γ · Q(s', a') − Q(s, a)]
```

Zamiast `max_a' Q(s', a')` używasz `Q(s', a')` gdzie `a'` to akcja, którą **faktycznie wybierzesz** w następnym stanie (zgodnie z polityką ε-greedy).

Konsekwencje teoretyczne:
- **Q-learning** jest **off-policy**: uczy się optymalnej polityki niezależnie od tego, jak eksploruje. Zakłada w każdym kroku, że w przyszłości będzie wybierać greedy.
- **SARSA** jest **on-policy**: uczy się polityki, którą faktycznie wykonuje (z eksploracją włącznie). Bardziej "bezpieczny", bo bierze pod uwagę ryzyko wynikające z eksploracji.

W praktyce: SARSA zwykle daje bardziej **konserwatywne** polityki, które unikają ryzyka. W środowisku z karami (np. dziury w FrozenLake albo upadek z klifu w klasycznym Cliff Walking) SARSA woli bezpieczną dłuższą trasę, podczas gdy Q-learning prze do najkrótszej nawet jeśli jest ryzykowna. W CartPole różnica będzie subtelniejsza, ale teoretycznie SARSA powinna być nieco bardziej stabilna podczas treningu (mniej oscylacji).

### Implementacja SARSA (różnica vs Q-learning)

Kluczowa różnica strukturalna: musisz wybrać następną akcję **przed** aktualizacją Q.

```python
for episode in range(N_EPISODES):
    obs, _ = env.reset()
    state = discretize(obs)
    
    # Wybierz pierwszą akcję
    if np.random.random() < epsilon:
        action = np.random.randint(N_ACTIONS)
    else:
        action = np.argmax(Q[state])
    
    done = False
    while not done:
        next_obs, reward, terminated, truncated, _ = env.step(action)
        next_state = discretize(next_obs)
        done = terminated or truncated
        
        # Wybierz następną akcję (potrzebna do update'u)
        if np.random.random() < epsilon:
            next_action = np.random.randint(N_ACTIONS)
        else:
            next_action = np.argmax(Q[next_state])
        
        # SARSA update
        next_q = Q[next_state + (next_action,)] if not terminated else 0
        Q[state + (action,)] += ALPHA * (reward + GAMMA * next_q - Q[state + (action,)])
        
        state = next_state
        action = next_action  # ważne: używamy tej samej akcji w następnym kroku
```

### Porównanie algorytmów (do sprawozdania)

Uruchom po **kilka seedów** dla każdego algorytmu (np. 5 seedów × 2000 epizodów) i porównaj:

1. **Krzywe uczenia** (średnia ± odchylenie standardowe w pasie cieniowanym)
2. **Końcowa wydajność** (średnia długość epizodu w ostatnich 100 epizodach)
3. **Stabilność** (variance między seedami)
4. **Charakterystyka nauczonej polityki** (czy SARSA jest bardziej stabilna podczas treningu?)

Ten kawałek z wieloma seedami jest **bardzo ważny**. Pojedyncze runy w RL są bardzo zaszumione — dwa runy z różnymi seedami mogą dać kompletnie różne krzywe. Bez uśredniania porównanie nie ma wartości statystycznej.

### Optymalizacja hiperparametrów

Wymagane: zoptymalizuj hiperparametry algorytmów względem **całkowitej zdyskontowanej nagrody w 1000 pierwszych epizodach** (lub krokach).

Zdefiniuj funkcję celu:

```python
def total_discounted_reward(rewards_history, gamma=0.9):
    return sum(r * (gamma ** i) for i, r in enumerate(rewards_history[:1000]))
```

Hiperparametry do optymalizacji:
- `ALPHA` (learning rate): np. {0.01, 0.05, 0.1, 0.3, 0.5}
- `EPSILON_DECAY` (jak szybko maleje ε): np. 3 warianty
- `N_BINS` (granularność dyskretyzacji): np. konfiguracje `[4,8,8,8]`, `[6,12,12,12]`, `[8,16,16,16]`

Dwa podejścia:

**Opcja A: Grid search ręczny** — szybki, prosty, wystarczy na ten projekt. Wybierz 2-3 najważniejsze hiperparametry, zrób grid search po sensownej siatce, narysuj heatmapę wyników.

**Opcja B: Optuna** — biblioteka do automatycznej optymalizacji hiperparametrów (Bayesian optimization). Bardziej "wow" w sprawozdaniu, ale wymaga nauczenia się Optuny.

Polecam Opcję A z grid searchem na 2 hiperparametrach (np. α i granularność dyskretyzacji) → masz heatmapę 5×3 = 15 runów dla każdego z 2 algorytmów = 30 runów. Każdy run to ~1000 epizodów, w czystym NumPy CartPole liczy się szybko, cały eksperyment ~kilkanaście minut.

**Bardzo ważne**: dla każdej kombinacji hiperparametrów uruchom przynajmniej 3 seedy i uśrednij. Inaczej szum optymalizacyjny zdominuje sygnał i wybierzesz zwycięzcę przypadkowo.

### Co opisać w sprawozdaniu (~1 strona dodatkowo)

- Opis algorytmu SARSA z naciskiem na różnicę vs Q-learning
- Dyskusja teoretyczna: on-policy vs off-policy, co to znaczy w praktyce
- Wykres porównawczy krzywych uczenia (Q-learning vs SARSA, średnia ± std)
- Tabela / heatmapa wyników optymalizacji hiperparametrów
- Wybrane optymalne hiperparametry dla obu algorytmów
- Ostateczne porównanie: który algorytm wygrał i dlaczego

---

## Sugerowana struktura projektu (struktura plików)

```
projekt3_rl/
├── frozen_lake/
│   ├── q_learning_frozen.py      # Część 1
│   └── plots/
├── cart_pole/
│   ├── q_learning_cp.py           # Część 2 + część 3
│   ├── sarsa_cp.py                # Część 3
│   ├── hyperparam_search.py       # Część 3
│   └── plots/
├── utils/
│   ├── discretization.py          # współdzielona logika dyskretyzacji
│   └── plotting.py                # współdzielone funkcje rysowania
├── sprawozdanie.pdf
└── README.md
```

## Sugerowany harmonogram (deadline 2025-04-29)

Zakładając że masz ~3 tygodnie:

- **Tydzień 1**: FrozenLake + Q-learning (Część 1), powinno zająć max 1-2 wieczory + podstawy CartPole (uruchomienie środowiska, dyskretyzacja, pierwszy działający Q-learning bez optymalizacji)
- **Tydzień 2**: CartPole — eksperyment z 3 współczynnikami γ, dostrajanie granularności dyskretyzacji, implementacja SARSA
- **Tydzień 3**: Optymalizacja hiperparametrów, finalne wykresy, pisanie sprawozdania

## Najczęstsze pułapki, na które uważać

1. **`terminated` vs `truncated`**: target Q powinien być `r` tylko gdy `terminated=True` (epizod skończył się "naturalnie"). Gdy `truncated=True` (timeout, w CartPole = osiągnięto 500 kroków), powinieneś dalej bootstrapować z `Q[next_state]` bo MDP się nie zakończył — środowisko cię tylko ucięło. To szczególnie ważne w CartPole, gdzie najlepsze epizody kończą się przez timeout!

2. **Przycinanie obserwacji**: prędkości w CartPole są nieograniczone teoretycznie, ale w praktyce mieszczą się w ~±3. Jeśli nie przyciąć, możesz dostać `bin_idx` poza zakresem i `IndexError`. Funkcja `np.clip` + `min(bin_idx, N_BINS[i]-1)` zabezpiecza.

3. **Pojedyncze seedy w RL**: NIGDY nie wnioskuj z pojedynczego runa. Zawsze uśredniaj 3-5 seedów minimum.

4. **Brak resetu Q-table między eksperymentami**: jeśli porównujesz różne γ w pętli, pamiętaj o re-inicjalizacji Q.

5. **`gym` vs `gymnasium`**: instaluj `pip install gymnasium`, importuj `import gymnasium as gym`. Większość przykładów online używa starej nazwy `gym` — kod jest prawie identyczny ale API zwraca 5-tuple z `step()` (`obs, reward, terminated, truncated, info`) zamiast starych 4-tuple.

6. **Indeksowanie wielowymiarowego Q-table**: `Q[state + (action,)]` gdzie `state` jest krotką. Łatwo o pomyłkę z `Q[state, action]` (które działa tylko dla 1D-state). Możesz alternatywnie spłaszczyć stan do jednego indeksu funkcją typu `np.ravel_multi_index`, ale wielowymiarowa wersja jest czytelniejsza.

7. **Nierówna granularność dyskretyzacji**: jeśli dasz 6 binów dla kąta drążka zamiast 12, polityka się nie nauczy dobrze, bo "ważny" wymiar straci rozdzielczość. To jest świetne do pokazania w sprawozdaniu — uruchom run z `[6,6,6,6]` vs `[6,12,12,12]` i porównaj.
