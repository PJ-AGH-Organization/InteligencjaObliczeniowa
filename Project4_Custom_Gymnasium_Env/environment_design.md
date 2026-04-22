# Projekt 4 — Opis środowiska: Rolling Ball Navigator

## Ogólna koncepcja

Kulka tocząca się po planszy musi dotrzeć do wyznaczonego celu, omijając po drodze przeszkody.
Agent uczy się nawigacji wyłącznie na podstawie lokalnych obserwacji (prędkość, kierunek do celu, sensory odległości) — nie zna swojej pozycji absolutnej.

---

## Plansza

- Prostokątna, płaska, 2D
- Stałe ściany na granicach planszy
- Zestaw statycznych przeszkód (prostokąty) rozmieszczonych na planszy
- Układ przeszkód jest stały między epizodami (hardkodowany)
- Na starcie każdego epizodu losowane są: pozycja startowa kulki i pozycja celu (w miejscach wolnych od przeszkód)

---

## Kulka — fizyka ruchu

Każdy krok czasowy:

```
vel += action * force_scale
vel *= friction              # tłumienie, np. 0.95
pos += vel
pos = clip(pos, granice)     # nie wychodzimy poza planszę
```

- Kulka **nie skręca** — agent przykłada siłę w dowolnym kierunku 2D
- Tłumienie (`friction < 1`) zapobiega nieskończonemu przyspieszaniu
- Przy kolizji ze ścianą lub przeszkodą: odbicie (odpowiednia składowa prędkości zmienia znak)

---

## Przestrzeń obserwacji

Ciągła (`spaces.Box`, `dtype=float32`), wektor 13 liczb rzeczywistych:

| Indeks | Wartość | Zakres |
|--------|---------|--------|
| 0 | `vel_x` — prędkość kulki w osi X | `[-v_max, v_max]` |
| 1 | `vel_y` — prędkość kulki w osi Y | `[-v_max, v_max]` |
| 2 | `goal_dx` — znormalizowany kierunek do celu (X) | `[-1, 1]` |
| 3 | `goal_dy` — znormalizowany kierunek do celu (Y) | `[-1, 1]` |
| 4 | `goal_dist` — odległość euklidesowa do celu | `[0, diagonal]` |
| 5 | `ray_0` — sensor odległości do ścian, kąt 0° (prawo) | `[0, ray_max]` |
| 6 | `ray_1` — sensor odległości, kąt 45° | `[0, ray_max]` |
| 7 | `ray_2` — sensor odległości, kąt 90° (góra) | `[0, ray_max]` |
| 8 | `ray_3` — sensor odległości, kąt 135° | `[0, ray_max]` |
| 9 | `ray_4` — sensor odległości, kąt 180° (lewo) | `[0, ray_max]` |
| 10 | `ray_5` — sensor odległości, kąt 225° | `[0, ray_max]` |
| 11 | `ray_6` — sensor odległości, kąt 270° (dół) | `[0, ray_max]` |
| 12 | `ray_7` — sensor odległości, kąt 315° | `[0, ray_max]` |

**Sensory odległości (raycasting):** każdy promień jest wysyłany z pozycji kulki w danym kierunku i mierzy odległość do najbliższej ściany lub przeszkody. Wartość jest obcinana do `ray_max`. Dzięki temu agent "widzi" przeszkody w swoim otoczeniu bez znajomości pozycji absolutnej.

---

## Przestrzeń akcji

Ciągła (`spaces.Box`, `dtype=float32`), wektor 2 liczb:

| Indeks | Wartość | Zakres |
|--------|---------|--------|
| 0 | `fx` — siła w osi X | `[-1, 1]` |
| 1 | `fy` — siła w osi Y | `[-1, 1]` |

---

## Nagrody

| Zdarzenie | Nagroda |
|-----------|---------|
| Dotarcie do celu | `+10.0` |
| Każdy krok (przeżycie) | `-0.01` (kara za zwłokę, motywuje do szybkości) |
| Uderzenie w przeszkodę lub ścianę | `-0.1` |

---

## Warunki zakończenia epizodu

- **Sukces (`terminated=True`):** kulka dotrze do celu (środek kulki w promieniu `goal_radius` od celu)
- **Timeout (`truncated=True`):** przekroczenie maksymalnej liczby kroków (np. `max_steps=1000`)

Uderzenie w przeszkodę **nie kończy** epizodu — kulka się odbija i gra toczy się dalej.

---

## Tryb graficzny (pygame)

Renderowane elementy:
- Szare prostokąty — przeszkody
- Zielone kółko — cel
- Niebieskie kółko — kulka
- Czerwone linie wychodzące z kulki — promienie sensorów (opcjonalnie, do wizualizacji)
- Czarne tło, białe ściany graniczne

Metadane:
```python
metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}
```

---

## Planowany algorytm uczenia

**SAC (Soft Actor-Critic)** — dedykowany do ciągłych przestrzeni akcji, stabilny i próbkooszczędny.

Alternatywa: **PPO** z ciągłą głowicą (Gaussian policy) — prostszy w konfiguracji.

Biblioteka: `stable-baselines3`

---

## Struktura plików

```
Project4_Custom_Gymnasium_Env/
├── rolling_ball_env.py       # implementacja środowiska
├── train.ipynb               # notebook z treningiem agenta
├── environment_design.md     # ten plik
└── Projekt 4 Własne środowisko.pdf
```
