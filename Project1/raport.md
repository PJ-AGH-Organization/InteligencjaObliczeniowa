---
title: "Projekt 1: EasyAI — Tic-tac-doh"
subtitle: "Inteligencja Obliczeniowa, Semestr 6"
author:
  - "Imię i nazwisko (nr indeksu)"
  - "Imię i nazwisko (nr indeksu)"
date: "10 marca 2026"
geometry: margin=2.5cm
fontsize: 11pt
lang: pl
toc: true
numbersections: true
header-includes:
  - \usepackage{booktabs}
  - \usepackage{float}
  - \floatplacement{table}{H}
---

# Wprowadzenie

Raport przedstawia implementację probabilistycznego wariantu kółko–krzyżyk (Tic-tac-doh) oraz porównanie algorytmów przeszukiwania drzewa gry pod względem jakości decyzji i kosztu obliczeniowego.

## Opis gry

Tic-tac-doh to wariant gry 3×3, w którym z prawdopodobieństwem 20% wykonany ruch „nie dochodzi do skutku” (na planszy nie pojawia się znacznik), a ruch przechodzi na przeciwnika. Wprowadzenie losowości powoduje, że wynik rozgrywki nie jest deterministyczny, a algorytmy nieuwzględniające ryzyka mogą podejmować decyzje nieoptymalne w sensie wartości oczekiwanej.


## Implementacja gry

Grę zaimplementowano w oparciu o EasyAI jako rozgrywkę dwuosobową z planszą 3×3. Kluczowym założeniem było rozdzielenie losowości od symulacji w drzewie gry: losowy „fail” jest stosowany wyłącznie przy faktycznym wykonaniu wybranego ruchu, natomiast w trakcie obliczania ruchu (symulacji stanów) mechanizm pozostaje deterministyczny.

Funkcja oceny przyjmuje wartość $-100$ w przypadku przegranej i $0$ w pozostałych stanach końcowych, co oznacza, że algorytmy priorytetyzują unikanie przegranej.


# Porównywane algorytmy

W ramach projektu zaimplementowano i porównano cztery algorytmy przeszukiwania drzewa gry:

## Negamax z odcięciem alfa-beta

Standardowy algorytm z biblioteki EasyAI. Negamax to wariant algorytmu Minimax, gdzie wartość pozycji jest negowana przy zmianie gracza, eliminując potrzebę osobnych faz minimalizacji i maksymalizacji. Odcięcie alfa-beta przyspiesza przeszukiwanie poprzez eliminację gałęzi drzewa, które nie mogą wpłynąć na wynik.

## Negamax bez odcięcia alfa-beta

Własna implementacja zgodna z interfejsem EasyAI. Przeszukuje **pełne drzewo gry** bez jakichkolwiek odcięć. Daje identyczne wyniki jak Negamax z alfa-beta, ale jest znacznie wolniejsza, ponieważ eksploruje każdy węzeł.

## SSS*

Algorytm SSS\* z biblioteki EasyAI. Jest to algorytm best-first search, który przeszukuje drzewo gry w kolejności „najbardziej obiecujących" gałęzi. Teoretycznie odwiedza mniejszą liczbę węzłów niż alfa-beta, ale wymaga dodatkowej pamięci.

## Expecti-Minimax z odcięciem alfa-beta

Własna implementacja zaprojektowana dla gier z elementem losowości. W odróżnieniu od standardowego Negamax, Expecti-Minimax **modeluje węzły losowe (chance nodes)** w drzewie gry.

Dla każdego ruchu algorytm oblicza wartość oczekiwaną:

$$V(\text{ruch}) = (1-p) \cdot V(\text{sukces}) + p \cdot V(\text{porażka})$$

gdzie $p = 0{,}2$ to prawdopodobieństwo nieudanego ruchu. W przypadku porażki plansza pozostaje bez zmian, a kolej przechodzi do przeciwnika.

Odcięcie alfa-beta na węzłach losowych wykorzystuje technikę **Star1 pruning**, która ogranicza przeszukiwanie na podstawie pesymistycznych i optymistycznych oszacowań wartości oczekiwanej. Dzięki temu algorytm nie musi zawsze eksplorować obu gałęzi (sukces/porażka) dla każdego ruchu — jeśli znana jest wartość jednej gałęzi, można zawęzić granice alfa-beta dla drugiej.


# Eksperymenty

Eksperymenty polegały na wielokrotnym rozgrywaniu partii **AI vs AI**, z wymianą gracza rozpoczynającego co partię, w celu zbadania:

1. Wpływu probabilistyczności na wyniki gry.
2. Wpływu głębokości przeszukiwania na jakość gry.
3. Różnic wydajnościowych (czas obliczenia ruchu) między algorytmami.
4. Różnic w skuteczności algorytmu uwzględniającego losowość (Expecti-Minimax) względem algorytmów deterministycznych.

Wszystkie eksperymenty uruchomiono z ustalonym ziarnem generatora losowego (42) dla powtarzalności wyników.

## Środowisko oraz powtarzalność

- Implementacja: Python (wymagane co najmniej 3.11), biblioteka EasyAI.
- Wartości czasów mają charakter zależny od sprzętu i obciążenia systemu; w analizie kluczowe są relacje (porządki wielkości) pomiędzy algorytmami oraz wpływ głębokości przeszukiwania.

## Wpływ głębokości Negamax na wyniki gry

Pierwszy eksperyment porównuje algorytm Negamax (z odcięciem alfa-beta) przy dwóch głębokościach przeszukiwania: **4** i **8**, na obu wariantach gry. Rozegrano **100 partii** na konfigurację.

| Głębokość | Wariant | Gracz 1 | Gracz 2 | Remisy |
|:---------:|:--------|--------:|--------:|-------:|
| 4 | Deterministyczny | 0 | 0 | 100 |
| 4 | Probabilistyczny | 42 | 24 | 34 |
| 8 | Deterministyczny | 0 | 0 | 100 |
| 8 | Probabilistyczny | 35 | 16 | 49 |

**Obserwacje:**

- W wariancie **deterministycznym** wszystkie partie kończą się remisem, niezależnie od głębokości. Tic-tac-toe jest grą o pełnej informacji z optymalnym rozwiązaniem remisowym, a głębokość 4 jest już wystarczająca, by AI grało bezbłędnie.
- W wariancie **probabilistycznym** losowość powoduje, że wiele partii kończy się wygraną jednego z graczy. Gracz 1 (rozpoczynający) wygrywa częściej, co jest przewagą wynikającą z inicjatywy.
- Przy **głębokości 8** Negamax gra lepiej niż przy głębokości 4 w wariancie probabilistycznym — więcej remisów (49 vs 34), co oznacza, że AI rzadziej popełnia błędy, nawet gdy ruch się nie uda. Głębsze przeszukiwanie pozwala lepiej kompensować nieudane ruchy.
- W obu wariantach probabilistycznych procent nieudanych ruchów oscyluje wokół oczekiwanych 20% (18,0% i 18,1%), co potwierdza poprawność implementacji.


## Porównanie algorytmów: wydajność i czas

Drugi eksperyment porównuje **cztery algorytmy** na obu wariantach gry, z głębokościami przeszukiwania **2** i **6**. Rozegrano **50 partii** na konfigurację.

**Metodyka pomiaru czasu.** Czas wyboru ruchu mierzono jako czas wykonania procedury wyboru ruchu dla aktualnego gracza (z użyciem zegara o wysokiej rozdzielczości), a następnie uśredniano po wszystkich ruchach ze wszystkich partii (dla obu graczy). W tabelach podano średni czas „na ruch”; pomocniczo analizowano również czas łączny i liczbę próbek (równą liczbie wykonanych ruchów w danej konfiguracji).

### Głębokość 2

| Algorytm | Wariant | G1 | G2 | Rem | Śr. czas/ruch |
|:---------|:--------|---:|---:|----:|---------------:|
| Negamax (α-β) | Deter. | 50 | 0 | 0 | 93 µs |
| Negamax (α-β) | Prob. | 36 | 12 | 2 | 93 µs |
| Negamax (bez α-β) | Deter. | 50 | 0 | 0 | 204 µs |
| Negamax (bez α-β) | Prob. | 36 | 12 | 2 | 207 µs |
| SSS\* | Deter. | 50 | 0 | 0 | 124 µs |
| SSS\* | Prob. | 36 | 12 | 2 | 120 µs |
| ExpectiMinimax (α-β) | Deter. | 50 | 0 | 0 | 522 µs |
| ExpectiMinimax (α-β) | Prob. | 36 | 12 | 2 | 482 µs |

### Głębokość 6

| Algorytm | Wariant | G1 | G2 | Rem | Śr. czas/ruch |
|:---------|:--------|---:|---:|----:|---------------:|
| Negamax (α-β) | Deter. | 0 | 0 | 50 | 2,59 ms |
| Negamax (α-β) | Prob. | 20 | 10 | 20 | 3,34 ms |
| Negamax (bez α-β) | Deter. | 0 | 0 | 50 | 61,02 ms |
| Negamax (bez α-β) | Prob. | 17 | 14 | 19 | 72,53 ms |
| SSS\* | Deter. | 0 | 0 | 50 | 3,93 ms |
| SSS\* | Prob. | 17 | 14 | 19 | 4,38 ms |
| ExpectiMinimax (α-β) | Deter. | 0 | 0 | 50 | 1,82 s |
| ExpectiMinimax (α-β) | Prob. | 19 | 10 | 21 | 2,98 s |


## Analiza wydajności algorytmów

### Wpływ odcięcia alfa-beta

Porównanie Negamax z i bez odcięcia alfa-beta wyraźnie pokazuje wartość tej optymalizacji:

| Głębokość | Bez α-β | Z α-β | Przyspieszenie |
|:---------:|--------:|------:|:--------------:|
| 2 | 204 µs | 93 µs | **2,2×** |
| 6 | 61,02 ms | 2,59 ms | **23,6×** |

Przyspieszenie rośnie wykładniczo z głębokością. Przy głębokości 6 odcięcie alfa-beta jest **ponad 23-krotnie szybsze**, ponieważ eliminuje znaczną część drzewa gry. Jest to zgodne z teorią — odcięcie alfa-beta w najlepszym przypadku redukuje liczbę odwiedzanych węzłów z $O(b^d)$ do $O(b^{d/2})$, gdzie $b$ to współczynnik rozgałęzienia, a $d$ to głębokość.

### SSS* vs Negamax (α-β)

SSS\* jest nieznacznie wolniejszy od Negamax z alfa-beta:

| Głębokość | Negamax (α-β) | SSS\* | Stosunek |
|:---------:|--------------:|------:|:--------:|
| 2 | 93 µs | 124 µs | 1,3× |
| 6 | 2,59 ms | 3,93 ms | 1,5× |

SSS\* wymaga dodatkowej pamięci do utrzymania listy otwartych węzłów, co wprowadza narzut. W praktyce, dla Tic-tac-doh, nie oferuje przewagi nad Negamax z alfa-beta.

### ExpectiMinimax vs Negamax (α-β)

ExpectiMinimax jest znacząco wolniejszy, ponieważ dla każdego ruchu musi zbadać dwa scenariusze (sukces + porażka):

| Głębokość | Negamax (α-β) | ExpectiMinimax | Stosunek |
|:---------:|--------------:|---------------:|:--------:|
| 2 | 93 µs | 522 µs | **5,6×** |
| 6 | 2,59 ms | 1,82 s | **700×** |

Dramatyczny wzrost kosztów przy głębokości 6 wynika z tego, że **każdy ruch** wymaga rozważenia dodatkowego scenariusza (sukces/porażka), co w praktyce zwiększa efektywny współczynnik rozgałęzienia drzewa. W konsekwencji liczba ocenianych stanów rośnie bardzo szybko wraz z głębokością, chociaż pruning Star1 częściowo ogranicza ten efekt.


## Analiza jakości decyzji

### Wariant deterministyczny

W wariancie deterministycznym przy głębokości 6 wszystkie algorytmy osiągają taki sam wynik — **100% remisów**. Oznacza to, że głębokość 6 jest wystarczająca, aby każdy z algorytmów grał optymalnie.

Przy głębokości 2 wszystkie algorytmy dają identyczny wynik (Gracz 1 wygrywa 50 gier na 50), co sugeruje, że Gracz 2 gra suboptmalnie z powodu zbyt płytkiego przeszukiwania.

### Wariant probabilistyczny

W wariancie probabilistycznym pojawiają się różnice:

| Algorytm (głęb. 6) | Gracz 1 | Gracz 2 | Remisy |
|:--------------------|--------:|--------:|-------:|
| Negamax (α-β) | 20 | 10 | **20** |
| Negamax (bez α-β) | 17 | 14 | **19** |
| SSS\* | 17 | 14 | **19** |
| ExpectiMinimax (α-β) | 19 | 10 | **21** |

ExpectiMinimax (21 remisów) osiąga porównywalne wyniki do Negamax z alfa-beta (20 remisów), oba lepsze od Negamax bez alfa-beta i SSS\* (po 19 remisów). Więcej remisów oznacza lepszą obronę — AI potrafi zminimalizować wpływ losowości na wynik.

Warto zauważyć, że **Negamax bez alfa-beta** i **SSS\*** dają identyczne wyniki pod względem wygranych/przegranych/remisów, co jest zgodne z oczekiwaniami — oba przeszukują drzewo w pełni (lub zbliżonej do pełnej) i podejmują identyczne decyzje.


# Napotkane problemy

1. **Separacja losowości od symulacji AI** — kluczowe było zapewnienie, że losowość (20% nieudanych ruchów) nie zaburza przeszukiwania drzewa gry. Rozwiązaniem było stosowanie losowego „fail” wyłącznie podczas faktycznego wykonania wybranego ruchu, a nie podczas symulacji stanów w trakcie obliczeń.

2. **Wydajność Expecti-Minimax** — algorytm jest ~700× wolniejszy od Negamax przy głębokości 6 (2,98 s vs 3,34 ms na ruch). W praktyce przekłada się to na bardzo duży czas łączny obliczeń: dla konfiguracji probabilistycznej (50 gier) suma czasów wyboru ruchu wyniosła ok. 1293 s (≈ 21,5 min). Podwójne rozgałęzienie na każdym węźle (sukces/porażka) dramatycznie zwiększa liczbę odwiedzanych węzłów. Mimo zastosowania pruningu Star1, narzut ten jest trudny do uniknięcia, co ogranicza maksymalną użyteczną głębokość przeszukiwania.

3. **Zgodność interfejsów** — własne implementacje algorytmów musiały być zgodne z interfejsem biblioteki wykorzystywanym do rozgrywek AI vs AI.


# Podsumowanie

Projekt obejmował implementację probabilistycznej gry Tic-tac-doh oraz porównanie czterech algorytmów przeszukiwania drzewa gry: Negamax z odcięciem alfa-beta, Negamax bez odcięcia, SSS\* oraz Expecti-Minimax z odcięciem alfa-beta.

Kluczowe wnioski:

- **Odcięcie alfa-beta** jest krytyczną optymalizacją — przyspiesza przeszukiwanie od 2× (głębokość 2) do ponad 23× (głębokość 6), bez wpływu na jakość decyzji.
- **SSS\*** nie oferuje istotnej przewagi nad Negamax z alfa-beta w kontekście Tic-tac-doh — jest nieco wolniejszy i daje identyczne wyniki.
- **Głębsze przeszukiwanie** poprawia wyniki w wariancie probabilistycznym — AI lepiej kompensuje losowe porażki ruchów.
- **Expecti-Minimax** jako jedyny algorytm explicite modeluje losowość w drzewie gry. Osiąga nieznacznie lepsze wyniki w wariancie probabilistycznym (więcej remisów), ale kosztem dramatycznie większego czasu obliczeń (~700× wolniejszy od Negamax z alfa-beta przy głębokości 6). W najbardziej kosztownej konfiguracji (głębokość 6, wariant probabilistyczny) łączny czas obliczeń dla 50 gier był rzędu kilkudziesięciu minut, co istotnie ogranicza praktyczne zastosowanie algorytmu dla większych głębokości.
- W kontekście Tic-tac-doh, ze względu na stosunkowo płytkie drzewo gry (maks. 9 ruchów), różnice w jakości decyzji między Negamax (α-β) a Expecti-Minimax nie są znaczące. Algorytm Expecti-Minimax miałby większy wpływ w grach z głębszym drzewem i wyższym prawdopodobieństwem losowych zdarzeń.

