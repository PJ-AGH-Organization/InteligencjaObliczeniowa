"""Subgoals definitions for 6-point and 8-point requirements.

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

    # ========== 8-point problems (12 blocks, >= 20 actions) ==========

    elif problem_name == "problem4":
        # Problem4: Two 6-block towers -> single 12-block tower
        # Start: a-b-c-d-e-f tower + g-h-i-j-k-l tower
        # Goal: single tower a-b-c-d-e-f-g-h-i-j-k-l
        return [
            # Subgoal 1: Disassemble first tower (a,b,c,d,e to table)
            {
                on("a"): "table",
                on("b"): "table",
                on("c"): "table",
                on("d"): "table",
                on("e"): "table",
            },
            # Subgoal 2: Disassemble second tower completely
            {
                on("a"): "table",
                on("b"): "table",
                on("c"): "table",
                on("d"): "table",
                on("e"): "table",
                on("f"): "table",
                on("g"): "table",
                on("h"): "table",
                on("i"): "table",
                on("j"): "table",
                on("k"): "table",
                on("l"): "table",
            },
            # Subgoal 3: Build bottom of target (k on l)
            {
                on("k"): "l",
                on("l"): "table",
            },
            # Subgoal 4: Continue (j on k)
            {
                on("j"): "k",
                on("k"): "l",
            },
            # Subgoal 5: Continue (i on j)
            {
                on("i"): "j",
                on("j"): "k",
            },
            # Subgoal 6: Continue (h on i)
            {
                on("h"): "i",
                on("i"): "j",
            },
            # Subgoal 7: Continue (g on h)
            {
                on("g"): "h",
                on("h"): "i",
            },
            # Subgoal 8: Continue (f on g)
            {
                on("f"): "g",
                on("g"): "h",
            },
            # Subgoal 9: Complete tower
            {
                on("a"): "b",
                on("b"): "c",
                on("c"): "d",
                on("d"): "e",
                on("e"): "f",
                on("f"): "g",
                on("g"): "h",
                on("h"): "i",
                on("i"): "j",
                on("j"): "k",
                on("k"): "l",
                on("l"): "table",
            },
        ]

    elif problem_name == "problem5":
        # Problem5: 12-tower -> reversed 12-tower
        # Start: tower a-b-c-d-e-f-g-h-i-j-k-l (a at top)
        # Goal: reversed tower l-k-j-i-h-g-f-e-d-c-b-a (l at top, a at bottom)
        return [
            # Subgoal 1: Disassemble tower (first 6 blocks to table)
            {
                on("a"): "table",
                on("b"): "table",
                on("c"): "table",
                on("d"): "table",
                on("e"): "table",
                on("f"): "table",
                clear("g"): True,
            },
            # Subgoal 2: Disassemble rest (all to table)
            {
                on("a"): "table",
                on("b"): "table",
                on("c"): "table",
                on("d"): "table",
                on("e"): "table",
                on("f"): "table",
                on("g"): "table",
                on("h"): "table",
                on("i"): "table",
                on("j"): "table",
                on("k"): "table",
                on("l"): "table",
            },
            # Subgoal 3: Build reversed base (b on a)
            {
                on("b"): "a",
                on("a"): "table",
            },
            # Subgoal 4: Continue (c on b)
            {
                on("c"): "b",
                on("b"): "a",
            },
            # Subgoal 5: Continue (d on c)
            {
                on("d"): "c",
                on("c"): "b",
            },
            # Subgoal 6: Continue (e on d)
            {
                on("e"): "d",
                on("d"): "c",
            },
            # Subgoal 7: Continue (f on e)
            {
                on("f"): "e",
                on("e"): "d",
            },
            # Subgoal 8: Continue (g on f)
            {
                on("g"): "f",
                on("f"): "e",
            },
            # Subgoal 9: Continue (h on g)
            {
                on("h"): "g",
                on("g"): "f",
            },
            # Subgoal 10: Complete reversed tower
            {
                on("l"): "k",
                on("k"): "j",
                on("j"): "i",
                on("i"): "h",
                on("h"): "g",
                on("g"): "f",
                on("f"): "e",
                on("e"): "d",
                on("d"): "c",
                on("c"): "b",
                on("b"): "a",
                on("a"): "table",
            },
        ]

    elif problem_name == "problem6":
        # Problem6: 2 towers of 6 -> reversed single 12-tower
        # Start: towers a-b-c-d-e-f and g-h-i-j-k-l
        # Goal: reversed tower l-k-j-i-h-g-f-e-d-c-b-a
        return [
            # Subgoal 1: Disassemble tower 1 (a,b,c,d,e to table)
            {
                on("a"): "table",
                on("b"): "table",
                on("c"): "table",
                on("d"): "table",
                on("e"): "table",
            },
            # Subgoal 2: Disassemble tower 2 (g,h,i,j,k to table)
            {
                on("a"): "table",
                on("b"): "table",
                on("c"): "table",
                on("d"): "table",
                on("e"): "table",
                on("f"): "table",
                on("g"): "table",
                on("h"): "table",
                on("i"): "table",
                on("j"): "table",
                on("k"): "table",
                on("l"): "table",
            },
            # Subgoal 3: Build reversed base (b on a)
            {
                on("b"): "a",
                on("a"): "table",
            },
            # Subgoal 4: Continue (c on b)
            {
                on("c"): "b",
                on("b"): "a",
            },
            # Subgoal 5: Continue (d on c)
            {
                on("d"): "c",
                on("c"): "b",
            },
            # Subgoal 6: Continue (e on d)
            {
                on("e"): "d",
                on("d"): "c",
            },
            # Subgoal 7: Continue (f on e)
            {
                on("f"): "e",
                on("e"): "d",
            },
            # Subgoal 8: Continue (g on f)
            {
                on("g"): "f",
                on("f"): "e",
            },
            # Subgoal 9: Continue (h on g)
            {
                on("h"): "g",
                on("g"): "f",
            },
            # Subgoal 10: Continue (i on h)
            {
                on("i"): "h",
                on("h"): "g",
            },
            # Subgoal 11: Complete reversed tower
            {
                on("l"): "k",
                on("k"): "j",
                on("j"): "i",
                on("i"): "h",
                on("h"): "g",
                on("g"): "f",
                on("f"): "e",
                on("e"): "d",
                on("d"): "c",
                on("c"): "b",
                on("b"): "a",
                on("a"): "table",
            },
        ]

    else:
        raise ValueError(f"Unknown problem: {problem_name}")
