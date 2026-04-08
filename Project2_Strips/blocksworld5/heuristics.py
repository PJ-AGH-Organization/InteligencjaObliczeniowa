"""Heuristics for Blocks World forward planning."""

from __future__ import annotations

from typing import Dict

StateAssignment = Dict[str, object]
Goal = Dict[str, object]


def goal_mismatch_heur(state: StateAssignment, goal: Goal) -> float:
    """Count how many goal feature-value pairs are not yet satisfied."""
    return float(sum(1 for feat, val in goal.items() if state.get(feat) != val))
