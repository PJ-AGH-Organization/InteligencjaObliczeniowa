#!/bin/bash

set -e  # Zatrzymaj przy błędzie

TIMEOUT=300  # 5 minut timeout

echo "=========================================="
echo "Małe problemy (5 bloków) - 4 punkty"
echo "=========================================="

echo ""
echo ">>> Problem 1-3, heurystyka mismatch"
uv run python -m Project2.blocksworld5_4_points --problem=all --heur=mismatch --viz

echo ""
echo ">>> Problem 1-3, bez heurystyki (zero)"
uv run python -m Project2.blocksworld5_4_points --problem=all --heur=zero --viz --timeout=$TIMEOUT

echo ""
echo "=========================================="
echo "Małe problemy z subgoals - 6 punktów"
echo "=========================================="

echo ""
echo ">>> Problem 1-3, subgoals + mismatch"
uv run python -m Project2.blocksworld5_4_points --problem=all --heur=mismatch --subgoals --viz

echo ""
echo ">>> Problem 1-3, subgoals + zero"
uv run python -m Project2.blocksworld5_4_points --problem=all --heur=zero --subgoals --viz --timeout=$TIMEOUT

echo ""
echo "=========================================="
echo "Duże problemy (12 bloków) - 8 punktów"
echo "=========================================="

echo ""
echo ">>> Problem 4-6, subgoals + mismatch"
uv run python -m Project2.blocksworld5_4_points --large --subgoals --heur=mismatch --viz --timeout=$TIMEOUT

echo ""
echo ">>> Problem 4-6, subgoals + zero"
uv run python -m Project2.blocksworld5_4_points --large --subgoals --heur=zero --viz --timeout=$TIMEOUT

echo ""
echo "=========================================="
echo "WSZYSTKIE TESTY ZAKOŃCZONE!"
echo "=========================================="
