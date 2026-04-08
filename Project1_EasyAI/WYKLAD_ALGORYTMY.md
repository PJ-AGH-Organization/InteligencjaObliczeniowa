# Algorytmy przeszukiwania drzew gier -- kompletny wykład

> Opracowanie na podstawie projektu **Tic-tac-doh** (Inteligencja Obliczeniowa, Semestr 6).
> Wszystkie przykłady odnoszą się bezpośrednio do kodu w `Project1/`.

---

## Spis treści

1. [Gry dwuosobowe i dlaczego AI umie w nie grać](#1-gry-dwuosobowe)
2. [Drzewo gry -- fundament wszystkiego](#2-drzewo-gry)
3. [Wartości w drzewie gry -- funkcja oceny (scoring)](#3-funkcja-oceny)
4. [Algorytm Minimax -- "zakładam, że przeciwnik gra optymalnie"](#4-minimax)
5. [Negamax -- elegancka wersja Minimaxa](#5-negamax)
6. [Ograniczenie głębokości -- dlaczego nie przeszukujemy całego drzewa](#6-ograniczenie-glebokosci)
7. [Odcięcie alfa-beta -- pomijamy to, co nie ma sensu](#7-alfa-beta)
8. [SSS* -- przeszukiwanie best-first](#8-sss)
9. [Gry z losowością -- węzły szansy (chance nodes)](#9-wezly-szansy)
10. [Expecti-Minimax -- Minimax dla gier losowych](#10-expectiminimax)
11. [Star1 Pruning -- odcięcie alfa-beta dla węzłów szansy](#11-star1)
12. [Podsumowanie -- porównanie wszystkich algorytmów](#12-podsumowanie)
13. [Słownik pojęć](#13-slownik)

---

<a id="1-gry-dwuosobowe"></a>
## 1. Gry dwuosobowe i dlaczego AI umie w nie grać

### Czym jest gra dwuosobowa z pełną informacją?

Gra dwuosobowa z pełną informacją to taka, w której:

- Jest **dwóch graczy**, którzy wykonują ruchy **na zmianę**
- Obaj gracze **widzą cały stan gry** (w przeciwieństwie np. do pokera, gdzie karty są ukryte)
- Gra jest **deterministyczna** (w wersji podstawowej -- bez losowości)
- Gra **kiedyś się kończy** (jest skończona)

Przykłady: szachy, warcaby, Go, kółko i krzyżyk, Tic-tac-doh (z modyfikacją losową).

### Kluczowa obserwacja

Skoro obaj gracze widzą wszystko i gra jest skończona, to **teoretycznie istnieje strategia optymalna** -- ciąg ruchów, który gwarantuje najlepszy możliwy wynik niezależnie od tego, co zrobi przeciwnik. Problem polega na tym, żeby tę strategię **znaleźć**.

I właśnie do tego służy **drzewo gry**.

---

<a id="2-drzewo-gry"></a>
## 2. Drzewo gry -- fundament wszystkiego

### Definicja

**Drzewo gry** (ang. *game tree*) to struktura danych w kształcie drzewa, która reprezentuje **wszystkie możliwe przebiegi gry** od danego stanu początkowego.

- **Korzeń** (root) = aktualny stan gry (np. pusta plansza)
- **Węzeł** (node) = konkretny stan planszy w pewnym momencie gry
- **Krawędź** (edge) = ruch, który prowadzi z jednego stanu do drugiego
- **Liść** (leaf) = stan końcowy gry (wygrana, przegrana lub remis)
- **Głębokość** (depth) = ile ruchów w przód "patrzymy" od korzenia

### Przykład: Tic-tac-doh na początku gry

Wyobraź sobie pustą planszę 3x3. Gracz O (gracz 1) zaczyna.

```
Poziom 0 (korzeń):        . . .
                           . . .       <- pusta plansza
                           . . .

Ma 9 możliwych ruchów (pól 1-9), więc z korzenia wychodzi 9 gałęzi:

Poziom 1:    O . .    . O .    . . O       ...i 6 innych
             . . .    . . .    . . .
             . . .    . . .    . . .
             (ruch 1) (ruch 2) (ruch 3)

Każdy z tych stanów ma 8 pustych pól, więc przeciwnik (X) ma 8 ruchów:

Poziom 2:    O X .    O . X    O . .       ...itd.
             . . .    . . .    X . .
             . . .    . . .    . . .

I tak dalej, aż do stanów końcowych (ktoś wygrał lub plansza pełna).
```

### Rozmiar drzewa

Dla kółka i krzyżyka 3x3:
- Na poziomie 0: 1 stan
- Na poziomie 1: 9 stanów
- Na poziomie 2: 9 × 8 = 72 stany
- Na poziomie 3: 9 × 8 × 7 = 504 stany
- ...
- Maksymalna głębokość: 9 (bo jest 9 pól)
- Górne ograniczenie: 9! = 362 880 stanów (w praktyce mniej, bo gra kończy się wcześniej)

Dla szachów drzewo ma około 10^120 stanów -- więcej niż atomów we wszechświecie. Dlatego **nie da się go w całości przejrzeć** i potrzebujemy sprytnych algorytmów.

### Kto rusza się na którym poziomie?

To kluczowa cecha drzewa gry:

```
Głębokość 0: rusza się GRACZ AKTUALNY    (MAX -- chce zmaksymalizować wynik)
Głębokość 1: rusza się PRZECIWNIK        (MIN -- chce zminimalizować wynik)
Głębokość 2: rusza się GRACZ AKTUALNY    (MAX)
Głębokość 3: rusza się PRZECIWNIK        (MIN)
...i tak na zmianę.
```

To naprzemienne "MAX-MIN" jest fundamentem algorytmu **Minimax**.

---

<a id="3-funkcja-oceny"></a>
## 3. Wartości w drzewie gry -- funkcja oceny (scoring)

### Po co wartości?

Każdy węzeł w drzewie gry potrzebuje **liczbowej oceny** -- ile ten stan jest "warty" z perspektywy aktualnego gracza. Dzięki temu algorytm może **porównywać** różne ruchy i wybrać najlepszy.

### Funkcja oceny w Tic-tac-doh

W kodzie (`tictac.py:108`):

```python
def scoring(self):
    return -100 if self.lose() else 0
```

Co to znaczy:
- **`-100`** = aktualny gracz PRZEGRAŁ (przeciwnik ma trzy w rzędzie). Wartość ujemna, bo przegrana to zły wynik.
- **`0`** = gra trwa dalej lub remis. Neutralna wartość.

**Uwaga:** Nie ma `+100` za wygraną, bo `lose()` sprawdza przegranie **aktualnego gracza**. Wygrana aktualnego gracza to przegrana przeciwnika, czyli na kolejnym poziomie drzewa pojawi się `-100`.

### Modyfikacja wartości względem głębokości

W algorytmach (np. `negamax_no_ab.py:14-16`):

```python
if score == 0:
    return score
return score - 0.01 * depth * abs(score) / score
```

To sprytna sztuczka: **wygrane osiągane szybciej są warte więcej niż wygrane osiągane później**. Dzięki temu AI woli wygrać w 3 ruchy niż w 7 ruchów. Analogicznie, przegrana za 7 ruchów jest "lepsza" (mniej bolesna) niż przegrana za 3 ruchy.

Przykład:
- Wygrana na głębokości 2: `100 - 0.01 * 2 * 1 = 99.98`
- Wygrana na głębokości 6: `100 - 0.01 * 6 * 1 = 99.94`
- AI wybierze `99.98 > 99.94`, czyli szybszą wygraną.

### Wartości propagowane w drzewie

Liście mają wartości bezpośrednio z funkcji oceny. Ale co z węzłami wewnętrznymi? Ich wartości są **obliczane od dołu do góry** (bottom-up) za pomocą algorytmu Minimax:

```
        MAX (gracz)
       /     \
    MIN       MIN (przeciwnik)
   /   \     /   \
  3    -5   7    -2      <- liście: wartości z scoring()

Węzeł MIN lewy:  min(3, -5)  = -5   (przeciwnik wybiera gorsze dla nas)
Węzeł MIN prawy: min(7, -2)  = -2   (przeciwnik wybiera gorsze dla nas)
Węzeł MAX:       max(-5, -2) = -2   (my wybieramy lepsze dla nas)

Wynik: gramy w prawo (wartość -2 lepsza niż -5)
```

---

<a id="4-minimax"></a>
## 4. Algorytm Minimax -- "zakładam, że przeciwnik gra optymalnie"

### Główna idea

Minimax opiera się na jednym genialnym założeniu:

> **Przeciwnik zawsze zagra najlepiej jak potrafi.**

To prowadzi do strategii:
- **Ja (MAX)** wybieram ruch, który **maksymalizuje** mój wynik
- **Przeciwnik (MIN)** wybiera ruch, który **minimalizuje** mój wynik

### Algorytm krok po kroku

```
MINIMAX(węzeł, głębokość, czyGraczMAX):
    jeśli węzeł jest liściem LUB głębokość = 0:
        zwróć scoring(węzeł)

    jeśli czyGraczMAX:
        najlepsza = -nieskończoność
        dla każdego ruchu z możliwych_ruchów(węzeł):
            wartość = MINIMAX(dziecko, głębokość-1, FALSE)
            najlepsza = max(najlepsza, wartość)
        zwróć najlepsza

    w przeciwnym razie:  // gracz MIN
        najlepsza = +nieskończoność
        dla każdego ruchu z możliwych_ruchów(węzeł):
            wartość = MINIMAX(dziecko, głębokość-1, TRUE)
            najlepsza = min(najlepsza, wartość)
        zwróć najlepsza
```

### Pełny przykład

Rozważmy mini-drzewo gry (głębokość 3):

```
                              MAX
                           /       \
                        MIN         MIN
                       / | \       / | \
                     MAX MAX MAX MAX MAX MAX
                     /\  /\  /\  /\  /\  /\
                    3 5 6 9 1 2 0 7 4 2 8 1   <- wartości liści
```

**Krok 1: Obliczamy wartości najgłębszych węzłów MAX** (każdy wybiera max ze swoich dzieci):

```
                     MAX MAX MAX MAX MAX MAX
                     /\  /\  /\  /\  /\  /\
                    3 5 6 9 1 2 0 7 4 2 8 1

                      5   9   2   7   4   8     <- MAX wybiera większe
```

**Krok 2: Obliczamy wartości węzłów MIN** (każdy wybiera min ze swoich dzieci):

```
                        MIN         MIN
                       / | \       / | \
                      5   9   2   7   4   8

                        2             4         <- MIN wybiera mniejsze
```

**Krok 3: Korzeń MAX wybiera max(2, 4) = 4**, więc gramy w prawo.

### Dlaczego to działa?

Bo zakładamy **najgorszy scenariusz**. Jeśli przeciwnik gra optymalnie, to i tak osiągniemy wynik co najmniej 4. Gdybyśmy wybrali lewą gałąź, przy optymalnym przeciwniku dostalibyśmy tylko 2.

To jest strategia **pesymistyczna ale bezpieczna** -- gwarantuje nam najlepszy wynik w najgorszym przypadku.

---

<a id="5-negamax"></a>
## 5. Negamax -- elegancka wersja Minimaxa

### Problem z Minimaxem

W czystym Minimaxie musimy rozróżniać, czy jesteśmy na poziomie MAX czy MIN. To wymaga dwóch osobnych bloków kodu i parametru `czyGraczMAX`.

### Kluczowa obserwacja

> **To, co jest dobre dla mnie, jest złe dla przeciwnika.**

Matematycznie: `min(a, b) = -max(-a, -b)`

Czyli zamiast "minimalizować" na poziomie przeciwnika, możemy **zawsze maksymalizować**, ale **negować** (odwracać znak) wartość zwróconą przez przeciwnika!

### Algorytm Negamax

```
NEGAMAX(węzeł, głębokość):
    jeśli węzeł jest liściem LUB głębokość = 0:
        zwróć scoring(węzeł)    // z perspektywy AKTUALNEGO gracza

    najlepsza = -nieskończoność
    dla każdego ruchu z możliwych_ruchów(węzeł):
        wykonaj_ruch(ruch)
        zmień_gracza()
        wartość = -NEGAMAX(dziecko, głębokość-1)   // MINUS!
        cofnij_ruch(ruch)
        najlepsza = max(najlepsza, wartość)

    zwróć najlepsza
```

**Kluczowy element to ten minus:** `-NEGAMAX(...)`. Oznacza on: "weź wynik z perspektywy przeciwnika i odwróć znak, żeby uzyskać wynik z mojej perspektywy".

### Negamax w kodzie projektu

Implementacja z `negamax_no_ab.py:10-44`:

```python
def _negamax_no_ab(game, depth, orig_depth, scoring):
    # Warunek stopu: liść lub osiągnięta głębokość
    if (depth == 0) or game.is_over():
        score = scoring(game)
        if score == 0:
            return score
        return score - 0.01 * depth * abs(score) / score

    possible_moves = game.possible_moves()
    best_move = possible_moves[0]

    if depth == orig_depth:
        game.ai_move = possible_moves[0]   # zapamiętaj najlepszy ruch

    best_value = -inf                       # zaczynamy od najgorszego

    for move in possible_moves:
        game.make_move(move)                # wykonaj ruch
        game.switch_player()                # zmień gracza

        # REKURENCJA Z NEGACJĄ -- serce Negamaxa
        move_value = -_negamax_no_ab(game, depth - 1, orig_depth, scoring)

        game.switch_player()                # cofnij zmianę gracza
        game.unmake_move(move)              # cofnij ruch

        if best_value < move_value:         # znaleźliśmy lepszy ruch?
            best_value = move_value
            best_move = move
            if depth == orig_depth:
                game.ai_move = move         # zapamiętaj najlepszy ruch

    return best_value
```

### Dlaczego `unmake_move` zamiast kopiowania?

Zauważ w kodzie gry (`tictac.py:62-63`):

```python
def unmake_move(self, move):
    self.board[int(move) - 1] = 0
```

Zamiast kopiować cały stan gry (co jest kosztowne pamięciowo), robimy ruch, rekurencyjnie przeszukujemy, a potem **cofamy ruch** ustawiając pole na 0. To ogromna optymalizacja -- zamiast tworzyć tysiące kopii planszy, operujemy na jednej.

---

<a id="6-ograniczenie-glebokosci"></a>
## 6. Ograniczenie głębokości -- dlaczego nie przeszukujemy całego drzewa

### Problem

Nawet dla kółka i krzyżyka pełne drzewo ma setki tysięcy stanów. Dla szachów to 10^120.
Przeszukiwanie całego drzewa jest **zbyt wolne** dla większości gier.

### Rozwiązanie: ograniczenie głębokości

Zamiast przeszukiwać do samych liści, **zatrzymujemy się na ustalonej głębokości** i używamy **funkcji oceny heurystycznej**, żeby ocenić jak dobry jest dany stan.

```
Pełne drzewo:                 Drzewo z głębokością = 2:
      A                              A
    / | \                          / | \
   B  C  D                       B  C  D
  /|  |  |\                     /|  |  |\
 E F  G  H I                   E F  G  H I  <- tu się ZATRZYMUJEMY
/\ |  |  /\                                    i oceniamy heurystycznie
...........                                     zamiast iść głębiej
```

### Głębokość w projekcie

W eksperymentach testowano głębokości 2, 4, 6 i 8:

- **Głębokość 2**: AI "widzi" 2 ruchy do przodu (1 swój + 1 odpowiedź). Gra słabo, ale szybko.
- **Głębokość 4**: AI "widzi" 4 ruchy do przodu. Znacznie lepsza gra.
- **Głębokość 6**: AI "widzi" 6 ruchów do przodu. Prawie optymalna gra.
- **Głębokość 8**: AI "widzi" prawie do końca gry (max 9 ruchów). Optymalna, ale wolna.

**Kluczowy wynik z eksperymentów:** Przy głębokości 4 w trybie deterministycznym wszystkie gry kończą się remisem (AI gra optymalnie). To dlatego, że kółko i krzyżyk to na tyle prosta gra, że 4 ruchy do przodu wystarczą do znalezienia optymalnej strategii.

### Kompromis głębokość vs. czas

Z raportu projektu:

| Głębokość | Śr. czas/ruch (Negamax z α-β) |
|:---------:|:------------------------------:|
| 2         | ~60 μs                         |
| 6         | ~2.6 ms                        |

Czas rośnie **wykładniczo** z głębokością, bo na każdym poziomie mnożymy liczbę stanów przez liczbę możliwych ruchów.

---

<a id="7-alfa-beta"></a>
## 7. Odcięcie alfa-beta -- pomijamy to, co nie ma sensu

To jest **najważniejsza optymalizacja** w przeszukiwaniu drzew gier. Pozwala osiągnąć ten sam wynik co Minimax/Negamax, ale bez przeszukiwania wszystkich gałęzi.

### Intuicja -- analogia do życia

Wyobraź sobie, że kupujesz mieszkanie i porównujesz dwie dzielnice:

- **Dzielnica A**: znalazłeś mieszkanie za 400 000 zł (i szukasz dalej w tej dzielnicy)
- **Dzielnica B**: pierwsze mieszkanie kosztuje 500 000 zł

Jeśli szukasz najtańszego mieszkania, **nie musisz już sprawdzać reszty ofert w dzielnicy B** -- nawet jeśli znajdziesz tam coś tańszego niż 500 000, to nic nie zmienia faktu, że w dzielnicy A masz już ofertę za 400 000 i szukasz tam czegoś jeszcze lepszego.

Dokładnie tak działa odcięcie alfa-beta.

### Definicja alpha i beta

```
alpha (α) = DOLNA GRANICA -- najlepsza wartość, jaką gracz MAX
            ma ZAGWARANTOWANĄ (może osiągnąć na pewno).
            Zaczyna od -∞ (nic jeszcze nie gwarantujemy).

beta (β)  = GÓRNA GRANICA -- najlepsza wartość, jaką gracz MIN
            może ograniczyć gracza MAX (najgorsze co MAX może dostać).
            Zaczyna od +∞ (MIN jeszcze niczego nie ograniczył).
```

### Reguła odcięcia

> **Jeśli α ≥ β, PRZESTAŃ przeszukiwać tę gałąź.**

Dlaczego? Bo to oznacza, że gracz MAX ma już gwarantowany wynik (α) lepszy niż najlepsze co gracz MIN mu pozwoli (β) w tej gałęzi. Więc **MIN nigdy nie pozwoli tutaj dojść** -- wybierze wcześniejszą, lepszą (dla MIN) opcję.

### Pełny przykład krok po kroku

```
                MAX (α=-∞, β=+∞)
               /                \
        MIN (α=-∞, β=+∞)     MIN (α=3, β=+∞)
        /      \              /      \
      MAX      MAX          MAX      MAX
      /\       /\           /\       /\
     3  5    6  9          1  ?     ?  ?
```

**Krok 1:** Idziemy lewą stroną do samego dołu.
- Liść `3`: wartość = 3
- Liść `5`: wartość = 5
- Węzeł MAX: max(3, 5) = **5**

**Krok 2:** Wracamy do lewego węzła MIN.
- Dziecko lewe dało 5. Aktualizujemy: `β = min(+∞, 5) = 5`
- Idziemy do prawego dziecka MAX:
  - Liść `6`: wartość = 6
  - Ten MAX ma już 6. Ale rodzic MIN ma β=5. Węzeł MAX ma α=6 ≥ β=5.
  - **ODCIĘCIE!** Nie musimy sprawdzać liścia `9` -- MIN i tak wybierze lewą gałąź (wartość 5), bo prawa daje MAX co najmniej 6 (gorzej dla MIN).
- Węzeł MIN lewy: wartość = **5**. Aktualizujemy w MIN wyżej: traktujemy jako wartość 5.

**Krok 3:** Wracamy do korzenia MAX.
- Lewe dziecko dało 5. Aktualizujemy: `α = max(-∞, 5) = 5`. Teraz α=5.

**Krok 4:** Idziemy w prawo. Prawy węzeł MIN dziedziczy α=5 od rodzica (ale jako β=+∞ — MIN jeszcze nie ma ograniczeń z prawej strony, ale MAX ma zagwarantowane 5).
- Węzeł MAX prawy-lewy: liść `1`. Wartość = 1.
  - Wracamy do prawego MIN: dziecko dało 1. `β = min(+∞, 1) = 1`.
  - Teraz α=5, β=1. **α ≥ β → ODCIĘCIE!**
  - Nie musimy w ogóle sprawdzać prawego dziecka MIN!

**Wynik:** Korzeń MAX wybiera lewą gałąź (wartość 5).

**Co zaoszczędziliśmy?** Nie musieliśmy sprawdzać 3 liści (9, i oba liście prawego poddrzewa). W dużych drzewach to ogromna oszczędność.

### Jak duża jest oszczędność?

Idealnie (przy dobrym porządku ruchów) alfa-beta redukuje liczbę odwiedzanych węzłów z **b^d** do **b^(d/2)**, gdzie `b` = liczba ruchów, `d` = głębokość.

To znaczy: **alfa-beta pozwala przeszukać drzewo dwa razy głębiej w tym samym czasie!**

Z raportu projektu (głębokość 6):

| Algorytm                    | Śr. czas/ruch |  Przyspieszenie |
|:----------------------------|:--------------:|:---------------:|
| Negamax **bez** alfa-beta   | 61.10 ms       | 1× (bazowy)    |
| Negamax **z** alfa-beta     | 2.59 ms        | **23.6×**       |

Alfa-beta daje tutaj **23.6-krotne przyspieszenie** przy zachowaniu identycznych decyzji!

### Wizualizacja odcięcia

```
        MAX
       / | \
      3  ?  ?         <- MAX znalazł 3 w lewej gałęzi (α = 3)
         |
        MIN
       / | \
      2  ?  ?         <- MIN znalazł 2 (β = 2). Ale α(3) ≥ β(2)!
                          ODCIĘCIE ✂️ -- nie sprawdzamy "?" w MIN

Dlaczego? MAX już ma gwarancję 3 (z lewej gałęzi).
MIN w środkowej gałęzi daje co najwyżej 2 (bo znalazł 2 i szuka mniejszych).
MAX NIGDY nie wybierze tej gałęzi, bo 2 < 3. Więc po co dalej sprawdzać?
```

---

<a id="8-sss"></a>
## 8. SSS* -- przeszukiwanie best-first

### Idea

SSS* (State Space Search*) to alternatywne podejście do przeszukiwania drzew gier. Zamiast przeszukiwać drzewo **w głąb** (depth-first) jak Minimax/Negamax, SSS* przeszukuje je **"najlepszy najpierw"** (best-first).

### Jak to działa?

1. SSS* utrzymuje **listę otwartych stanów** (priority queue) posortowaną po wartości
2. Zawsze rozwija **najbardziej obiecujący stan** (ten z najwyższą wartością)
3. Teoretycznie odwiedza **mniej węzłów** niż alfa-beta, bo nie traci czasu na beznadziejne gałęzie

### W teorii vs. w praktyce

**Teoria:** SSS* nigdy nie odwiedza więcej węzłów niż alfa-beta i często odwiedza mniej.

**Praktyka (z raportu):** SSS* jest **wolniejsze** niż Negamax z alfa-beta!

| Algorytm          | Śr. czas/ruch (głęb. 6) |
|:-------------------|:------------------------:|
| Negamax (α-β)      | 2.59 ms                 |
| SSS*               | 3.34 ms                 |

Dlaczego? Bo SSS* potrzebuje dużo **pamięci** (lista otwartych stanów) i **narzutu obliczeniowego** na zarządzanie kolejką priorytetową. Dla małych gier jak kółko i krzyżyk ten narzut jest większy niż zysk z odwiedzania mniejszej liczby węzłów.

SSS* opłaca się bardziej w **dużych grach** z dużym współczynnikiem rozgałęzienia, gdzie redukcja liczby węzłów jest na tyle duża, że rekompensuje narzut pamięciowy.

---

<a id="9-wezly-szansy"></a>
## 9. Gry z losowością -- węzły szansy (chance nodes)

### Problem: Tic-tac-doh

Tic-tac-doh dodaje do kółka i krzyżyka **element losowy**: każdy ruch ma **20% szans na niepowodzenie**. Gdy ruch się nie uda, na planszy nic się nie zmienia (żaden znak nie jest postawiony), a kolej przechodzi do przeciwnika.

To fundamentalnie zmienia naturę gry, bo **ten sam ruch może prowadzić do różnych stanów**.

### Nowy typ węzła: węzeł szansy

W standardowym drzewie gry mamy węzły MAX i MIN. W grach z losowością pojawia się **trzeci typ: węzeł szansy** (chance node).

```
Drzewo gry BEZ losowości:          Drzewo gry Z losowością:

     MAX                                  MAX
    / | \                                / | \
  MIN MIN MIN                      CHANCE CHANCE CHANCE
  /\  /\  /\                        / \    / \    / \
                               sukces fail sukces fail sukces fail
                               (80%) (20%) (80%) (20%) (80%) (20%)
                                |     |     |     |     |     |
                               MIN   MIN   MIN   MIN   MIN   MIN
```

### Co się dzieje w węźle szansy?

Węzeł szansy **nie podejmuje decyzji** (w przeciwieństwie do MAX i MIN). Zamiast tego:

1. Ma kilka możliwych **wyników** (sukces, porażka)
2. Każdy wynik ma przypisane **prawdopodobieństwo**
3. Wartość węzła szansy = **średnia ważona** wartości dzieci

W Tic-tac-doh:
- **Sukces** (prawdopodobieństwo 80%): znak jest postawiony, przeciwnik rusza
- **Porażka** (prawdopodobieństwo 20%): nic się nie zmienia, przeciwnik rusza

```
    CHANCE(ruch na pole 5)
       /          \
   SUKCES(80%)   PORAŻKA(20%)
      |              |
  O na polu 5    plansza bez zmian
  rusza X         rusza X
```

### Dlaczego standardowy Minimax tutaj nie działa optymalnie?

Standardowy Minimax/Negamax **nie wie o losowości**. Podczas przeszukiwania drzewa symuluje ruchy deterministycznie (ruch zawsze się udaje). Potem, podczas rzeczywistej gry, ruch może się nie udać -- ale AI tego nie uwzględniła w swoich obliczeniach.

To znaczy, że Negamax może wybrać ruch, który jest **optymalny jeśli się uda**, ale **katastrofalny jeśli się nie uda** -- nie biorąc pod uwagę, że jest 20% szans na niepowodzenie.

---

<a id="10-expectiminimax"></a>
## 10. Expecti-Minimax -- Minimax dla gier losowych

### Idea

Expecti-Minimax (znany też jako Expectiminimax) rozszerza Minimax o **węzły szansy**. Na każdym poziomie drzewa mamy teraz trzy typy węzłów:

- **MAX**: gracz maksymalizujący (wybiera max)
- **MIN**: gracz minimalizujący (wybiera min)
- **CHANCE**: węzeł losowy (liczy średnią ważoną)

### Algorytm

```
EXPECTIMINIMAX(węzeł, głębokość):
    jeśli węzeł jest liściem LUB głębokość = 0:
        zwróć scoring(węzeł)

    jeśli węzeł jest typu MAX:
        zwróć max(EXPECTIMINIMAX(dziecko) dla każdego dziecka)

    jeśli węzeł jest typu MIN:
        zwróć min(EXPECTIMINIMAX(dziecko) dla każdego dziecka)

    jeśli węzeł jest typu CHANCE:
        zwróć Σ (prawdopodobieństwo_i × EXPECTIMINIMAX(dziecko_i))
```

### Wartość oczekiwana ruchu w Tic-tac-doh

Z kodu `expectiminimax.py`:

```
V(ruch) = (1 - p) × V(sukces) + p × V(porażka)
         = 0.80   × V(sukces) + 0.20 × V(porażka)
```

Gdzie:
- `V(sukces)` = wartość stanu, gdy ruch się **udał** (znak postawiony, rusza przeciwnik)
- `V(porażka)` = wartość stanu, gdy ruch się **nie udał** (plansza bez zmian, rusza przeciwnik)
- `p = 0.20` = szansa na nieudany ruch

### Przykład liczbowy

Gracz O rozważa ruch na pole 5:

```
   CHANCE(pole 5)
   /            \
SUKCES(80%)   PORAŻKA(20%)
   |              |
  MIN             MIN
  ...              ...
wartość: +50    wartość: -30

V(pole 5) = 0.80 × (+50) + 0.20 × (-30)
           = 40 + (-6)
           = +34
```

Porównaj z polem 1:

```
   CHANCE(pole 1)
   /            \
SUKCES(80%)   PORAŻKA(20%)
   |              |
  MIN             MIN
  ...              ...
wartość: +60    wartość: -80

V(pole 1) = 0.80 × (+60) + 0.20 × (-80)
           = 48 + (-16)
           = +32
```

**Wynik:** Expecti-Minimax wybiera pole 5 (+34 > +32), mimo że pole 1 daje lepszy wynik przy sukcesie (+60 > +50). Dlaczego? Bo pole 1 jest **bardziej ryzykowne** -- przy porażce daje -80 zamiast -30.

**Standardowy Negamax wybrałby pole 1** (patrzy tylko na sukces: +60 > +50), nie widząc ryzyka porażki.

### Implementacja w projekcie

Z `expectiminimax.py:43-88`:

```python
for move in possible_moves:
    if fail_chance > 0 and depth > 0:
        # --- Węzeł szansy ---
        p_fail = fail_chance        # 0.20
        p_success = 1.0 - fail_chance  # 0.80

        # Wynik 1: ruch SIĘ UDAJE
        game_success.make_move(move)
        game_success.switch_player()
        v_success = -_expectiminimax(game_success, depth-1, ...)

        # Wynik 2: ruch SIĘ NIE UDAJE (plansza bez zmian, rusza przeciwnik)
        game_fail.switch_player()   # tylko zmiana gracza, BEZ ruchu
        v_fail = -_expectiminimax(game_fail, depth-1, ...)

        # Wartość oczekiwana
        move_value = p_success * v_success + p_fail * v_fail
    else:
        # Tryb deterministyczny -- standardowy Negamax
        ...
```

### Koszt obliczeniowy

Expecti-Minimax jest **dramatycznie droższy** niż zwykły Negamax, bo dla każdego ruchu musi obliczyć **dwie gałęzie** zamiast jednej (sukces i porażka):

| Algorytm                | Śr. czas/ruch (głęb. 6, prob.) |  vs Negamax α-β    |
|:------------------------|:-------------------------------:|:-------------------:|
| Negamax (α-β)           | 2.59 ms                         | 1× (bazowy)        |
| Negamax (bez α-β)       | 61.10 ms                        | 24×                |
| **ExpectiMinimax (α-β)**| **2 978 ms (~3 s)**            | **~700×**           |

Dla 50 gier na głębokości 6 w trybie probabilistycznym, ExpectiMinimax potrzebował **~21.5 minuty** -- w porównaniu do sekund dla Negamaxa.

---

<a id="11-star1"></a>
## 11. Star1 Pruning -- odcięcie alfa-beta dla węzłów szansy

### Problem

Standardowe odcięcie alfa-beta **nie działa** na węzłach szansy. Dlaczego?

W nodeach MAX/MIN wiemy, że wartość jest **dokładnie** max lub min z dzieci. Więc jak tylko znamy jedną wartość, możemy ograniczyć przeszukiwanie.

Ale w nodeach CHANCE wartość to **średnia ważona**. Nawet jeśli jedno dziecko ma wartość 100, średnia może być niska (jeśli inne dziecko ma wartość -100 z dużą wagą). Dlatego potrzebujemy specjalnej techniki.

### Idea Star1

Star1 (stylizowane: \*1) to technika adaptacji odcięcia alfa-beta do węzłów szansy. Kluczowa idea:

> Znając **ograniczenia na wartości** (min_score, max_score) w grze, możemy **zawęzić okno alfa-beta** dla każdej gałęzi szansy.

### Jak to działa

Mamy węzeł szansy z dwoma wynikami: sukces (p=0.8) i porażka (p=0.2).

**Krok 1:** Obliczamy najpierw gałąź sukcesu, z zawężonym oknem:

```
alpha_sukces = (alpha - p_fail × min_score) / p_success
beta_sukces  = (beta  - p_fail × max_score) / p_success
```

Dlaczego te wartości? Bo wiemy, że wartość porażki będzie w przedziale [min_score, max_score].
Więc aby cała średnia ważona mieściła się w [α, β], gałąź sukcesu musi mieścić się w zawężonym oknie.

**Krok 2:** Po obliczeniu `v_success`, zawężamy okno dla gałęzi porażki:

```
alpha_porazka = (alpha - p_success × v_success) / p_fail
beta_porazka  = (beta  - p_success × v_success) / p_fail
```

Teraz znamy dokładną wartość sukcesu, więc możemy **precyzyjnie** obliczyć jakie wartości porażki pozwolą na odcięcie.

**Krok 3:** Jeśli `alpha_porazka ≥ beta_porazka`, to **odcinamy** -- nie musimy w ogóle obliczać gałęzi porażki!

### Implementacja w projekcie

Z `expectiminimax.py:50-59`:

```python
# Star1 pruning: zawężone okno dla gałęzi sukcesu
alpha_s = (alpha - p_fail * (-min_score)) / p_success
beta_s = (beta - p_fail * (-max_score)) / p_success

v_success = -_expectiminimax(
    game_success, depth - 1, orig_depth, scoring,
    -beta_s, -alpha_s, fail_chance, score_bounds
)
```

I dla gałęzi porażki (`expectiminimax.py:68-74`):

```python
# Star1 bounds for fail branch
alpha_f = (alpha - p_success * v_success) / p_fail
beta_f = (beta - p_success * v_success) / p_fail

# Clamp to valid score range
alpha_f = max(alpha_f, -(-min_score))
beta_f = min(beta_f, -(-max_score))

if alpha_f < beta_f:
    v_fail = -_expectiminimax(...)  # normalna rekurencja
else:
    # ODCIĘCIE -- gałąź porażki nie zmieni decyzji
    v_fail = -_expectiminimax(...)  # fallback z pełnym oknem
```

### Dlaczego score_bounds?

Zauważ parametr `score_bounds = (-100, 100)` w kodzie. To KLUCZOWY element Star1 -- musimy znać **skrajne możliwe wartości** oceny, żeby wielkie okno alfa-beta zawężać. W Tic-tac-doh scoring zwraca wartości z przedziału [-100, 0] (z modyfikacjami głębokości blisko tych granic), więc `win_score=100` to bezpieczna granica.

---

<a id="12-podsumowanie"></a>
## 12. Podsumowanie -- porównanie wszystkich algorytmów

### Tabela algorytmów

| Algorytm | Typ przeszukiwania | Obsługuje losowość? | Odcięcie | Złożoność | Zastosowanie |
|:---------|:-------------------|:-------------------:|:--------:|:---------:|:-------------|
| Minimax | Depth-first, MAX/MIN | Nie | Brak | O(b^d) | Gry deterministyczne |
| Negamax | Depth-first, negacja | Nie | Brak | O(b^d) | Jak Minimax, prostszy kod |
| Negamax + α-β | Depth-first, negacja | Nie | Alfa-beta | O(b^(d/2)) idealnie | Standard dla gier determ. |
| SSS* | Best-first | Nie | Tak (implicitnie) | O(b^(d/2)) | Gry z dużym rozgałęzieniem |
| ExpectiMinimax | Depth-first, chance nodes | **TAK** | Brak | O(b^d × c^d) | Gry losowe |
| ExpectiMinimax + Star1 | Depth-first, chance nodes | **TAK** | Star1 | < O(b^d × c^d) | Gry losowe (optymalizowane) |

Gdzie `b` = współczynnik rozgałęzienia, `d` = głębokość, `c` = liczba wyników losowych (2 w Tic-tac-doh: sukces/porażka).

### Jak algorytmy podejmują decyzję -- podsumowanie procesu

```
1. BUDOWA DRZEWA: Od aktualnego stanu wygeneruj wszystkie możliwe ruchy

2. REKURENCJA: Dla każdego ruchu, zasymuluj go i rekurencyjnie przeszukaj
   dalsze możliwości (do ustalonej głębokości lub końca gry)

3. OCENA LIŚCI: Na dole drzewa oceń stan funkcją scoring():
   - Przegrana = -100 (bardzo źle)
   - Remis/gra trwa = 0 (neutralnie)

4. PROPAGACJA W GÓRĘ:
   - Węzły MAX: wybierz maximum z wartości dzieci (gracz chce wygrać)
   - Węzły MIN: wybierz minimum z wartości dzieci (przeciwnik chce wygrać)
   - Węzły CHANCE: oblicz średnią ważoną prawdopodobieństwami

5. ODCIĘCIE: Pomiń gałęzie, które na pewno nie zmienią decyzji:
   - Alfa-beta: gdy α ≥ β (granice się przecięły)
   - Star1: gdy zawężone okno dla chance node jest puste

6. WYBÓR RUCHU: Korzeń (aktualny stan) wybiera ruch z najwyższą wartością
```

### Kiedy którego algorytmu użyć?

```
Gra deterministyczna + mała?     → Negamax z α-β (szybki, optymalny)
Gra deterministyczna + duża?     → Negamax z α-β + heurystyki porządkowania
Gra z losowością?                → ExpectiMinimax z Star1
Potrzebujesz "benchmark" bez optymalizacji?  → Negamax bez α-β
```

### Wyniki eksperymentów -- czego się dowiedzieliśmy

1. **α-β pruning jest kluczowe:** 23.6× przyspieszenie przy identycznych wynikach
2. **SSS\* nie opłaca się dla małych gier:** narzut pamięciowy > zysk z mniejszej liczby węzłów
3. **Głębokość ma znaczenie w grach losowych:** głębokość 8 daje więcej remisów (49) niż głębokość 4 (34) w trybie probabilistycznym
4. **ExpectiMinimax jest "poprawniejszy" ale ekstremalnie drogi:** ~700× wolniejszy za marginalną poprawę jakości (21 vs 20 remisów na 50 gier)
5. **Dla prostych gier losowych Negamax jest wystarczający:** dodatkowa jakość z ExpectiMinimax nie uzasadnia kosztu obliczeniowego

---

<a id="13-slownik"></a>
## 13. Słownik pojęć

| Pojęcie | Definicja |
|:--------|:----------|
| **Drzewo gry** | Struktura drzewa reprezentująca wszystkie możliwe przebiegi gry |
| **Korzeń (root)** | Aktualny stan gry, od którego zaczynamy przeszukiwanie |
| **Liść (leaf)** | Stan końcowy gry lub węzeł na maksymalnej głębokości |
| **Głębokość (depth)** | Ile ruchów do przodu przeszukujemy |
| **Współczynnik rozgałęzienia (branching factor)** | Średnia liczba możliwych ruchów w danym stanie |
| **Funkcja oceny (scoring/evaluation function)** | Funkcja przypisująca liczbową wartość stanowi gry |
| **Gracz MAX** | Gracz, który maksymalizuje wartość (aktualny gracz) |
| **Gracz MIN** | Gracz, który minimalizuje wartość (przeciwnik) |
| **Węzeł szansy (chance node)** | Węzeł reprezentujący losowy wynik (np. sukces/porażka ruchu) |
| **Wartość oczekiwana** | Średnia ważona wartości, z wagami = prawdopodobieństwa |
| **Alpha (α)** | Dolna granica: najlepsza zagwarantowana wartość dla MAX |
| **Beta (β)** | Górna granica: najlepsza zagwarantowana wartość dla MIN |
| **Odcięcie (pruning/cutoff)** | Pominięcie gałęzi drzewa, o których wiadomo, że nie zmienią decyzji |
| **Star1 pruning** | Technika odcięcia alfa-beta adaptowana do węzłów szansy |
| **Negamax** | Wariant Minimaxa korzystający z negacji: `min(a,b) = -max(-a,-b)` |
| **Heurystyka** | Przybliżona ocena stanu gry, gdy nie docieramy do końca drzewa |
| **`unmake_move`** | Cofanie ruchu zamiast kopiowania stanu -- optymalizacja pamięciowa |

---

> **Kluczowe źródła:** Implementacja w `Project1/` (Negamax, ExpectiMinimax), biblioteka easyAI, skrypt laboratoryjny `EasyAI.pdf`.
