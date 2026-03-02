#!/usr/bin/env python3
"""
Eksperyment: AI vs AI w Tic-Tac-Toe / Tic-tac-doh.
- Wielokrotne rozgrywki z wymianą gracza rozpoczynającego
- Porównanie dwóch głębokości Negamax
- Wariant deterministyczny vs probabilistyczny (20% nieudanych ruchów)
"""

import random
from collections import defaultdict
from easyAI import AI_Player, Negamax

from tictac import TicTacDoh


def run_single_game(players, probabilistic, verbose=False):
    """Jedna rozgrywka. Zwraca (winner, total_moves, moves_failed)."""
    game = TicTacDoh(players, probabilistic=probabilistic)
    game.play(nmoves=100, verbose=verbose)
    winner = game.get_winner()
    return winner, game.total_moves, game.moves_failed


def run_experiment(n_games, depth, probabilistic, verbose=False):
    """
    Uruchamia n_games partii. Gracze zamieniają się kolorem co partię.
    Zwraca: {1: wins, 2: wins, 0: draws}, total_moves, moves_failed_total
    """
    ai_algo = Negamax(depth)
    results = defaultdict(int)
    total_moves_sum = 0
    moves_failed_total = 0

    for i in range(n_games):
        # Zamiana gracza rozpoczynającego: parzyste = gracz 1 startuje, nieparzyste = gracz 2
        if i % 2 == 0:
            players = [AI_Player(ai_algo), AI_Player(ai_algo)]
        else:
            players = [AI_Player(ai_algo), AI_Player(ai_algo)]
            players = [players[1], players[0]]

        winner, total_moves, moves_failed = run_single_game(players, probabilistic, verbose)
        results[winner] += 1
        total_moves_sum += total_moves
        moves_failed_total += moves_failed

    return dict(results), total_moves_sum, moves_failed_total


def main():
    import sys
    N_GAMES = int(sys.argv[1]) if len(sys.argv) > 1 else 100  # np. python experiment.py 50
    DEPTHS = [4, 8]  # dwie głębokości do porównania

    print("=" * 70)
    print("EKSPERYMENT: AI vs AI - Tic-Tac-Toe / Tic-tac-doh")
    print("=" * 70)
    print(f"Partie na konfigurację: {N_GAMES}")
    print(f"Głębokości Negamax: {DEPTHS}")
    print()

    all_results = []

    for depth in DEPTHS:
        print(f"\n--- Głębokość Negamax = {depth} ---")
        for probabilistic, variant_name in [(False, "Deterministyczny (klasyczne TTT)"), (True, "Probabilistyczny (Tic-tac-doh, 20% failure)")]:
            print(f"\n  {variant_name}:")
            random.seed(42)
            results, total_moves, moves_failed = run_experiment(N_GAMES, depth, probabilistic)
            wins_1 = results.get(1, 0)
            wins_2 = results.get(2, 0)
            draws = results.get(0, 0)
            print(f"    Gracz 1: {wins_1} wygranych")
            print(f"    Gracz 2: {wins_2} wygranych")
            print(f"    Remisy:  {draws}")
            print(f"    Łącznie ruchów: {total_moves}")
            if probabilistic and total_moves > 0:
                pct = 100 * moves_failed / total_moves
                print(f"    Nieudane ruchy: {moves_failed} ({pct:.1f}%)")

            all_results.append({
                "depth": depth,
                "variant": variant_name,
                "probabilistic": probabilistic,
                "wins_1": wins_1,
                "wins_2": wins_2,
                "draws": draws,
                "total_moves": total_moves,
                "moves_failed": moves_failed if probabilistic else 0,
            })

    # Zapis wyników do pliku
    with open("experiment_results.txt", "w", encoding="utf-8") as f:
        f.write("Wyniki eksperymentów AI vs AI\n")
        f.write("=" * 50 + "\n")
        for r in all_results:
            f.write(f"\nGłębokość={r['depth']}, {r['variant']}\n")
            f.write(f"  Gracz 1: {r['wins_1']}  Gracz 2: {r['wins_2']}  Remisy: {r['draws']}\n")
            f.write(f"  Łącznie ruchów: {r['total_moves']}\n")
            if r["probabilistic"] and r["total_moves"] > 0:
                pct = 100 * r["moves_failed"] / r["total_moves"]
                f.write(f"  Nieudane ruchy: {r['moves_failed']} ({pct:.1f}%)\n")

    print("\n" + "=" * 70)
    print("Wyniki zapisane do experiment_results.txt")
    print("=" * 70)


if __name__ == "__main__":
    main()
