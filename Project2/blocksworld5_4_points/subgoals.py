"""Subgoals definitions for 6-point requirements.

Each problem has at least 2 subgoals that decompose the main goal into smaller steps.
"""

from __future__ import annotations

from typing import Dict, List

import Project2  # noqa: F401

from stripsProblem import on, clear


def get_subgoals(problem_name: str) -> List[Dict[str, object]]:
    """Return list of subgoals for given problem.

    Each subgoal is a partial goal dict that must be achieved before the next.
    The final subgoal should match the full problem goal.
    """

    if problem_name == "problem1":
        # Problem1:
        # Start: c on a, e on d, a/b/d on table
        # Goal: a on b, b on c, c on table, e on table
        #
        # Subgoal 1: Clear a by moving c to table
        # Subgoal 2: Build stack b on c
        # Subgoal 3: Complete goal (a on b, e on table)
        return [
            # Subgoal 1: c must be on table (to free a)
            {
                on("c"): "table",
                clear("a"): True,
            },
            # Subgoal 2: Build base of tower (b on c)
            {
                on("c"): "table",
                on("b"): "c",
            },
            # Subgoal 3: Complete goal
            {
                on("a"): "b",
                on("b"): "c",
                on("c"): "table",
                on("e"): "table",
            },
        ]

    elif problem_name == "problem2":
        # Problem2:
        # Start: a on b on c on d on e on table (tall tower)
        # Goal: e on d, d on c, c on table, a on b
        #
        # Subgoal 1: Disassemble tower - get c to table
        # Subgoal 2: Build new base (d on c)
        # Subgoal 3: Complete goal (e on d, a on b)
        return [
            # Subgoal 1: Disassemble to get c on table
            {
                on("c"): "table",
                clear("c"): True,
            },
            # Subgoal 2: Build d on c
            {
                on("c"): "table",
                on("d"): "c",
                clear("d"): True,
            },
            # Subgoal 3: Complete goal
            {
                on("e"): "d",
                on("d"): "c",
                on("c"): "table",
                on("a"): "b",
            },
        ]

    elif problem_name == "problem3":
        # Problem3:
        # Start: c on a, b/d/e on table
        # Goal: a on b, b on c, c on table, d on e
        #
        # Subgoal 1: Clear a (move c to table)
        # Subgoal 2: Build tower a-b-c
        # Subgoal 3: Complete with d on e
        return [
            # Subgoal 1: c on table
            {
                on("c"): "table",
                clear("a"): True,
            },
            # Subgoal 2: Build a-b-c tower
            {
                on("c"): "table",
                on("b"): "c",
                on("a"): "b",
            },
            # Subgoal 3: Complete goal with d on e
            {
                on("a"): "b",
                on("b"): "c",
                on("c"): "table",
                on("d"): "e",
            },
        ]

    else:
        raise ValueError(f"Unknown problem: {problem_name}")
