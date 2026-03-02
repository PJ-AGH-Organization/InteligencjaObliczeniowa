# Projekt 1: Tic-tac-doh — Raport z eksperymentów z AI

> **Przedmiot:** Inteligencja obliczeniowa w analizie danych cyfrowych  
> **Biblioteka:** easyAI (Python)  
> **Wybrana gra:** Tic-tac-doh (kółko i krzyżyk z 20% szansą na nieudany ruch)

---

## 1. Opis gry

### 1.1 Klasyczne kółko i krzyżyk

Gra na planszy 3×3. Dwaj gracze naprzemiennie stawiają znaki (O i X). Wygrywa ten, kto pierwszy ułoży trzy swoje znaki w linii (poziomej, pionowej lub przekątnej). Jeśli plansza się zapełni bez trójki — remis.

### 1.2 Wariant probabilistyczny: Tic-tac-doh

W wariancie **Tic-tac-doh** każdy ruch ma **20% szansy na niepowodzenie**. Gdy ruch się nie uda:

- na planszy nie pozostaje żaden ślad,
- kolej przechodzi na przeciwnika.

To wprowadza element losowości — gra przestaje być deterministyczna, a jej wynik zależy nie tylko od strategii, ale też od szczęścia.

### 1.3 Implementacja

Gra zaimplementowana jako klasa `TicTacDoh` dziedzicząca po `TwoPlayerGame` (easyAI). Kluczowe metody:

| Metoda | Opis |
|--------|------|
| `possible_moves()` | Zwraca listę wolnych pól (1–9) |
| `make_move(move)` | Stawia znak; w trybie probabilistycznym losuje 20% szansę na fail |
| `unmake_move(move)` | Cofa ruch (optymalizacja dla AI) |
| `is_over()` | Sprawdza koniec gry (wygrana lub brak ruchów) |
| `scoring()` | Ocena pozycji: −100 za przegraną, 0 w innym wypadku |

**Ważny detal:** Losowanie 20% działa tylko przy rzeczywistych ruchach, nie przy symulacjach AI. Flaga `_apply_failure` włączana jest wyłącznie w pętli gry — Negamax eksploruje drzewo deterministycznie.

---

## 2. Algorytmy AI

### 2.1 Negamax z odcięciem alfa-beta

Wariant algorytmu Minimax z negacją ocen i **alpha-beta pruning**. Odcięcia eliminują gałęzie drzewa, które nie mogą zmienić wyniku, drastycznie redukując liczbę eksplorowanych stanów.

### 2.2 Negamax bez odcięcia alfa-beta

Własna implementacja czystego Negamax **bez** alpha-beta. Przeszukuje **pełne** drzewo gry — daje identyczne wyniki, ale jest znacznie wolniejsza (brak przycinania).

### 2.3 SSS*

Algorytm z biblioteki easyAI. Wariant Minimax z bardziej agresywnym przycinaniem niż standardowe alpha-beta. Eksploruje potencjalnie mniej stanów kosztem wyższej złożoności pamięciowej.

### 2.4 Parametr: głębokość

Głębokość określa liczbę pół-ruchów, które AI analizuje z wyprzedzeniem. Dla planszy 3×3:

- **Głębokość 2** — AI widzi 1 turę do przodu, gra słabo (wygrywa gracz 1).
- **Głębokość 4–6** — gra bliska optymalnej.
- **Głębokość 6–9** — gra optymalna, deterministyczne TTT kończy się remisem.

---

## 3. Eksperymenty — Part 1 (4 pkt)

### 3.1 Metodologia

- **Algorytm:** Negamax (z α-β)
- **Głębokości:** 4 i 8
- **Warianty:** deterministyczny i probabilistyczny
- **Liczba partii:** 100 na konfigurację (seed=42)
- **Alternacja:** co druga partia gracz 1 i 2 zamieniają się kolorem

### 3.2 Wyniki

| Głębokość | Wariant | Gracz 1 | Gracz 2 | Remisy | Ruchy | Nieudane | % nieud. |
|-----------|---------|--------:|--------:|-------:|------:|---------:|---------:|
| 4 | deterministyczny | 0 | 0 | 100 | 900 | — | — |
| 4 | probabilistyczny | 42 | 24 | 34 | 900 | 162 | 18,0% |
| 8 | deterministyczny | 0 | 0 | 100 | 900 | — | — |
| 8 | probabilistyczny | 35 | 16 | 49 | 884 | 160 | 18,1% |

### 3.3 Interpretacja

**Wariant deterministyczny:** Przy optymalnej grze (gł. 4 i 8 wystarczają) TTT zawsze kończy się remisem — 100% remisów, 900 ruchów (100 × 9 pełnych plansz).

**Wariant probabilistyczny:**
- Losowość łamie symetrię i generuje wygrane/przegrane mimo identycznego AI po obu stronach.
- Gracz 1 (zaczynający) wygrywa częściej — ma jeden dodatkowy ruch, co przy losowych failach daje statystyczną przewagę.
- **Głębokość 8 vs 4:** silniejsze AI generuje więcej remisów (49 vs 34), bo lepiej broni pozycji.
- Procent nieudanych ruchów (~18%) bliski teoretycznym 20% — typowa wariancja statystyczna na 100 próbach.

---

## 4. Eksperymenty — Part 2 (6 pkt)

### 4.1 Metodologia

- **Algorytmy:** Negamax (α-β), Negamax (bez α-β), SSS*
- **Głębokości:** 2 i 6
- **Warianty:** deterministyczny i probabilistyczny
- **Liczba partii:** 50 na konfigurację (seed=42)
- **Pomiar czasu:** `time.perf_counter()` wokół `ask_move()` — mierzy czas decyzji AI

### 4.2 Wyniki — zwycięstwa i remisy

| Algorytm | Głęb. | Wariant | G1 | G2 | Remisy | Ruchy | Nieud. | % nieud. |
|----------|------:|---------|---:|---:|-------:|------:|-------:|---------:|
| Negamax (α-β) | 2 | determin. | 50 | 0 | 0 | 350 | — | — |
| Negamax (α-β) | 2 | probabil. | 36 | 12 | 2 | 434 | 81 | 18,7% |
| Negamax (bez α-β) | 2 | determin. | 50 | 0 | 0 | 350 | — | — |
| Negamax (bez α-β) | 2 | probabil. | 36 | 12 | 2 | 434 | 81 | 18,7% |
| SSS* | 2 | determin. | 50 | 0 | 0 | 350 | — | — |
| SSS* | 2 | probabil. | 36 | 12 | 2 | 434 | 81 | 18,7% |
| Negamax (α-β) | 6 | determin. | 0 | 0 | 50 | 450 | — | — |
| Negamax (α-β) | 6 | probabil. | 20 | 10 | 20 | 419 | 76 | 18,1% |
| Negamax (bez α-β) | 6 | determin. | 0 | 0 | 50 | 450 | — | — |
| Negamax (bez α-β) | 6 | probabil. | 17 | 14 | 19 | 464 | 83 | 17,9% |
| SSS* | 6 | determin. | 0 | 0 | 50 | 450 | — | — |
| SSS* | 6 | probabil. | 17 | 14 | 19 | 464 | 83 | 17,9% |

**Kluczowe obserwacje:**
- Przy **głębokości 2** AI gra słabo — gracz 1 wygrywa wszystkie partie determinisyczne. Losowość wprowadza trochę remisów i wygranych gracza 2.
- Przy **głębokości 6** wszystkie algorytmy grają optymalnie w wariancie deterministycznym (same remisy). W wariancie probabilistycznym losowość decyduje o wyniku.
- Wszystkie algorytmy dają **identyczne wyniki** przy tym samym seed i głębokości (przeszukują to samo drzewo — różnią się tylko czasem).

### 4.3 Wyniki — średni czas na ruch

| Algorytm | Głęb. | Wariant | Śr. czas/ruch | Czas łączny | Przyspieszenie vs bez α-β |
|----------|------:|---------|---------------|-------------|---------------------------|
| Negamax (α-β) | 2 | determin. | 184 µs | 64 ms | 2,0× |
| Negamax (bez α-β) | 2 | determin. | 375 µs | 131 ms | — (bazowy) |
| SSS* | 2 | determin. | 245 µs | 86 ms | 1,5× |
| Negamax (α-β) | 2 | probabil. | 181 µs | 79 ms | 2,1× |
| Negamax (bez α-β) | 2 | probabil. | 377 µs | 164 ms | — (bazowy) |
| SSS* | 2 | probabil. | 234 µs | 102 ms | 1,6× |
| **Negamax (α-β)** | **6** | **determin.** | **4,84 ms** | **2,18 s** | **21,2×** |
| **Negamax (bez α-β)** | **6** | **determin.** | **102,84 ms** | **46,28 s** | **— (bazowy)** |
| **SSS\*** | **6** | **determin.** | **6,72 ms** | **3,02 s** | **15,3×** |
| Negamax (α-β) | 6 | probabil. | 6,30 ms | 2,64 s | 19,1× |
| Negamax (bez α-β) | 6 | probabil. | 120,63 ms | 55,97 s | — (bazowy) |
| SSS* | 6 | probabil. | 7,48 ms | 3,47 s | 16,1× |

### 4.4 Analiza czasów

**Wpływ alpha-beta pruning:**
- Przy głębokości 2 różnica ~2× — drzewo jest płytkie, mało do odcięcia.
- Przy głębokości 6 **Negamax z α-β jest ~21× szybszy** niż bez (4,84 ms vs 102,84 ms). Alpha-beta eliminuje ogromną większość gałęzi.

**Negamax (α-β) vs SSS\*:**
- SSS* jest ~30–40% wolniejszy niż Negamax z α-β (6,72 ms vs 4,84 ms przy gł. 6). Narzut wynika z dodatkowej złożoności pamięciowej algorytmu SSS*.
- Przy małych grach jak TTT SSS* nie daje przewagi. Mógłby się wyróżnić w grach z większym drzewem.

**Wariant probabilistyczny vs deterministyczny:**
- Czasy nieznacznie dłuższe w probabilistycznym — partie mają więcej ruchów (fail-e wydłużają grę).

---

## 5. Napotkane problemy

### 5.1 Losowanie w symulacjach Negamax

Negamax wywołuje `make_move()` setki razy przy eksploracji drzewa. Gdy 20% fail stosowane było do każdego wywołania, AI podejmowało błędne decyzje (stan gry po symulacji nie odpowiadał zamierzonemu).

**Rozwiązanie:** Flaga `_apply_failure` ustawiana na `True` wyłącznie przed faktycznym ruchem w pętli gry. Symulacje AI działają deterministycznie.

### 5.2 Kompatybilność wersji easyAI

Starsze wersje easyAI używają `nplayer`/`nopponent`, nowsze `current_player`/`opponent_index`. Implementacja dopasowana do zainstalowanej wersji (v2.x).

### 5.3 Alternacja gracza rozpoczynającego

Obaj gracze AI używają identycznego algorytmu. Wymiana kolejności co partię zapewnia, że asymetria wyniku wynika z przewagi pierwszego ruchu (lub losowości), nie z różnic w AI.

---

## 6. Struktura plików

```
Project1/
├── EasyAI.pdf                      # Treść zadania
├── raport.md                       # Ten raport
├── Part1_4_points/
│   ├── tictac.py                   # Gra Tic-tac-doh
│   ├── experiment.py               # Eksperyment Part 1 (Negamax, 2 głębokości)
│   └── experiment_results.csv      # Wyniki Part 1
└── Part2_6_points/
    ├── tictac.py                   # Gra Tic-tac-doh (kopia)
    ├── negamax_no_ab.py            # Negamax bez alpha-beta (własna impl.)
    ├── experiment.py               # Eksperyment Part 2 (3 algorytmy, czasy)
    └── experiment_results.csv      # Wyniki Part 2
```

**Uruchomienie:**
```bash
pip install easyAI
cd Part1_4_points && python experiment.py        # domyślnie 100 partii
cd Part2_6_points && python experiment.py 50     # 50 partii
```

---

## 7. Podsumowanie

| Wniosek | Szczegóły |
|---------|-----------|
| Deterministyczne TTT = remis | Przy optymalnej grze (gł. ≥ 4) AI zawsze remisuje |
| Losowość zmienia wyniki | 20% fail generuje wygrane/przegrane, gracz 1 ma statystyczną przewagę |
| α-β pruning przyspiesza ~21× | Przy gł. 6: 4,84 ms vs 102,84 ms na ruch |
| SSS* porównywalny z α-β | Minimalnie wolniejszy (~30%), identyczne wyniki |
| Głębsza analiza = więcej remisów | AI z gł. 6 broni lepiej niż z gł. 2 w wariancie probabilistycznym |
| ~18% ruchów nieudanych | Zgodne z oczekiwanymi 20% (wariancja statystyczna) |
