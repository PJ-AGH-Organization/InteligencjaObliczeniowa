# STRIPS i Planowanie w Sztucznej Inteligencji - Kompletny Przewodnik

## Spis treści
1. [Czym jest STRIPS?](#1-czym-jest-strips)
2. [Blocks World - klasyczny problem](#2-blocks-world---klasyczny-problem)
3. [Reprezentacja stanu w STRIPS](#3-reprezentacja-stanu-w-strips)
4. [Akcje w STRIPS - nie tylko "move from table"](#4-akcje-w-strips---nie-tylko-move-from-table)
5. [Przestrzeń stanów i graf przeszukiwania](#5-przestrzeń-stanów-i-graf-przeszukiwania)
6. [Czym są węzły? - kluczowe pojęcie](#6-czym-są-węzły---kluczowe-pojęcie)
7. [Algorytm A* i funkcja heurystyczna](#7-algorytm-a-i-funkcja-heurystyczna)
8. [Heurystyka goal_mismatch](#8-heurystyka-goal_mismatch)
9. [AIPython - biblioteka](#9-aipython---biblioteka)
10. [Twój kod - analiza](#10-twój-kod---analiza)
11. [Wyniki eksperymentów](#11-wyniki-eksperymentów)

---

## 1. Czym jest STRIPS?

**STRIPS** (Stanford Research Institute Problem Solver) to formalizm stworzony w 1971 roku przez Fikesa i Nilssona. Służy do reprezentowania **problemów planowania** - czyli znajdowania sekwencji działań prowadzących od stanu początkowego do stanu docelowego.

### Dlaczego STRIPS jest ważny?

STRIPS to fundament **automatycznego planowania** w AI. Używany jest w:
- Robotyce (planowanie ruchów robota)
- Grach komputerowych (AI przeciwników)
- Logistyce (planowanie tras, harmonogramów)
- Systemach wspomagania decyzji

### Podstawowa idea

```
┌─────────────────┐                              ┌─────────────────┐
│  STAN           │      sekwencja akcji         │  CEL            │
│  POCZĄTKOWY     │  =========================>  │  (stan          │
│                 │   akcja1, akcja2, akcja3...  │   docelowy)     │
└─────────────────┘                              └─────────────────┘
```

**Problem planowania** to pytanie: *"Jakie akcje wykonać, żeby przejść ze stanu początkowego do celu?"*

---

## 2. Blocks World - klasyczny problem

**Blocks World** (Świat Bloków) to kanoniczny problem w AI, używany do testowania algorytmów planowania od lat 70-tych.

### Zasady:

```
ŚWIAT BLOKÓW - ZASADY:
━━━━━━━━━━━━━━━━━━━━━━

1. Mamy bloki oznaczone literami (a, b, c, d, e...)
2. Bloki mogą leżeć na stole lub na innych blokach
3. Na jednym bloku może leżeć MAKSYMALNIE jeden inny blok
4. Robot może przenosić tylko JEDEN blok naraz
5. Robot może podnieść blok TYLKO jeśli jest "wolny" (nic na nim nie leży)
6. Robot może położyć blok TYLKO na wolne miejsce (stół lub wolny blok)
```

### Przykładowa sytuacja:

```
STAN POCZĄTKOWY:              CEL:

    [c]                          [a]
    [a]      [e]                 [b]
    [b]      [d]              [c][d][e]
━━━━━━━━━━━━━━━━━━━━━      ━━━━━━━━━━━━━━━━
      stół                       stół

Jak przenieść bloki ze stanu początkowego do celu?
```

### Dlaczego Blocks World jest trudny?

Mimo prostych zasad, problem jest **NP-trudny** do rozwiązania optymalnego:

| Liczba bloków | Przybliżona liczba stanów |
|---------------|---------------------------|
| 3             | ~13                       |
| 4             | ~73                       |
| 5             | ~501                      |
| 6             | ~4051                     |
| 10            | ~115 milionów             |

To zjawisko nazywamy **eksplozją kombinatoryczną**.

---

## 3. Reprezentacja stanu w STRIPS

### Stan to zbiór "cech" (features) z przypisanymi wartościami

W AIPython stan reprezentujemy jako **słownik** (dictionary):

```python
# Stan: blok 'a' na stole, 'b' na 'a', 'c' na 'b'
stan = {
    'a_is_on': 'table',    # a leży na stole
    'b_is_on': 'a',        # b leży na a
    'c_is_on': 'b',        # c leży na b
    'clear_a': False,      # a NIE jest wolne (b na nim leży)
    'clear_b': False,      # b NIE jest wolne (c na nim leży)
    'clear_c': True,       # c JEST wolne (nic na nim)
    'clear_table': True    # na stole zawsze można położyć
}
```

### Wizualizacja:

```
Stan słownikowy:                    Wizualnie:

a_is_on = 'table'                       [c]  <- clear_c = True
b_is_on = 'a'                           [b]  <- clear_b = False
c_is_on = 'b'                           [a]  <- clear_a = False
clear_a = False                     ━━━━━━━━━━
clear_b = False                        stół
clear_c = True
```

### Cel to CZĘŚCIOWY opis stanu

Cel nie musi określać wszystkich cech - tylko te, które nas interesują:

```python
# Cel: chcemy żeby 'a' było na 'b', a 'b' na 'c'
# (nie obchodzi nas gdzie jest reszta bloków)
cel = {
    'a_is_on': 'b',
    'b_is_on': 'c'
}
```

---

## 4. Akcje w STRIPS - nie tylko "move from table"

### Struktura akcji STRIPS

Każda akcja ma trzy elementy:

```
┌──────────────────────────────────────────────────────────────────┐
│  AKCJA: move_X_from_Y_to_Z                                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  WARUNKI WSTĘPNE (Preconditions):                               │
│  ─────────────────────────────────                              │
│  Co MUSI być prawdą, żeby akcja mogła być wykonana              │
│                                                                  │
│  EFEKTY (Effects):                                               │
│  ─────────────────                                              │
│  Co ZMIENIA SIĘ w stanie po wykonaniu akcji                     │
│                                                                  │
│  KOSZT:                                                          │
│  ──────                                                          │
│  Ile "kosztuje" wykonanie akcji (domyślnie 1)                   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### RÓŻNE TYPY AKCJI w Blocks World

W Blocks World mamy **różne typy** akcji, nie tylko "from table to block":

#### Typ 1: Z bloku na blok (move_X_from_BLOCK_to_BLOCK)

```python
# Przenieś blok 'a' z bloku 'b' na blok 'c'
akcja_move_a_from_b_to_c = Strips(
    name='move_a_from_b_to_c',
    preconds={
        'a_is_on': 'b',      # a musi być na b
        'clear_a': True,     # a musi być wolne (można podnieść)
        'clear_c': True      # c musi być wolne (można położyć)
    },
    effects={
        'a_is_on': 'c',      # teraz a jest na c
        'clear_b': True,     # b jest teraz wolne
        'clear_c': False     # c nie jest już wolne
    }
)
```

```
PRZED:                      PO:

   [a]                            [a]
   [b]      [c]              [b]  [c]
━━━━━━━━━━━━━━━━━━      ━━━━━━━━━━━━━━━━
```

#### Typ 2: Ze stołu na blok (move_X_from_table_to_BLOCK)

```python
# Przenieś blok 'a' ze stołu na blok 'b'
akcja_move_a_from_table_to_b = Strips(
    name='move_a_from_table_to_b',
    preconds={
        'a_is_on': 'table',  # a musi być na stole
        'clear_a': True,     # a musi być wolne
        'clear_b': True      # b musi być wolne
    },
    effects={
        'a_is_on': 'b',      # teraz a jest na b
        'clear_table': True, # stół zawsze wolny
        'clear_b': False     # b nie jest już wolne
    }
)
```

```
PRZED:                      PO:

                                 [a]
   [a]      [b]                  [b]
━━━━━━━━━━━━━━━━━━      ━━━━━━━━━━━━━━━━
```

#### Typ 3: Z bloku na stół (move_X_from_BLOCK_to_table)

```python
# Przenieś blok 'a' z bloku 'b' na stół
akcja_move_a_from_b_to_table = Strips(
    name='move_a_from_b_to_table',
    preconds={
        'a_is_on': 'b',      # a musi być na b
        'clear_a': True      # a musi być wolne
        # NIE sprawdzamy clear_table - stół ma nieskończoną pojemność
    },
    effects={
        'a_is_on': 'table',  # teraz a jest na stole
        'clear_b': True      # b jest teraz wolne
    }
)
```

```
PRZED:                      PO:

   [a]
   [b]                       [a]  [b]
━━━━━━━━━━━━━━━━━━      ━━━━━━━━━━━━━━━━
```

### Ile akcji dla 5 bloków?

Dla 5 bloków (a, b, c, d, e) mamy:
- Każdy blok może być przeniesiony na: stół + 4 inne bloki = 5 miejsc docelowych
- Każdy blok może być przeniesiony Z: stołu + 4 innych bloków = 5 miejsc źródłowych

Ale nie wszystkie kombinacje są sensowne (np. move_a_from_a_to_a), więc:
- **5 bloków × 5 źródeł × 5 celów - nieprawidłowe = około 80 unikalnych akcji**

---

## 5. Przestrzeń stanów i graf przeszukiwania

### Przestrzeń stanów

**Przestrzeń stanów** to zbiór WSZYSTKICH możliwych konfiguracji świata bloków.

```
                    ┌─────────────────────────────────────┐
                    │     PRZESTRZEŃ STANÓW               │
                    │     (dla 5 bloków: ~500 stanów)     │
                    │                                     │
                    │   ●───●───●───●                     │
                    │   │   │   │   │                     │
                    │   ●───●───●───●───●                 │
                    │       │   │   │   │                 │
    START ──────────│──→ ★  │   ●   │   ●                 │
                    │       │       │                     │
                    │   ●───●───●───●───●                 │
                    │           │   │                     │
                    │       ●───●───◆ ←──────────── CEL   │
                    │                                     │
                    └─────────────────────────────────────┘

    ● = stan (konfiguracja bloków)
    ─ = możliwe przejście (akcja)
    ★ = stan początkowy
    ◆ = stan docelowy
```

### Graf przeszukiwania

Algorytm przeszukiwania buduje **graf** (lub drzewo) reprezentujące eksplorowane stany:

```
                         [Stan początkowy]
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
         [Stan A]         [Stan B]         [Stan C]
         (po akcji1)      (po akcji2)      (po akcji3)
              │                │                │
         ┌────┴────┐      ┌────┴────┐          ...
         ▼         ▼      ▼         ▼
      [Stan D]  [Stan E] [Stan F] [Stan G]
         │
         ▼
      [CEL!]
```

---

## 6. Czym są węzły? - kluczowe pojęcie

### Węzeł (Node) w przeszukiwaniu

**Węzeł** to struktura danych reprezentująca:
1. Konkretny **stan** świata
2. **Ścieżkę** od stanu początkowego do tego stanu
3. **Koszt** dotarcia do tego stanu
4. (opcjonalnie) **Wartość heurystyki** dla tego stanu

```
┌─────────────────────────────────────────────────────────────────┐
│  WĘZEŁ (Node)                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  stan = {                           Aktualny stan świata        │
│      'a_is_on': 'b',                                            │
│      'b_is_on': 'table',                                        │
│      'clear_a': True,                                           │
│      'clear_b': False,                                          │
│      ...                                                        │
│  }                                                              │
│                                                                 │
│  ścieżka = [                        Jak tu dotarliśmy           │
│      'move_c_from_a_to_table',                                  │
│      'move_b_from_table_to_c'                                   │
│  ]                                                              │
│                                                                 │
│  g = 2                              Koszt dotarcia (2 akcje)    │
│                                                                 │
│  h = 3                              Heurystyka (oszacowanie     │
│                                     ile jeszcze do celu)        │
│                                                                 │
│  f = g + h = 5                      Całkowita ocena węzła       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### "Rozwinięcie" węzła (Node Expansion)

**Rozwinięcie węzła** oznacza:
1. Wzięcie węzła z kolejki
2. Wygenerowanie WSZYSTKICH możliwych stanów-następników (przez zastosowanie wszystkich możliwych akcji)
3. Utworzenie nowych węzłów dla tych stanów
4. Dodanie nowych węzłów do kolejki

```
    Rozwijamy węzeł ze stanem S:

                    [S]
                     │
        ─────────────┼─────────────────
        │            │            │            │
        ▼            ▼            ▼            ▼
    [S + akcja1] [S + akcja2] [S + akcja3] [S + akcja4]

    Jeśli w stanie S jest 4 możliwych akcji,
    rozwinięcie tego węzła tworzy 4 nowe węzły.
```

### Frontier (Granica) vs Expanded (Rozwinięte)

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  EXPANDED (rozwinięte):     Węzły, które już przeanalizowaliśmy │
│  ═══════════════════════    i wygenerowaliśmy ich następników   │
│                                                                 │
│  FRONTIER (granica):        Węzły w kolejce, czekające na       │
│  ═══════════════════════    rozwinięcie                         │
│                                                                 │
│                                                                 │
│        ┌──────────────────────────────────────┐                 │
│        │         EXPANDED                      │                 │
│        │    ●─────●─────●                      │                 │
│        │    │     │     │                      │                 │
│        │    ●─────●─────●─────○  ○  ○          │                 │
│        │          │     │     │  │  │          │                 │
│        │          ●─────●     ○  ○  ○          │                 │
│        │                      ↑                │                 │
│        │                  FRONTIER             │                 │
│        └──────────────────────────────────────┘                 │
│                                                                 │
│   ● = expanded (rozwinięty)                                     │
│   ○ = frontier (w kolejce)                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Co oznacza "323 paths expanded"?

Gdy widzisz w wynikach:
```
323 paths have been expanded and 821 paths remain in the frontier
```

To oznacza:
- **323 węzły zostały rozwinięte** - algorytm przeanalizował 323 różne stany
- **821 węzłów czeka w kolejce** - są w "frontier", jeszcze nierozwinięte
- Algorytm musiał "odwiedzić" 323 stany, zanim znalazł rozwiązanie

**Im więcej węzłów rozwinięto, tym dłużej trwało szukanie.**

---

## 7. Algorytm A* i funkcja heurystyczna

### Przeszukiwanie ślepe vs informowane

```
PRZESZUKIWANIE ŚLEPE (Blind Search):
════════════════════════════════════
- Nie wie, który kierunek jest "lepszy"
- Rozwija węzły w kolejności: BFS (wszerz), DFS (w głąb), lub UCS (najtańszy)
- Może rozwinąć OGROMNĄ liczbę węzłów


PRZESZUKIWANIE INFORMOWANE (Informed Search):
═════════════════════════════════════════════
- Używa HEURYSTYKI - "inteligentnego zgadywania"
- Preferuje węzły, które wyglądają na bliższe celu
- Rozwija DUŻO MNIEJ węzłów
```

### Algorytm A*

**A*** to najpopularniejszy algorytm przeszukiwania informowanego.

Używa funkcji oceny: **f(n) = g(n) + h(n)**

```
f(n) = g(n) + h(n)

gdzie:
  f(n) = całkowita ocena węzła (im mniejsza, tym lepiej)
  g(n) = RZECZYWISTY koszt dotarcia od startu do węzła n
  h(n) = OSZACOWANY koszt od węzła n do celu (HEURYSTYKA)
```

### Jak A* wybiera węzły do rozwinięcia?

```
KOLEJKA PRIORYTETOWA (posortowana po f):
══════════════════════════════════════════

┌────────────────────────────────────────────────────┐
│  Węzeł A: g=2, h=3, f=5                            │  ← NAJLEPSZY (f=5)
│  Węzeł B: g=1, h=5, f=6                            │
│  Węzeł C: g=4, h=3, f=7                            │
│  Węzeł D: g=3, h=5, f=8                            │
│  ...                                               │
└────────────────────────────────────────────────────┘

A* zawsze rozwija węzeł z NAJMNIEJSZYM f.
W tym przypadku: Węzeł A (f=5)
```

### Dlaczego heurystyka musi być DOPUSZCZALNA?

**Heurystyka dopuszczalna (admissible)**: nigdy nie przeszacowuje kosztu do celu.

```
Dla każdego węzła n:    h(n) ≤ rzeczywisty_koszt(n → cel)
```

**Jeśli h jest dopuszczalna, A* GWARANTUJE znalezienie optymalnego rozwiązania!**

```
PRZYKŁAD:

    n ────────────────────────────→ CEL

    rzeczywisty koszt = 5 akcji

    Dopuszczalna heurystyka:
    h(n) = 3  ✓  (3 ≤ 5, nie przeszacowuje)
    h(n) = 5  ✓  (5 ≤ 5, idealna!)
    h(n) = 7  ✗  (7 > 5, PRZESZACOWUJE - niedopuszczalna!)
```

---

## 8. Heurystyka goal_mismatch

### Definicja

```python
def goal_mismatch_heur(state, goal):
    """Zlicza ile celów nie jest jeszcze spełnionych."""
    return sum(1 for feat, val in goal.items() if state.get(feat) != val)
```

### Jak działa?

```
PRZYKŁAD:

Stan aktualny:                    Cel:
  a_is_on = 'table'                 a_is_on = 'b'     ← NIESPEŁNIONY! (+1)
  b_is_on = 'c'                     b_is_on = 'c'     ← spełniony
  c_is_on = 'table'                 d_is_on = 'e'     ← NIESPEŁNIONY! (+1)
  d_is_on = 'table'
  e_is_on = 'table'

Heurystyka: h = 2 (dwa cele niespełnione)
```

### Dlaczego jest DOPUSZCZALNA?

```
DOWÓD DOPUSZCZALNOŚCI:
══════════════════════

1. Każdy niespełniony cel wymaga CO NAJMNIEJ jednej akcji do spełnienia
   (nie da się "magicznie" zmienić pozycji bloku)

2. Więc jeśli mamy k niespełnionych celów:
   - h(n) = k
   - rzeczywisty koszt ≥ k

3. Zatem: h(n) ≤ rzeczywisty koszt  ✓

WNIOSEK: goal_mismatch jest dopuszczalna!
```

### Przykład działania

```
Stan: a na stole, b na stole, c na stole
Cel:  a na b, b na c

Niespełnione cele:
  - a_is_on = 'b' (mamy 'table') → +1
  - b_is_on = 'c' (mamy 'table') → +1

h = 2

Rzeczywiste rozwiązanie:
  1. move_b_from_table_to_c
  2. move_a_from_table_to_b

Rzeczywisty koszt = 2

h = 2 ≤ 2 = rzeczywisty koszt  ✓  DOPUSZCZALNA!
```

---

## 9. AIPython - biblioteka

### Co to jest AIPython?

**AIPython** to edukacyjna biblioteka Pythona towarzysząca podręcznikowi:
*"Artificial Intelligence: Foundations of Computational Agents"* (Poole & Mackworth)

Dostępna na: https://aipython.org

### Struktura plików STRIPS w AIPython

```
aipython/
├── stripsProblem.py          # Klasy: Strips, STRIPS_domain, Planning_problem
├── stripsForwardPlanner.py   # Forward planning - przeszukiwanie "do przodu"
├── stripsRegressionPlanner.py # Regression planning - przeszukiwanie "od celu"
├── stripsHeuristic.py        # Przykładowe heurystyki
├── stripsCSPPlanner.py       # Planer oparty na CSP
├── stripsPOP.py              # Partial Order Planning
├── searchProblem.py          # Abstrakcyjna klasa problemu przeszukiwania
├── searchMPP.py              # A* z Multiple Path Pruning
└── searchGeneric.py          # Bazowe algorytmy przeszukiwania
```

### Kluczowe klasy

#### Strips - pojedyncza akcja

```python
from stripsProblem import Strips

akcja = Strips(
    name='move_a_from_table_to_b',
    preconds={'a_is_on': 'table', 'clear_a': True, 'clear_b': True},
    effects={'a_is_on': 'b', 'clear_b': False},
    cost=1
)
```

#### STRIPS_domain - dziedzina (zbiór akcji)

```python
from stripsProblem import STRIPS_domain

domain = STRIPS_domain(
    feature_domain_dict={
        'a_is_on': {'table', 'b', 'c'},
        'b_is_on': {'table', 'a', 'c'},
        'clear_a': {True, False},
        'clear_b': {True, False},
        ...
    },
    actions={akcja1, akcja2, akcja3, ...}
)
```

#### Planning_problem - konkretny problem

```python
from stripsProblem import Planning_problem

problem = Planning_problem(
    prob_domain=domain,
    initial_state={'a_is_on': 'table', 'b_is_on': 'a', ...},
    goal={'a_is_on': 'b', 'b_is_on': 'c'}
)
```

#### Forward_STRIPS - planer forward

```python
from stripsForwardPlanner import Forward_STRIPS
from searchMPP import SearcherMPP

planer = Forward_STRIPS(problem, heur=moja_heurystyka)
searcher = SearcherMPP(planer)
rozwiazanie = searcher.search()
```

---

## 10. Twój kod - analiza

### Struktura projektu

```
Project2/blocksworld5_4_points/
├── __init__.py       # Pusty, oznacza pakiet Python
├── __main__.py       # Punkt wejścia (python -m ...)
├── problems.py       # Definicje 3 problemów Blocks World
├── solve.py          # Funkcje rozwiązujące z A*
├── heuristics.py     # Heurystyka goal_mismatch
├── viz.py            # Wizualizacja rozwiązań (PNG/PDF)
└── outputs/          # Wyniki (obrazki)
```

### problems.py - definicja problemów

```python
# Tworzy dziedzinę Blocks World z 5 blokami
domain = make_domain()  # generuje ~80 akcji move

# Tworzy 3 problemy o różnej trudności
problems = make_problems(domain)
# - problem1: ~522 stanów, rozwiązanie w 4 akcjach
# - problem2: ~555 stanów, rozwiązanie w 6 akcji
# - problem3: ~506 stanów, rozwiązanie w 4 akcjach
```

### solve.py - rozwiązywanie

```python
def solve_forward(problem, heur=None, timeout=300):
    """
    Rozwiązuje problem używając Forward Planning z A*.

    - problem: Planning_problem z AIPython
    - heur: funkcja heurystyczna (lub None dla h=0)
    - timeout: limit czasu w sekundach

    Zwraca: SolveResult z planem, kosztem, czasem, liczbą rozwiniętych węzłów
    """
```

### heuristics.py - heurystyka

```python
def goal_mismatch_heur(state, goal):
    """Zlicza ile celów nie jest jeszcze spełnionych."""
    return float(sum(1 for feat, val in goal.items() if state.get(feat) != val))
```

---

## 11. Wyniki eksperymentów

### Porównanie: bez heurystyki vs z heurystyką

```
┌──────────┬─────────────────────┬─────────────────────┬───────────┐
│ Problem  │ BEZ heurystyki      │ Z goal_mismatch     │ Redukcja  │
│          │ (h=0, ślepe)        │ (h=niespełnione)    │           │
├──────────┼─────────────────────┼─────────────────────┼───────────┤
│          │                     │                     │           │
│ problem1 │ 177-323 węzłów      │ 7 węzłów            │ ~46x      │
│ (4 akcje)│ ~0.03-0.07s         │ ~0.0005s            │ ~100x     │
│          │                     │                     │           │
├──────────┼─────────────────────┼─────────────────────┼───────────┤
│          │                     │                     │           │
│ problem2 │ 192-273 węzłów      │ 8 węzłów            │ ~25x      │
│ (6 akcji)│ ~0.04-0.06s         │ ~0.0005s            │ ~50x      │
│          │                     │                     │           │
├──────────┼─────────────────────┼─────────────────────┼───────────┤
│          │                     │                     │           │
│ problem3 │ 302-381 węzłów      │ 6 węzłów            │ ~50x      │
│ (4 akcje)│ ~0.06-0.08s         │ ~0.0004s            │ ~150x     │
│          │                     │                     │           │
└──────────┴─────────────────────┴─────────────────────┴───────────┘
```

### Wizualizacja różnicy

```
BEZ HEURYSTYKI (przeszukiwanie ślepe):

    START
      │
      ├──┬──┬──┬──┬──┐
      │  │  │  │  │  │
      ○  ○  ○  ○  ○  ○       ← rozwija WSZYSTKIE kierunki
         │  │  │  │  │
      ○──○──○──○──○──○──○
            │  │  │
         ○──○──○──○──○
               │
            ──CEL──

    Rozwinięto: ~300 węzłów


Z HEURYSTYKĄ goal_mismatch:

    START
      │
      ○                      ← rozwija tylko OBIECUJĄCE kierunki
      │
      ○
      │
      ○
      │
      ○
      │
    ──CEL──

    Rozwinięto: ~7 węzłów
```

### Wnioski

1. **Heurystyka dramatycznie redukuje liczbę rozwijanych węzłów** (25-50x mniej)
2. **Przyspieszenie czasowe jest jeszcze większe** (50-150x szybciej)
3. **Oba podejścia znajdują OPTYMALNE rozwiązanie** (ten sam koszt)
4. **goal_mismatch jest prosta ale skuteczna** - wystarczy dla Blocks World

---

## Podsumowanie wymagań na 4 punkty

| Wymaganie | Status | Szczegóły |
|-----------|--------|-----------|
| Dziedzina STRIPS | ✓ | Blocks World 5 bloków |
| 3 problemy | ✓ | problem1, problem2, problem3 |
| ≥50 stanów każdy | ✓ | 522, 555, 506 stanów |
| Plan ≥4 akcji | ✓ | 4, 6, 4 akcji |
| Forward planning | ✓ | Forward_STRIPS + SearcherMPP |
| Heurystyka | ✓ | goal_mismatch_heur |
| Opis heurystyki | ✓ | Ten dokument + komentarze |
| Wyniki z/bez | ✓ | 25-50x redukcja węzłów |

---

## Jak uruchomić kod?

```bash
# Z katalogu głównego repozytorium:

# Rozwiąż wszystkie problemy z heurystyką i wizualizacją:
python -m Project2.blocksworld5_4_points --viz

# Rozwiąż problem2 bez heurystyki:
python -m Project2.blocksworld5_4_points --problem problem2 --heur zero

# Rozwiąż problem1 z heurystyką:
python -m Project2.blocksworld5_4_points --problem problem1 --heur mismatch --viz
```

Wyniki wizualizacji trafiają do `Project2/blocksworld5_4_points/outputs/`.
