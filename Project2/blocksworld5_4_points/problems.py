"""Blocks World problems in AIPython STRIPS format.

Contains:
- Small problems (5 blocks) for 4-6 point requirements
- Large problems (12 blocks) for 8 point requirements
- Subgoals for all problems
"""

from __future__ import annotations

from typing import Dict, List, Set

import Project2  # noqa: F401

from stripsProblem import Planning_problem, STRIPS_domain, create_blocks_world, on, clear

Goal = Dict[str, object]


# =============================================================================
# Domain creation
# =============================================================================


def make_domain(blocks: Set[str] | None = None) -> STRIPS_domain:
    """Create a Blocks World domain with given blocks."""
    if blocks is None:
        blocks = {"a", "b", "c", "d", "e"}
    return create_blocks_world(blocks)


def make_large_domain() -> STRIPS_domain:
    """Create a domain with 12 blocks for complex problems."""
    return make_domain({"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l"})


# =============================================================================
# Small problems (5 blocks) - 4-6 point requirements
# =============================================================================


def make_problems(domain: STRIPS_domain | None = None) -> Dict[str, Planning_problem]:
    """Create 3 small problems (5 blocks, >= 50 states, >= 4 actions)."""
    if domain is None:
        domain = make_domain()

    problem1 = Planning_problem(
        domain,
        {
            on("a"): "table", on("b"): "table", on("c"): "a",
            on("d"): "table", on("e"): "d",
            clear("a"): False, clear("b"): True, clear("c"): True,
            clear("d"): False, clear("e"): True,
        },
        {on("a"): "b", on("b"): "c", on("c"): "table", on("e"): "table"},
    )

    problem2 = Planning_problem(
        domain,
        {
            on("a"): "b", on("b"): "c", on("c"): "d",
            on("d"): "e", on("e"): "table",
            clear("a"): True, clear("b"): False, clear("c"): False,
            clear("d"): False, clear("e"): False,
        },
        {on("e"): "d", on("d"): "c", on("c"): "table", on("a"): "b"},
    )

    problem3 = Planning_problem(
        domain,
        {
            on("a"): "table", on("b"): "table", on("c"): "a",
            on("d"): "table", on("e"): "table",
            clear("a"): False, clear("b"): True, clear("c"): True,
            clear("d"): True, clear("e"): True,
        },
        {on("a"): "b", on("b"): "c", on("c"): "table", on("d"): "e"},
    )

    return {"problem1": problem1, "problem2": problem2, "problem3": problem3}


# =============================================================================
# Large problems (12 blocks) - 8 point requirements (>= 20 actions)
# =============================================================================


def make_large_problems(domain: STRIPS_domain | None = None) -> Dict[str, Planning_problem]:
    """Create 3 large problems (12 blocks, >= 20 actions)."""
    if domain is None:
        domain = make_large_domain()

    # Problem 4: Two 6-block towers -> one 12-block tower
    problem4 = Planning_problem(
        domain,
        {
            # Tower 1: a-b-c-d-e-f
            on("a"): "b", on("b"): "c", on("c"): "d",
            on("d"): "e", on("e"): "f", on("f"): "table",
            clear("a"): True, clear("b"): False, clear("c"): False,
            clear("d"): False, clear("e"): False, clear("f"): False,
            # Tower 2: g-h-i-j-k-l
            on("g"): "h", on("h"): "i", on("i"): "j",
            on("j"): "k", on("k"): "l", on("l"): "table",
            clear("g"): True, clear("h"): False, clear("i"): False,
            clear("j"): False, clear("k"): False, clear("l"): False,
        },
        {
            on("a"): "b", on("b"): "c", on("c"): "d", on("d"): "e",
            on("e"): "f", on("f"): "g", on("g"): "h", on("h"): "i",
            on("i"): "j", on("j"): "k", on("k"): "l", on("l"): "table",
        },
    )

    # Problem 5: 12-tower -> reversed 12-tower
    problem5 = Planning_problem(
        domain,
        {
            on("a"): "b", on("b"): "c", on("c"): "d", on("d"): "e",
            on("e"): "f", on("f"): "g", on("g"): "h", on("h"): "i",
            on("i"): "j", on("j"): "k", on("k"): "l", on("l"): "table",
            clear("a"): True, clear("b"): False, clear("c"): False,
            clear("d"): False, clear("e"): False, clear("f"): False,
            clear("g"): False, clear("h"): False, clear("i"): False,
            clear("j"): False, clear("k"): False, clear("l"): False,
        },
        {
            on("l"): "k", on("k"): "j", on("j"): "i", on("i"): "h",
            on("h"): "g", on("g"): "f", on("f"): "e", on("e"): "d",
            on("d"): "c", on("c"): "b", on("b"): "a", on("a"): "table",
        },
    )

    # Problem 6: Two 6-block towers -> reversed 12-tower
    problem6 = Planning_problem(
        domain,
        {
            # Tower 1: a-b-c-d-e-f
            on("a"): "b", on("b"): "c", on("c"): "d",
            on("d"): "e", on("e"): "f", on("f"): "table",
            clear("a"): True, clear("b"): False, clear("c"): False,
            clear("d"): False, clear("e"): False, clear("f"): False,
            # Tower 2: g-h-i-j-k-l
            on("g"): "h", on("h"): "i", on("i"): "j",
            on("j"): "k", on("k"): "l", on("l"): "table",
            clear("g"): True, clear("h"): False, clear("i"): False,
            clear("j"): False, clear("k"): False, clear("l"): False,
        },
        {
            on("l"): "k", on("k"): "j", on("j"): "i", on("i"): "h",
            on("h"): "g", on("g"): "f", on("f"): "e", on("e"): "d",
            on("d"): "c", on("c"): "b", on("b"): "a", on("a"): "table",
        },
    )

    return {"problem4": problem4, "problem5": problem5, "problem6": problem6}


# =============================================================================
# Subgoals for all problems
# =============================================================================


def get_subgoals(problem_name: str) -> List[Goal]:
    """Return list of subgoals for given problem.

    Each subgoal is a partial goal dict that must be achieved in order.
    The final subgoal matches the full problem goal.
    """
    subgoals = _SUBGOALS.get(problem_name)
    if subgoals is None:
        raise ValueError(f"Unknown problem: {problem_name}")
    return subgoals


# Small problems subgoals (5 blocks)
_SUBGOALS_SMALL = {
    "problem1": [
        {on("c"): "table", clear("a"): True},
        {on("c"): "table", on("b"): "c"},
        {on("a"): "b", on("b"): "c", on("c"): "table", on("e"): "table"},
    ],
    "problem2": [
        {on("c"): "table", clear("c"): True},
        {on("c"): "table", on("d"): "c", clear("d"): True},
        {on("e"): "d", on("d"): "c", on("c"): "table", on("a"): "b"},
    ],
    "problem3": [
        {on("c"): "table", clear("a"): True},
        {on("c"): "table", on("b"): "c", on("a"): "b"},
        {on("a"): "b", on("b"): "c", on("c"): "table", on("d"): "e"},
    ],
}

# Large problems subgoals (12 blocks)
_SUBGOALS_LARGE = {
    "problem4": [
        {on("a"): "table", on("b"): "table", on("c"): "table", on("d"): "table", on("e"): "table"},
        {on(b): "table" for b in "abcdefghijkl"},
        {on("k"): "l", on("l"): "table"},
        {on("j"): "k", on("k"): "l"},
        {on("i"): "j", on("j"): "k"},
        {on("h"): "i", on("i"): "j"},
        {on("g"): "h", on("h"): "i"},
        {on("f"): "g", on("g"): "h"},
        {
            on("a"): "b", on("b"): "c", on("c"): "d", on("d"): "e",
            on("e"): "f", on("f"): "g", on("g"): "h", on("h"): "i",
            on("i"): "j", on("j"): "k", on("k"): "l", on("l"): "table",
        },
    ],
    "problem5": [
        {on(b): "table" for b in "abcdef"} | {clear("g"): True},
        {on(b): "table" for b in "abcdefghijkl"},
        {on("b"): "a", on("a"): "table"},
        {on("c"): "b", on("b"): "a"},
        {on("d"): "c", on("c"): "b"},
        {on("e"): "d", on("d"): "c"},
        {on("f"): "e", on("e"): "d"},
        {on("g"): "f", on("f"): "e"},
        {on("h"): "g", on("g"): "f"},
        {
            on("l"): "k", on("k"): "j", on("j"): "i", on("i"): "h",
            on("h"): "g", on("g"): "f", on("f"): "e", on("e"): "d",
            on("d"): "c", on("c"): "b", on("b"): "a", on("a"): "table",
        },
    ],
    "problem6": [
        {on("a"): "table", on("b"): "table", on("c"): "table", on("d"): "table", on("e"): "table"},
        {on(b): "table" for b in "abcdefghijkl"},
        {on("b"): "a", on("a"): "table"},
        {on("c"): "b", on("b"): "a"},
        {on("d"): "c", on("c"): "b"},
        {on("e"): "d", on("d"): "c"},
        {on("f"): "e", on("e"): "d"},
        {on("g"): "f", on("f"): "e"},
        {on("h"): "g", on("g"): "f"},
        {on("i"): "h", on("h"): "g"},
        {
            on("l"): "k", on("k"): "j", on("j"): "i", on("i"): "h",
            on("h"): "g", on("g"): "f", on("f"): "e", on("e"): "d",
            on("d"): "c", on("c"): "b", on("b"): "a", on("a"): "table",
        },
    ],
}

_SUBGOALS = _SUBGOALS_SMALL | _SUBGOALS_LARGE
