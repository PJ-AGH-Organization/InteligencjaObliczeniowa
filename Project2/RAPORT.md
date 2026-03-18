# Raport: Planowanie STRIPS - Blocks World

**Autor:** [Imię Nazwisko]
**Data:** [Data]
**Przedmiot:** Inteligencja Obliczeniowa

---

## 1. Wstęp

### 1.1 Cel projektu

Celem projektu jest implementacja i analiza algorytmu planowania STRIPS (Stanford Research Institute Problem Solver) na przykładzie problemu Blocks World. Projekt obejmuje:

- Zdefiniowanie problemów planistycznych w formalizmie STRIPS
- Implementację heurystyki przyspieszającej przeszukiwanie
- Porównanie efektywności algorytmu z heurystyką i bez niej
- Analizę dekompozycji celów na podcele (subgoals)

### 1.2 STRIPS - podstawy teoretyczne

STRIPS to formalizm reprezentacji problemów planistycznych, gdzie:

- **Stan** to zbiór formuł atomowych (faktów) opisujących świat
- **Akcja** definiowana jest przez:
  - *Warunki wstępne (preconditions)* - co musi być prawdą, aby wykonać akcję
  - *Efekty (effects)* - jak akcja zmienia stan świata (add/delete lists)
- **Problem planistyczny** to trójka: (stan początkowy, cel, dostępne akcje)
- **Plan** to sekwencja akcji prowadząca od stanu początkowego do stanu spełniającego cel

### 1.3 Blocks World

Blocks World to klasyczny problem planistyczny, gdzie:

- Mamy zbiór klocków, które można układać w stosy
- Klocki można przenosić tylko gdy są "wolne" (nic na nich nie leży)
- Można przenosić klocek na inny wolny klocek lub na stół
- Stół ma nieograniczoną pojemność

**Reprezentacja stanu:**
- `on(X) = Y` - klocek X leży na Y (Y może być innym klockiem lub "table")
- `clear(X) = True/False` - czy klocek X jest wolny (nic na nim nie leży)

**Akcje:**
- `move_X_from_Y_to_Z` - przenieś klocek X z Y na Z
  - Warunki: `on(X) = Y`, `clear(X) = True`, `clear(Z) = True` (jeśli Z nie jest stołem)
  - Efekty: `on(X) = Z`, `clear(Y) = True`, `clear(Z) = False` (jeśli Z nie jest stołem)

---

## 2. Heurystyka Goal Mismatch

### 2.1 Definicja

Heurystyka **goal mismatch** (niedopasowanie celu) liczy ile warunków celu nie jest jeszcze spełnionych w bieżącym stanie:

```
h(state, goal) = |{(feature, value) ∈ goal : state[feature] ≠ value}|
```

W implementacji:
```python
def goal_mismatch_heur(state: StateAssignment, goal: Goal) -> float:
    return float(sum(1 for feat, val in goal.items() if state.get(feat) != val))
```

### 2.2 Uzasadnienie dopuszczalności

Heurystyka jest **dopuszczalna** (admissible), ponieważ:

1. Każdy niespełniony warunek celu wymaga **co najmniej jednej** akcji do osiągnięcia
2. Heurystyka zwraca liczbę niespełnionych warunków
3. Prawdziwy koszt osiągnięcia celu jest **co najmniej równy** tej liczbie (a zazwyczaj większy, bo jedna akcja może nie naprawić wszystkich warunków)

**Dowód:**
- Niech `k` = liczba niespełnionych warunków celu
- Każda akcja może zmienić co najwyżej jeden warunek `on(X)` na właściwą wartość
- Zatem potrzeba co najmniej `k` akcji → `h(s) ≤ h*(s)` (koszt rzeczywisty)

### 2.3 Wpływ na przeszukiwanie A*

Algorytm A* z dopuszczalną heurystyką gwarantuje znalezienie optymalnego rozwiązania. Heurystyka goal mismatch:

- **Przyspiesza** przeszukiwanie, kierując je ku stanom bliższym celowi
- **Redukuje** liczbę rozwijanych węzłów w porównaniu do przeszukiwania bez heurystyki (h=0)
- Jest prosta obliczeniowo (O(|goal|) na ewaluację)

---

## 3. Opis problemów testowych

### 3.1 Problemy małe (5 klocków) - wymagania 4-6 punktów

| Problem | Stan początkowy | Cel | Opis |
|---------|-----------------|-----|------|
| problem1 | `c` na `a`, `e` na `d`, reszta na stole | `a→b→c`, `e` na stole | Przebudowa dwóch małych wież |
| problem2 | Wieża `a→b→c→d→e` | `e→d→c`, `a→b` | Rozkład i częściowe odwrócenie wieży |
| problem3 | `c` na `a`, reszta na stole | `a→b→c`, `d→e` | Budowa dwóch wież |

**Wizualizacja problem1:**
```
Stan początkowy:          Cel:
    [c]                   [a]
    [a]  [e]              [b]
   ─────[d]────          ─[c]─ [e] [d]
```

<!-- TODO: Dodaj analogiczne wizualizacje dla problem2 i problem3 -->

### 3.2 Problemy duże (12 klocków) - wymagania 8 punktów

| Problem | Stan początkowy | Cel | Opis |
|---------|-----------------|-----|------|
| problem4 | Dwie wieże 6-klockowe | Jedna wieża 12-klockowa | Połączenie wież |
| problem5 | Wieża 12-klockowa a→...→l | Odwrócona wieża l→...→a | Pełne odwrócenie |
| problem6 | Dwie wieże 6-klockowe | Odwrócona wieża 12-klockowa | Połączenie i odwrócenie |

---

## 4. Wyniki eksperymentów

### 4.1 Problemy małe - tryb standardowy (4 punkty)

#### Heurystyka mismatch

| Problem | Stany osiągalne | Rozwiązany | Koszt (akcje) | Węzły rozwinięte | Czas [s] |
|---------|-----------------|------------|---------------|------------------|----------|
| problem1 | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |
| problem2 | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |
| problem3 | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |

#### Bez heurystyki (zero)

| Problem | Stany osiągalne | Rozwiązany | Koszt (akcje) | Węzły rozwinięte | Czas [s] |
|---------|-----------------|------------|---------------|------------------|----------|
| problem1 | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |
| problem2 | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |
| problem3 | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |

#### Porównanie - redukcja węzłów dzięki heurystyce

| Problem | Węzły (zero) | Węzły (mismatch) | Redukcja |
|---------|--------------|------------------|----------|
| problem1 | <!-- TODO --> | <!-- TODO --> | <!-- TODO -->% |
| problem2 | <!-- TODO --> | <!-- TODO --> | <!-- TODO -->% |
| problem3 | <!-- TODO --> | <!-- TODO --> | <!-- TODO -->% |

### 4.2 Problemy małe - tryb z subgoals (6 punktów)

#### Heurystyka mismatch + subgoals

| Problem | Liczba subgoals | Koszt całkowity | Węzły rozwinięte | Czas [s] |
|---------|-----------------|-----------------|------------------|----------|
| problem1 | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |
| problem2 | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |
| problem3 | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |

**Rozbicie na subgoals (przykład dla problem1):**

| Subgoal | Opis | Koszt | Węzły | Akcje |
|---------|------|-------|-------|-------|
| 1 | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |
| 2 | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |
| 3 | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |

#### Porównanie: standardowy vs subgoals

| Problem | Węzły (standard) | Węzły (subgoals) | Koszt (standard) | Koszt (subgoals) |
|---------|------------------|------------------|------------------|------------------|
| problem1 | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |
| problem2 | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |
| problem3 | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |

### 4.3 Problemy duże - tryb z subgoals (8 punktów)

#### Heurystyka mismatch + subgoals

| Problem | Liczba subgoals | Koszt całkowity | Węzły rozwinięte | Czas [s] |
|---------|-----------------|-----------------|------------------|----------|
| problem4 | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |
| problem5 | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |
| problem6 | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |

#### Bez heurystyki (zero) + subgoals

| Problem | Liczba subgoals | Koszt całkowity | Węzły rozwinięte | Czas [s] |
|---------|-----------------|-----------------|------------------|----------|
| problem4 | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |
| problem5 | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |
| problem6 | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> | <!-- TODO --> |

---

## 5. Plany rozwiązań

### 5.1 Problem 1

**Konfiguracja:** <!-- TODO: mismatch/zero, standard/subgoals -->

```
<!-- TODO: Wklej plan z results.json -->
1. move_...
2. move_...
...
```

### 5.2 Problem 2

**Konfiguracja:** <!-- TODO -->

```
<!-- TODO: Wklej plan -->
```

### 5.3 Problem 3

**Konfiguracja:** <!-- TODO -->

```
<!-- TODO: Wklej plan -->
```

### 5.4 Problem 4 (duży)

**Konfiguracja:** <!-- TODO -->

```
<!-- TODO: Wklej plan (>= 20 akcji) -->
```

### 5.5 Problem 5 (duży)

**Konfiguracja:** <!-- TODO -->

```
<!-- TODO: Wklej plan -->
```

### 5.6 Problem 6 (duży)

**Konfiguracja:** <!-- TODO -->

```
<!-- TODO: Wklej plan -->
```

---

## 6. Wizualizacje

Wizualizacje kroków rozwiązań znajdują się w katalogu `outputs/`:

- `outputs/problemX/mismatch/` - rozwiązania z heurystyką
- `outputs/problemX/zero/` - rozwiązania bez heurystyki
- `outputs/problemX/subgoals_mismatch/` - rozwiązania z subgoals i heurystyką
- `outputs/problemX/subgoals_zero/` - rozwiązania z subgoals bez heurystyki

Każdy katalog zawiera:
- `step_XXX.png` - wizualizacja stanu po każdej akcji
- `solution_path.pdf` - wszystkie kroki w jednym PDF
- `results.json` - szczegółowe wyniki (koszt, czas, plan)

<!-- TODO: Wstaw wybrane wizualizacje lub odwołania do plików -->

---

## 7. Analiza i wnioski

### 7.1 Wpływ heurystyki na efektywność

<!-- TODO: Uzupełnij na podstawie wyników -->

**Obserwacje:**
- Heurystyka mismatch zredukowała liczbę rozwijanych węzłów o średnio <!-- TODO -->%
- Największa redukcja wystąpiła dla problemu <!-- TODO --> (<!-- TODO -->%)
- Czas wykonania zmniejszył się <!-- TODO -->-krotnie

**Wnioski:**
- <!-- TODO -->

### 7.2 Dekompozycja na subgoals

<!-- TODO: Uzupełnij na podstawie wyników -->

**Obserwacje:**
- Podział na subgoals <!-- zmniejszył/zwiększył --> liczbę rozwijanych węzłów
- Koszt rozwiązania z subgoals był <!-- optymalny/nieoptymalny --> w porównaniu do rozwiązania bez podziału
- Dla dużych problemów subgoals były <!-- niezbędne/pomocne --> ze względu na <!-- TODO -->

**Wnioski:**
- <!-- TODO -->

### 7.3 Skalowalność

<!-- TODO: Uzupełnij na podstawie wyników dla problemów dużych -->

**Obserwacje:**
- Dla 12 klocków przestrzeń stanów wynosi <!-- TODO --> (szacunkowo)
- Bez subgoals rozwiązanie problemów dużych <!-- było możliwe/nie było możliwe w rozsądnym czasie -->
- Z subgoals problemy duże rozwiązywane są w czasie <!-- TODO -->s

**Wnioski:**
- <!-- TODO -->

### 7.4 Optymalność rozwiązań

**Obserwacje:**
- Algorytm A* z heurystyką mismatch zawsze znajduje rozwiązanie optymalne (heurystyka dopuszczalna)
- Dekompozycja na subgoals <!-- gwarantuje/nie gwarantuje --> optymalność globalną
- <!-- TODO: porównaj koszty standard vs subgoals -->

---

## 8. Podsumowanie

<!-- TODO: Napisz podsumowanie projektu -->

Projekt zrealizował następujące cele:
- [x] Zdefiniowano 3 problemy małe (5 klocków) z >= 50 stanami osiągalnymi
- [x] Zdefiniowano 3 problemy duże (12 klocków) z rozwiązaniami >= 20 akcji
- [x] Zaimplementowano heurystykę goal mismatch (dopuszczalna)
- [x] Porównano efektywność z heurystyką i bez niej
- [x] Zaimplementowano dekompozycję celów na subgoals
- [x] Wygenerowano wizualizacje rozwiązań

**Kluczowe wnioski:**
1. <!-- TODO -->
2. <!-- TODO -->
3. <!-- TODO -->

---

## Załączniki

### A. Komendy do uruchomienia eksperymentów

```bash
# Małe problemy - standardowy tryb
uv run python -m Project2.blocksworld5_4_points --heur=mismatch --viz
uv run python -m Project2.blocksworld5_4_points --heur=zero --viz

# Małe problemy - z subgoals
uv run python -m Project2.blocksworld5_4_points --subgoals --heur=mismatch --viz
uv run python -m Project2.blocksworld5_4_points --subgoals --heur=zero --viz

# Duże problemy - z subgoals
uv run python -m Project2.blocksworld5_4_points --large --subgoals --heur=mismatch --viz
uv run python -m Project2.blocksworld5_4_points --large --subgoals --heur=zero --viz
```

### B. Struktura plików wynikowych

```
Project2/blocksworld5_4_points/outputs/
├── problem1/
│   ├── mismatch/
│   │   ├── results.json
│   │   ├── step_000.png ... step_XXX.png
│   │   └── solution_path.pdf
│   ├── zero/
│   ├── subgoals_mismatch/
│   └── subgoals_zero/
├── problem2/
│   └── ...
├── problem3/
│   └── ...
├── problem4/  (duże)
│   └── ...
├── problem5/
│   └── ...
└── problem6/
    └── ...
```

### C. Format results.json

```json
{
  "problem": "problem1",
  "mode": "standard|subgoals",
  "heuristic": "mismatch|zero",
  "reachable_states": 522,
  "solved": true,
  "cost": 4,
  "expanded": 6,
  "time_seconds": 0.001,
  "plan": ["move_X_from_Y_to_Z", ...]
}
```
