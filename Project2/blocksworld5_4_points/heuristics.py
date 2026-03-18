"""Heurystyka dla problemu Blocks World w AIPython STRIPS."""

from __future__ import annotations
from typing import Dict

StateAssignment = Dict[str, object]
Goal = Dict[str, object]


def goal_mismatch_heur(state: StateAssignment, goal: Goal) -> float:
    """
    Heurystyka liczaca ile celow nie jest jeszcze spelnionych.

    Jest DOPUSZCZALNA (admissible) - nigdy nie przeszacowuje kosztu,
    bo kazdy niespelniony cel wymaga co najmniej jednej akcji.
    """
    return float(sum(1 for feat, val in goal.items() if state.get(feat) != val))
