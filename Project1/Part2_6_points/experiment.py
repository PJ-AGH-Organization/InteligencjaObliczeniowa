#!/usr/bin/env python3
"""
Eksperyment Part 2 (6 pkt): porównanie algorytmów AI na Tic-Tac-Toe / Tic-tac-doh.

Porównywane algorytmy:
  1. Negamax z alpha-beta pruning (easyAI)
  2. Negamax BEZ alpha-beta pruning (własna impl.)
  3. SSS* (easyAI)

Dwie głębokości (2, 6), dwa warianty gry (deterministyczny, probabilistyczny).
Pomiar średniego czasu wyboru ruchu dla każdego AI.
"""

import csv
import random
import sys
import time
from collections import defaultdict
from copy import deepcopy

from easyAI import AI_Player, Negamax
from easyAI.AI.SSS import SSS

from negamax_no_ab import NegamaxNoAB
from tictac import TicTacDoh


def run_single_game(players, probabilistic, verbose=False):
    """
    Jedna rozgrywka z pomiarem czasu.
    Zwraca (winner, total_moves, moves_failed, move_times_by_player).
    move_times_by_player = {1: [list of times], 2: [list of times]}
    """
    game = TicTacDoh(players, probabilistic=probabilistic)

    history = []
    move_times = {1: [], 2: []}

    if verbose:
        game.show()

    for game.nmove in range(1, 100):
        if game.is_over():
            break

        t0 = time.perf_counter()
        move = game.player.ask_move(game)
        elapsed = time.perf_counter() - t0
        move_times[game.current_player].append(elapsed)

        history.append((deepcopy(game), move))

        game._apply_failure = True
        try:
            game.make_move(move)
        finally:
            game._apply_failure = False
        game.total_moves += 1

        if verbose:
            failed_suffix = " (FAILED)" if game.last_move_failed else ""
            print(
                "\nMove #%d: player %d plays %s%s :"
                % (game.nmove, game.current_player, str(move), failed_suffix)
            )
            game.show()

        game.switch_player()

    winner = game.get_winner()
    return winner, game.total_moves, game.moves_failed, move_times


def run_experiment(n_games, algo_factory, probabilistic):
    """
    Uruchamia n_games partii. Gracze zamieniają się kolorem co partię.
    algo_factory: callable() -> algo_instance (tworzony na nowo per partia)
    Zwraca: results_dict, total_moves, moves_failed, all_move_times_flat
    """
    results = defaultdict(int)
    total_moves_sum = 0
    moves_failed_total = 0
    all_times = []

    for i in range(n_games):
        algo1 = algo_factory()
        algo2 = algo_factory()
        if i % 2 == 0:
            players = [AI_Player(algo1), AI_Player(algo2)]
        else:
            players = [AI_Player(algo2), AI_Player(algo1)]

        winner, total_moves, moves_failed, move_times = run_single_game(
            players, probabilistic
        )
        results[winner] += 1
        total_moves_sum += total_moves
        moves_failed_total += moves_failed
        all_times.extend(move_times[1])
        all_times.extend(move_times[2])

    return dict(results), total_moves_sum, moves_failed_total, all_times


def fmt_time(seconds):
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.0f} µs"
    if seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    return f"{seconds:.3f} s"


def main():
    N_GAMES = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    DEPTHS = [2, 6]

    algorithms = {
        "Negamax (α-β)": lambda d: Negamax(d),
        "Negamax (bez α-β)": lambda d: NegamaxNoAB(d),
        "SSS*": lambda d: SSS(d),
    }

    print("=" * 80)
    print("EKSPERYMENT Part 2: Porównanie algorytmów AI")
    print("=" * 80)
    print(f"Partie na konfigurację: {N_GAMES}")
    print(f"Głębokości: {DEPTHS}")
    print(f"Algorytmy: {', '.join(algorithms.keys())}")
    print()

    all_results = []

    for depth in DEPTHS:
        print(f"\n{'='*80}")
        print(f"  GŁĘBOKOŚĆ = {depth}")
        print(f"{'='*80}")

        for algo_name, algo_factory_fn in algorithms.items():
            factory = lambda _fn=algo_factory_fn, _d=depth: _fn(_d)

            for probabilistic, variant_name in [
                (False, "Deterministyczny"),
                (True, "Probabilistyczny (20% fail)"),
            ]:
                random.seed(42)
                results, total_moves, moves_failed, all_times = run_experiment(
                    N_GAMES, factory, probabilistic
                )

                wins_1 = results.get(1, 0)
                wins_2 = results.get(2, 0)
                draws = results.get(0, 0)
                avg_time = sum(all_times) / len(all_times) if all_times else 0
                total_time = sum(all_times)

                print(f"\n  {algo_name}, głęb.={depth}, {variant_name}:")
                print(f"    Gracz 1: {wins_1}  Gracz 2: {wins_2}  Remisy: {draws}")
                print(f"    Łącznie ruchów: {total_moves}")
                if probabilistic and total_moves > 0:
                    pct = 100 * moves_failed / total_moves
                    print(f"    Nieudane ruchy: {moves_failed} ({pct:.1f}%)")
                print(f"    Śr. czas/ruch: {fmt_time(avg_time)}  (łącznie: {fmt_time(total_time)})")

                all_results.append({
                    "algo": algo_name,
                    "depth": depth,
                    "variant": variant_name,
                    "probabilistic": probabilistic,
                    "wins_1": wins_1,
                    "wins_2": wins_2,
                    "draws": draws,
                    "total_moves": total_moves,
                    "moves_failed": moves_failed if probabilistic else 0,
                    "avg_time": avg_time,
                    "total_time": total_time,
                    "n_time_samples": len(all_times),
                })

    # Zapis CSV
    csv_file = "experiment_results.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "algorytm", "glebokosc", "wariant", "gracz1_wygrane", "gracz2_wygrane",
            "remisy", "lacznie_ruchow", "nieudane_ruchy", "procent_nieudanych",
            "sr_czas_ruch_s", "czas_laczny_s", "liczba_pomiarow"
        ])
        for r in all_results:
            pct = f"{100 * r['moves_failed'] / r['total_moves']:.1f}" if r["probabilistic"] and r["total_moves"] > 0 else ""
            writer.writerow([
                r["algo"], r["depth"], r["variant"],
                r["wins_1"], r["wins_2"], r["draws"],
                r["total_moves"],
                r["moves_failed"] if r["probabilistic"] else "",
                pct,
                f"{r['avg_time']:.6f}",
                f"{r['total_time']:.3f}",
                r["n_time_samples"],
            ])

    print(f"\n{'='*80}")
    print(f"Wyniki zapisane do {csv_file}")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
