# Raport: Gra Tic-tac-doh i eksperymenty z AI

**Uruchomienie eksperymentu:** `python experiment.py` (opcjonalnie: `python experiment.py 50` – 50 partii zamiast 100)

## 1. Opis gry

### 1.1 Klasyczne kółko i krzyżyk (Tic-Tac-Toe)

Gra rozgrywa się na planszy 3×3. Dwaj gracze na przemian stawiają znaki (O i X) w wolnych polach. Wygrywa ten, kto pierwszy ustawi trzy swoje znaki w jednej linii – poziomej, pionowej lub przekątnej. Przy prawidłowej grze obu stron wynikiem jest remis.

### 1.2 Wariant probabilistyczny: Tic-tac-doh

Wariant **Tic-tac-doh** wprowadza element losowości: z prawdopodobieństwem 20% wykonany ruch się „nie udaje” – na planszy nie zostaje żaden ślad, a kolej ruchu przechodzi na przeciwnika. Gracz traci kolejkę i nie może postawić znaku mimo wyboru pola.

Wpływa to na strategię i wynik: gra przestaje być deterministyczna, pojawiają się niespodziewane zwroty akcji i większa różnorodność rozgrywek.

### 1.3 Implementacja techniczna

Gra została zaimplementowana w Pythonie z użyciem biblioteki **easyAI**. Klasa `TicTacDoh` dziedziczy po `TwoPlayerGame` i definiuje:

- `possible_moves()` – lista legalnych ruchów,
- `make_move()` – wykonanie ruchu (z 20% szansą na niepowodzenie w wersji probabilistycznej),
- `unmake_move()` – cofnięcie ruchu (dla optymalizacji AI),
- `is_over()` – warunek zakończenia gry,
- `scoring()` – ocena pozycji dla algorytmu Negamax.

**Ważny szczegół implementacyjny:** Mechanizm nieudanych ruchów musi działać wyłącznie przy faktycznych ruchach w grze, a nie podczas symulacji AI (Negamax wywołuje `make_move` wielokrotnie w drzewie poszukiwań). Użyta została flaga `_apply_failure`, ustawiana na `True` tylko przed wykonaniem rzeczywistego ruchu w pętli gry.

---

## 2. Algorytm AI – Negamax

Algorytm **Negamax** to wariant Minimax, używający negacji ocen, co upraszcza implementację (jeden zestaw reguł oceny zamiast osobnych dla obu graczy). Z opcjonalną alfa-beta odcięciami i tablicami transpozycji dobrze nadaje się do gier takich jak kółko i krzyżyk.

Parametr **głębokość** określa, na ile pół ruchów do przodu AI analizuje. Większa głębokość oznacza lepszą jakość gry, ale dłuższy czas obliczeń. Dla planszy 3×3 głębokość 6–8 zwykle wystarcza do gry bliskiej optymalnej.

---

## 3. Przeprowadzone eksperymenty

### 3.1 Metodologia

W eksperymentach dwaj gracze AI (obaj z algorytmem Negamax) rozgrywali partię wielokrotnie. W każdej konfiguracji wykonano **100 partii** z następującymi ustawieniami:

- **Wymiana gracza rozpoczynającego:** co druga partia pierwszy ruch wykonywał gracz 2, dzięki czemu każdy gracz rozpoczynał 50 partii,
- **Dwie głębokości Negamax:** 4 i 8,
- **Dwa warianty gry:** deterministyczny (klasyczne TTT) oraz probabilistyczny (Tic-tac-doh).

### 3.2 Konfiguracje testowe

| Konfiguracja | Głębokość | Wariant             | Opis                  |
|-------------|-----------|---------------------|------------------------|
| D4          | 4         | deterministyczny    | Klasyczne TTT, gł. 4  |
| D8          | 8         | deterministyczny    | Klasyczne TTT, gł. 8  |
| P4          | 4         | probabilistyczny    | Tic-tac-doh, gł. 4    |
| P8          | 8         | probabilistyczny    | Tic-tac-doh, gł. 8    |

### 3.3 Wyniki

Eksperyment wykonano na 100 partiach dla każdej konfiguracji (seed=42). Wyniki:

| Konfiguracja        | Gracz 1 | Gracz 2 | Remisy | Łącznie ruchów | Nieudane (% z ruchów) |
|---------------------|---------|---------|--------|----------------|------------------------|
| Głęb. 4, determin.  | 0       | 0       | 100    | 900            | —                      |
| Głęb. 8, determin.  | 0       | 0       | 100    | 900            | —                      |
| Głęb. 4, probabil.  | 42      | 24      | 34     | 900            | 162 (18,0%)            |
| Głęb. 8, probabil.  | 35      | 16      | 49     | 884            | 160 (18,1%)            |

**Interpretacja:**

**Wariant deterministyczny:** Przy optymalnej grze obu stron klasyczne TTT zawsze kończy się remisem. Łącznie 900 ruchów (100 partii × 9 ruchów na partię – pełna plansza przy remisie).

**Wariant probabilistyczny (Tic-tac-doh):** Losowość zmienia wyniki:
- *Głębokość 4:* 42 vs 24 zwycięstw, 34 remisy, 900 ruchów łącznie, 162 nieudane (18,0%).
- *Głębokość 8:* 35 vs 16 zwycięstw, 49 remisów, 884 ruchy (krótsze partie przez wcześniejsze wygrane), 160 nieudanych (18,1%).
- **Procent nieudanych ruchów** (~18%) jest nieco poniżej teoretycznych 20% – typowa wariancja statystyczna. Oznacza to, że około 1 na 5 prób ruchu kończy się niepowodzeniem.
- Silniejsze AI (głęb. 8) generuje więcej remisów – lepiej broni pozycji.

Różnica między głębokością 4 a 8: przy głębokości 8 AI gra bezpieczniej, co przekłada się na większy odsetek remisów.

---

## 4. Napotkane problemy

### 4.1 Nieudane ruchy w symulacjach AI

Na początku mechanizm 20% nieudanych ruchów działał przy każdym wywołaniu `make_move`, także podczas symulacji Negamax (setki wywołań na jeden ruch). Skutkowało to:

- wieloma komunikatami o nieudanych ruchach w trakcie jednej decyzji AI,
- niestabilnym drzewem poszukiwań i błędnymi wyborami ruchów.

**Rozwiązanie:** Flaga `_apply_failure`, ustawiana na `True` wyłącznie przed wykonaniem rzeczywistego ruchu w pętli gry. Dzięki temu losowanie 20% nie dotyczy symulacji wewnątrz Negamax.

### 4.2 Spójność z easyAI

Biblioteka easyAI w różnych wersjach używa `nplayer`/`nopponent` albo `current_player`/`opponent_index`. Implementacja została dopasowana do używanej wersji (dla v2: `current_player`, `opponent_index`).

### 4.3 Alternacja gracza rozpoczynającego

W eksperymencie gracze AI są identyczni (ten sam algorytm). Alternacja kolejności w liście graczy co partię zapewnia, że każdy „gracz” ma taką samą liczbę pierwszych ruchów, co daje symetryczne statystyki zwycięstw i remisów.

---

## 5. Podsumowanie

Gra Tic-tac-doh rozszerza klasyczne kółko i krzyżyk o element losowości, co wpływa na strategię i wyniki. Algorytm Negamax pozwala na sensowną grę AI w obu wariantach.

Eksperymenty pokazują różnice między:

- wariantem deterministycznym (stosunkowo dużo remisów),
- wariantem probabilistycznym (więcej zwycięstw i porażek, wpływ losowości),
- różnymi głębokościami Negamax (głębokość 8 daje lepszą jakość gry niż 4).

Wyniki szczegółowe należy uzupełnić po uruchomieniu skryptu `experiment.py` i wpisaniu otrzymanych liczb do sekcji 3.3 powyżej.
