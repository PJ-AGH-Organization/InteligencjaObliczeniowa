# Reinforcement Learning — Teoria

## Spis treści

1. [Formalny model — MDP](#1-formalny-model--mdp)
2. [Return i dyskontowanie](#2-return-i-dyskontowanie)
3. [Funkcje wartości — V i Q](#3-funkcje-wartości--v-i-q)
4. [Równanie Bellmana](#4-równanie-bellmana)
5. [Polityka (Policy)](#5-polityka-policy)
6. [Eksploracja vs eksploatacja](#6-eksploracja-vs-eksploatacja)
7. [Taksonomia algorytmów RL](#7-taksonomia-algorytmów-rl)
8. [Value-based — DQN](#8-value-based--dqn)
9. [Policy Gradient — REINFORCE](#9-policy-gradient--reinforce)
10. [Actor-Critic](#10-actor-critic)
11. [On-policy vs Off-policy](#11-on-policy-vs-off-policy)
12. [Replay Buffer](#12-replay-buffer)
13. [Target Network](#13-target-network)
14. [Soft Actor-Critic (SAC)](#14-soft-actor-critic-sac)
15. [Kształtowanie nagrody (Reward Shaping)](#15-kształtowanie-nagrody-reward-shaping)
16. [Model-based vs Model-free](#16-model-based-vs-model-free)
17. [Zbieżność i stabilność uczenia](#17-zbieżność-i-stabilność-uczenia)
18. [Mapa pojęć — podsumowanie](#18-mapa-pojęć--podsumowanie)

---

## 1. Formalny model — MDP

Reinforcement Learning opiera się na formaliźmie **Markowskiego Procesu Decyzyjnego** (Markov Decision Process, MDP), opisywanego krotką:

```
MDP = (S, A, P, R, γ)
```

| Symbol | Nazwa | Opis |
|---|---|---|
| `S` | Przestrzeń stanów | Zbiór wszystkich możliwych stanów środowiska |
| `A` | Przestrzeń akcji | Zbiór wszystkich możliwych akcji agenta |
| `P(s'│s, a)` | Funkcja przejścia | Prawdopodobieństwo trafienia w stan `s'` po wykonaniu `a` w stanie `s` |
| `R(s, a, s')` | Funkcja nagrody | Natychmiastowa nagroda za przejście |
| `γ` | Współczynnik dyskontowania | `γ ∈ [0, 1)` — waga przyszłych nagród |

**Własność Markowa** — kluczowe założenie: następny stan zależy wyłącznie od bieżącego stanu i akcji, nie od historii:

```
P(s_{t+1} | s_t, a_t, s_{t-1}, a_{t-1}, ...) = P(s_{t+1} | s_t, a_t)
```

W praktyce własność Markowa jest często naruszona (np. gdy obserwacja jest niekompletna — agent widzi tylko część stanu). W Rolling Ball Navigator pozycja i prędkość kulki są w pełni zawarte w obserwacji, więc MDP jest spełnione.

Pętla interakcji:

```
s₀ → [Agent] → a₀ → [Środowisko] → (r₀, s₁)
s₁ → [Agent] → a₁ → [Środowisko] → (r₁, s₂)
...
```

---

## 2. Return i dyskontowanie

**Return** (skumulowana nagroda) to suma nagród od kroku `t` do końca epizodu:

```
G_t = r_t + γ·r_{t+1} + γ²·r_{t+2} + ... = Σ_{k=0}^{∞} γᵏ · r_{t+k}
```

**Współczynnik dyskontowania γ** kontroluje horyzont czasowy agenta:

| Wartość γ | Interpretacja |
|---|---|
| `γ = 0` | Agent myśli tylko o natychmiastowej nagrodzie — krótkowzroczny |
| `γ = 0.99` | Nagroda za 100 kroków warta `0.99^100 ≈ 0.37` obecnej | 
| `γ = 1.0` | Agent traktuje wszystkie przyszłe nagrody równo — może nie zbiegać |

W projekcie `γ = 0.99`, a `MAX_STEPS = 500`. Nagroda terminalna `+50` udzielona w kroku 123 (średnia) jest warta z perspektywy kroku 0:

```
0.99^123 · 50 ≈ 0.29 · 50 ≈ 14.5
```

To nadal duży sygnał — agent jest silnie motywowany do dotarcia do celu.

**Dlaczego nie γ = 1.0?** Przy nieskończonych horyzontach suma nagród mogłaby nie zbiegać. Dyskontowanie gwarantuje skończoność `G_t` i promuje szybkie rozwiązania.

---

## 3. Funkcje wartości — V i Q

### Funkcja wartości stanu V(s)

```
V^π(s) = E_π[ G_t | s_t = s ] = E_π[ r_t + γ·r_{t+1} + γ²·r_{t+2} + ... | s_t = s ]
```

„Jeśli jestem w stanie `s` i stosuję politykę `π` — ile sumarycznej nagrody się spodziewam?"

### Funkcja wartości akcji Q(s, a)

```
Q^π(s, a) = E_π[ G_t | s_t = s, a_t = a ]
```

„Jeśli jestem w stanie `s`, **najpierw wykonam akcję `a`**, a potem stosuję politykę `π` — ile sumarycznej nagrody się spodziewam?"

### Związek między V i Q

```
V^π(s) = Σ_a π(a|s) · Q^π(s, a)          (dyskretne akcje)
V^π(s) = E_{a~π} [ Q^π(s, a) ]            (ciągłe akcje)
```

V jest uśrednionym Q po wszystkich akcjach ważonych polityką.

### Optymalne funkcje wartości

Cel RL: znaleźć politykę `π*` maksymalizującą `V^π(s)` dla każdego stanu.

```
Q*(s, a) = max_π Q^π(s, a)
π*(s)    = argmax_a Q*(s, a)   (dyskretne akcje)
```

Znając `Q*`, natychmiast znamy optymalną politykę — wystarczy w każdym stanie wybrać akcję o najwyższym Q.

---

## 4. Równanie Bellmana

Równanie Bellmana to **rekurencyjna** definicja Q-funkcji — łączy wartość bieżącego przejścia z wartością następnego stanu:

```
Q^π(s, a) = E[ r + γ · Q^π(s', π(s')) ]
```

Dla optymalnej polityki (równanie Bellmana optymalności):

```
Q*(s, a) = E[ r + γ · max_{a'} Q*(s', a') ]
```

To równanie jest podstawą większości algorytmów RL — sieć Q uczy się tak, żeby **lewa i prawa strona były sobie równe**.

**Błąd Bellmana (TD error):**

```
δ = r + γ · Q(s', a') - Q(s, a)
```

Algorytm minimalizuje `δ²` — to jest funkcja straty Critica.

- `δ > 0` → Q(s,a) zaniżone → zwiększ
- `δ < 0` → Q(s,a) zawyżone → zmniejsz

---

## 5. Polityka (Policy)

Polityka `π` to funkcja mapująca stan na akcję — to „mózg" agenta, jedyna rzecz potrzebna do działania po zakończeniu treningu.

### Deterministyczna

```
a = π(s)
```

Jeden stan → jedna akcja. Prosta, ale nie eksploruje.

### Stochastyczna

```
a ~ π(·|s)
```

Jeden stan → rozkład prawdopodobieństwa nad akcjami. Akcja jest **próbkowana** z tego rozkładu.

**Co to znaczy próbkować?** Wyobraź sobie że polityka mówi: „w tym stanie najlepiej jechać w prawo (70%), ale może też w lewo (30%)." Próbkowanie to jeden losowy rzut zgodny z tym rozkładem — raz wyjdzie prawo, innym razem lewo. Nie jest to błąd ani szum — to **zamierzona losowość** umożliwiająca eksplorację.

W SAC rozkład jest Gaussowski:

```
π(·|s) = N(μ_θ(s), σ_θ(s))
```

Actor (sieć neuronowa z parametrami `θ`) zwraca `μ` i `σ`. Akcja:

```
ε ~ N(0, 1)                    # losowanie standardowe
a = tanh(μ + σ · ε)            # reparametryzacja + obcięcie do [-1,1]
```

**Trick reparametryzacji** pozwala liczyć gradienty przez operację próbkowania — bez niego nie można by trenować sieci backpropagation przez losową operację.

### Polityka a Critic

Polityka = Actor. Critic to narzędzie treningowe, nie część polityki. Po treningu do działania wystarczy Actor.

```
Polityka (Actor)  →  działa w środowisku
Critic (Q-sieć)   →  ocenia Actora podczas treningu, potem zbędny
```

---

## 6. Eksploracja vs eksploatacja

Fundamentalny dylemat RL:

- **Eksploatacja** — rób to co już wiesz że działa (wysoka natychmiastowa nagroda)
- **Eksploracja** — próbuj nowych rzeczy (może znajdziesz coś lepszego)

Za dużo eksploatacji → utknięcie w lokalnym optimum.
Za dużo eksploracji → nigdy nie korzystasz z tego czego się nauczyłeś.

### Metody eksploracji

**ε-greedy** (DQN): z prawdopodobieństwem `ε` wykonaj losową akcję, z `1-ε` najlepszą. `ε` maleje z czasem.

**Szum Ornsteina-Uhlenbecka / Gaussowski** (DDPG, TD3): dodaj szum do deterministycznej akcji:
```
a = π(s) + N(0, σ)
```

**Entropia polityki** (SAC): nie dodaje szumu zewnętrznie — zamiast tego **nagradza politykę za różnorodność akcji**. Polityka sama w sobie jest stochastyczna i uczy się pozostawać entropiczną.

SAC maksymalizuje:

```
J(π) = E[ Σ_t r_t + α · H(π(·|s_t)) ]
```

Gdzie `H(π) = -E[log π(a|s)]` to entropia polityki, a `α` to waga entropii (`ent_coef = 0.1` w projekcie). To eleganckie rozwiązanie — eksploracja jest wbudowana w cel uczenia, nie dodana z zewnątrz.

---

## 7. Taksonomia algorytmów RL

```
Reinforcement Learning
│
├── Model-free (nie uczą modelu środowiska)
│   │
│   ├── Value-based (uczą tylko Q-funkcji, polityka implicite)
│   │   └── DQN, Double DQN, Dueling DQN, Rainbow
│   │       → tylko dyskretne przestrzenie akcji
│   │
│   ├── Policy-based (uczą tylko polityki, bez Q-funkcji)
│   │   └── REINFORCE
│   │       → wysokie wariancja gradientów
│   │
│   └── Actor-Critic (uczą i polityki i Q-funkcji)
│       ├── On-policy:  A2C, A3C, PPO
│       └── Off-policy: DDPG, TD3, SAC  ← nasz projekt
│
└── Model-based (uczą modelu P(s'|s,a), planują w nim)
    └── Dreamer, MBPO, AlphaZero
        → wymagają mniej danych, ale model może być błędny
```

---

## 8. Value-based — DQN

DQN (Deep Q-Network) aproksymuje `Q*(s, a)` siecią neuronową. Polityka jest implicite:

```
π(s) = argmax_a Q(s, a)
```

**Dlaczego nie działa przy ciągłych akcjach?** `argmax` wymaga sprawdzenia Q dla każdej możliwej akcji — przy ciągłej przestrzeni jest ich nieskończenie wiele.

Innowacje DQN względem klasycznego Q-learningu:

| Technika | Opis |
|---|---|
| Replay buffer | Łamie korelacje między kolejnymi przejściami |
| Target network | Stabilizuje cele uczenia (zamrożona kopia Q-sieci) |
| Sieć neuronowa | Aproksymacja Q zamiast tablicy (skalowalność) |

---

## 9. Policy Gradient — REINFORCE

Zamiast uczyć Q-funkcji, bezpośrednio optymalizuje parametry polityki `θ` przez gradient:

```
∇_θ J(θ) = E_π [ G_t · ∇_θ log π_θ(a_t | s_t) ]
```

Intuicja: jeśli epizod dał wysoką nagrodę `G_t`, zwiększ prawdopodobieństwo wykonanych akcji. Jeśli niską — zmniejsz.

**Problem:** `G_t` ma bardzo wysoką wariancję — wynik jednego epizodu zależy od wielu losowych zdarzeń. Uczenie jest powolne i niestabilne.

**Rozwiązanie:** odejmij **baseline** (często `V(s)`) od `G_t`:

```
∇_θ J(θ) = E_π [ (G_t - V(s_t)) · ∇_θ log π_θ(a_t | s_t) ]
```

`G_t - V(s_t)` to **Advantage** — o ile lepsza była faktyczna nagroda od oczekiwanej. To prowadzi do architektury Actor-Critic.

---

## 10. Actor-Critic

Łączy policy gradient (Actor) z aproksymacją funkcji wartości (Critic):

```
Actor   π_θ(a|s)     — polityka, odpowiada „co robić"
Critic  V_φ(s)       — ocenia stany, odpowiada „jak dobrze mi idzie"
```

**Advantage Function:**

```
A(s, a) = Q(s, a) - V(s)
```

„O ile lepsza jest ta konkretna akcja od średniej akcji w tym stanie?"

- `A > 0` → ta akcja lepsza niż przeciętna → zwiększ jej prawdopodobieństwo
- `A < 0` → ta akcja gorsza → zmniejsz

Zamiast liczyć `A` wprost, używa się **TD error** jako jego estymatora:

```
A(s_t, a_t) ≈ r_t + γ·V(s_{t+1}) - V(s_t)
```

### PPO (Proximal Policy Optimization) — on-policy Actor-Critic

Popularna alternatywa dla SAC przy ciągłych akcjach. Kluczowa różnica: **ogranicza jak bardzo polityka może zmienić się w jednym kroku** (clipped surrogate objective), co zapobiega destruktywnym aktualizacjom:

```
L_CLIP = E[ min(r_t · A_t,  clip(r_t, 1-ε, 1+ε) · A_t) ]
```

Gdzie `r_t = π_new(a|s) / π_old(a|s)` — stosunek prawdopodobieństw.

PPO jest on-policy — po aktualizacji dane są wyrzucane. Mniej efektywne próbkowo niż SAC, ale stabilniejsze i prostsze w tuningu.

---

## 11. On-policy vs Off-policy

| | On-policy | Off-policy |
|---|---|---|
| Dane do uczenia | tylko z **aktualnej** polityki | z **dowolnej** polityki (np. starszej) |
| Po aktualizacji dane | wyrzucane | zostają w replay buffer |
| Efektywność próbkowania | niska — każde przejście użyte 1× | wysoka — przejście używane wielokrotnie |
| Stabilność | wyższa — dane zawsze aktualne | wymaga target network |
| Przykłady | REINFORCE, A2C, PPO | DQN, DDPG, TD3, SAC |
| Kiedy używać | gry, symulacje gdzie dane tanie | robotyka, środowiska gdzie dane drogie |

**Dlaczego off-policy może uczyć się ze starych danych?**

Q-learning i SAC uczą się relacji `Q(s,a) = r + γ·Q(s',a')` — ta relacja jest prawdziwa niezależnie od tego jakiej polityki używano do zebrania `(s, a, r, s')`. Metody policy gradient (on-policy) nie mają tej właściwości — gradient musi być liczony względem aktualnej polityki.

---

## 12. Replay Buffer

Kolejka (FIFO) przechowująca przejścia `(s, a, r, s', done)`:

```
krok → (s, a, r, s', done) → [  bufor 300 000 wpisów  ] → losowy batch 256
```

**Dlaczego losowy batch, nie sekwencyjny?**

Kolejne kroki są silnie skorelowane — `s₁ → s₂ → s₃` to kulka poruszająca się płynnie. Uczenie na takich sekwencjach powoduje, że sieć „kręci się" wokół jednego fragmentu przestrzeni stanów i zapomina resztę (catastrophic forgetting). Losowanie łamie te korelacje.

**Prioritized Experience Replay (PER)** — rozszerzenie: przejścia z dużym błędem Bellmana (`δ`) są próbkowane częściej, bo agent ma się na nich więcej do nauczenia. Nie używane w projekcie, ale popularne w praktyce.

**Kiedy bufor jest pełny?** Najstarsze wpisy są nadpisywane. Bufor 300 000 przy epizodach ~123 kroków mieści ~2 400 epizodów — wystarczająco dużo by sieć widziała różnorodne sytuacje.

---

## 13. Target Network

**Problem:** Q-sieć ucząca się z własnych przewidywań jako „prawdy" powoduje niestabilność — błędy się nakręcają (moving target problem).

Cel uczenia:

```
y = r + γ · Q_θ(s', a')       ← Q_θ ciągle się zmienia → niestabilne
```

**Rozwiązanie:** osobna, zamrożona kopia Q-sieci aktualizowana bardzo powoli:

```
y = r + γ · Q_θ_target(s', a')
```

**Twarda aktualizacja** (DQN): co `N` kroków skopiuj wagi: `θ_target ← θ`

**Miękka aktualizacja** (SAC, TD3): co krok przesuń wagi o mały krok:

```
θ_target ← (1 - τ) · θ_target  +  τ · θ
```

Przy `τ = 0.005` (jak w projekcie) target network „dogania" aktualną sieć w ciągu ~200 kroków. Zapewnia stabilne cele uczenia przez cały czas.

---

## 14. Soft Actor-Critic (SAC)

SAC to off-policy Actor-Critic z **entropijną regularyzacją** polityki. Maksymalizuje:

```
J(π) = Σ_t E[ r_t + α · H(π(·|s_t)) ]
```

### Architektura

```
Actor    π_θ(a|s)            MLP: obs → (μ, σ) → akcja przez tanh
Critic 1 Q_φ₁(s, a)          MLP: [obs, akcja] → Q-wartość
Critic 2 Q_φ₂(s, a)          MLP: [obs, akcja] → Q-wartość  (podwójny Critic)
Target 1 Q_φ₁_target(s, a)   zamrożona kopia Critica 1
Target 2 Q_φ₂_target(s, a)   zamrożona kopia Critica 2
```

**Podwójny Critic (Double Q-learning):** używamy `min(Q₁, Q₂)` do obliczania celów. Zapobiega **overestimation bias** — tendencji Q-sieci do zawyżania wartości, co prowadzi do nieoptymalnych polityk.

### Aktualizacje

**Critic (minimalizacja błędu Bellmana):**

```
y   = r + γ · (min(Q₁_target, Q₂_target)(s', ã') - α · log π(ã'|s'))
                                                    ↑
                                            człon entropii w celu
ã' ~ π(·|s')

L = E[ (Q₁(s,a) - y)² + (Q₂(s,a) - y)² ]
```

**Actor (maksymalizacja Q + entropia):**

```
L_Actor = E[ α · log π(ã|s) - min(Q₁, Q₂)(s, ã) ]
ã ~ π(·|s)     ← reparametryzacja: ã = tanh(μ + σ·ε)
```

**Automatyczne dostrajanie α** (domyślne w SAC):

```
L_α = E[ -α · (log π(a|s) + H_target) ]
```

`H_target` to pożądana entropia (zwykle `-dim(A)`). `α` rośnie gdy polityka jest zbyt deterministyczna, maleje gdy zbyt losowa. W projekcie wyłączone (`ent_coef=0.1` stały) dla stabilności.

**Miękka aktualizacja target networks:**

```
θ_target_i ← (1-τ)·θ_target_i + τ·θ_i,   τ = 0.005
```

### Schemat jednego kroku uczenia (po learning_starts)

```
1. Wylosuj batch (s, a, r, s', done) z bufora
2. ã' = Actor(s') + reparametryzacja           (próbkowanie z polityki)
3. y  = r + γ · (min Q_target(s', ã') - α·log π(ã'|s'))
4. Zaktualizuj Critic 1 i 2: min (Q_i - y)²
5. ã  = Actor(s) + reparametryzacja
6. Zaktualizuj Actor: min (α·log π(ã|s) - min Q(s, ã))
7. Miękka aktualizacja target networks
```

---

## 15. Kształtowanie nagrody (Reward Shaping)

Wiele środowisk ma **rzadkie nagrody** — agent dostaje sygnał dopiero po dotarciu do celu (lub nie dostaje wcale przez długi czas). Uczenie z rzadkich nagród jest bardzo trudne — agent musi trafić na nagrodę przez przypadek zanim zacznie się jej uczyć.

**Reward Shaping** dodaje gęste pośrednie nagrody prowadzące agenta w kierunku celu:

```
r_shaped(s, a, s') = r(s, a, s') + F(s, s')
```

**Potential-based shaping** — bezpieczna forma shapingu (nie zmienia optymalnej polityki):

```
F(s, s') = γ · Φ(s') - Φ(s)
```

Gdzie `Φ(s)` to dowolna funkcja potencjału (np. ujemna odległość do celu).

W projekcie:

```
reward = -0.01 + 0.02 · (prev_dist - dist)
```

Człon `0.02 · (prev_dist - dist)` to dokładnie potential-based shaping z `Φ(s) = -0.02 · dist(s)`:

```
F = γ · Φ(s') - Φ(s) ≈ Φ(s') - Φ(s) = -0.02·dist' - (-0.02·dist) = 0.02·(dist - dist')
```

(przy `γ ≈ 1` dla jednego kroku). Gwarantuje to że optymalna polityka bez shapingu jest nadal optymalna po shapingu.

**Kara czasowa** (`-0.01` co krok) zapobiega „lenistwu" — agentowi który mógłby zbierać nagrody kształtujące kręcąc się w kółko wokół celu bez wchodzenia do niego.

---

## 16. Model-based vs Model-free

| | Model-free | Model-based |
|---|---|---|
| Co się uczy | polityki / Q-funkcji bezpośrednio | modelu środowiska P(s'\|s,a) |
| Efektywność próbkowania | niska — potrzeba dużo danych | wysoka — planuje w modelu |
| Ryzyko | brak | błędy modelu → błędna polityka |
| Przykłady | SAC, PPO, DQN | Dreamer, MBPO, AlphaZero |
| Kiedy | środowiska szybkie (symulacje) | robotyka, środowiska kosztowne |

**Model** w RL to nie model ML — to aproksymacja funkcji przejścia środowiska `P(s'|s,a)`. Mając model, agent może **planować** (wyobrażać sobie przyszłość) bez interakcji ze środowiskiem.

AlphaZero (szachy, Go) to hybryda: model gry (zasady) + MCTS (planowanie) + sieć wartości i polityki.

---

## 17. Zbieżność i stabilność uczenia

### Typowe problemy

**Catastrophic forgetting:** sieć uczy się nowych sytuacji i „zapomina" stare. Replay buffer łagodzi to przez mieszanie danych ze wszystkich etapów uczenia.

**Overestimation bias:** Q-sieci mają tendencję do zawyżania wartości przez `max` operację. Podwójny Critic (`min(Q₁, Q₂)`) i Double Q-learning to redukują.

**Moving target problem:** uczysz sieć wobec celów generowanych przez tę samą sieć — cele się ruszają wraz z siecią. Target network zamraża cele.

**Exploding/vanishing gradients:** duże sieci mogą mieć niestabilne gradienty. Gradient clipping i normalizacja wejść pomagają.

**High variance gradients:** szczególnie w metodach policy gradient. Baseline (Advantage) i duże batche redukują wariancję.

### Wskaźniki zbieżności

- Rosnąca i stabilizująca się krzywa nagrody ewaluacyjnej
- Malejący błąd Bellmana (TD error)
- Malejąca entropia polityki (agent staje się bardziej deterministyczny)
- Stabilna wartość `α` przy auto-tuningu entropii

### Hiperparametry krytyczne dla stabilności SAC

| Hiperparametr | Zbyt mały | Zbyt duży |
|---|---|---|
| `learning_rate` | wolne uczenie | dywergencja |
| `batch_size` | wysoka wariancja | kosztowne obliczeniowo |
| `buffer_size` | za stare dane za szybko | bez negatywnych efektów |
| `τ` (soft update) | target network nie nadąża | niestabilne cele |
| `ent_coef α` | za deterministyczny, utknięcie | za losowy, nie uczy się |
| `γ` | krótkowzroczność | niestabilność numeryczna |

---

## 18. Mapa pojęć — podsumowanie

```
┌─────────────────────────────────────────────────────────────────┐
│                    Reinforcement Learning                        │
│                                                                  │
│  MDP: (S, A, P, R, γ)                                           │
│   │                                                              │
│   ├── Return G_t = Σ γᵏ·r_{t+k}                                │
│   │                                                              │
│   ├── Funkcje wartości                                           │
│   │    ├── V(s)    — wartość stanu                              │
│   │    └── Q(s,a)  — wartość akcji w stanie                    │
│   │         └── Równanie Bellmana: Q = r + γ·Q(s',a')          │
│   │                                                              │
│   └── Polityka π(a|s) ← TO jest cel uczenia                    │
│        ├── deterministyczna: a = π(s)                           │
│        └── stochastyczna:    a ~ π(·|s) = N(μ,σ)               │
│                                                                  │
│  Algorytmy                                                       │
│   ├── Value-based (DQN): uczy Q → π implicite                   │
│   ├── Policy Gradient (REINFORCE): uczy π wprost               │
│   └── Actor-Critic (SAC, PPO): uczy i π i Q                    │
│        ├── Actor  = polityka π_θ   → działa w środowisku        │
│        └── Critic = Q-sieć Q_φ    → ocenia Actora, potem zbędny│
│                                                                  │
│  Techniki stabilizacji                                           │
│   ├── Replay Buffer      — łamie korelacje, off-policy          │
│   ├── Target Network     — stabilne cele uczenia                │
│   ├── Double Q-learning  — redukuje overestimation             │
│   └── Entropia polityki  — eksploracja bez szumu zewnętrznego   │
│                                                                  │
│  SAC = Actor-Critic + off-policy + entropia + podwójny Critic   │
└─────────────────────────────────────────────────────────────────┘
```
