from __future__ import annotations

from typing import Dict, List, Set

import Project2

from stripsProblem import Planning_problem, STRIPS_domain, create_blocks_world, on, clear

Goal = Dict[str, object]

def make_domain(blocks: Set[str] | None = None) -> STRIPS_domain:
    if blocks is None:
        blocks = {"a", "b", "c", "d", "e"}
    return create_blocks_world(blocks)


def make_large_domain() -> STRIPS_domain:
    return make_domain({"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l"})

def make_problems(domain: STRIPS_domain | None = None) -> Dict[str, Planning_problem]:
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
        {on("a"): "b", on("b"): "c", on("c"): "table", on("d"): "table", on("e"): "table"},
    )

    problem2 = Planning_problem(
        domain,
        {
            on("a"): "b", on("b"): "c", on("c"): "d",
            on("d"): "e", on("e"): "table",
            clear("a"): True, clear("b"): False, clear("c"): False,
            clear("d"): False, clear("e"): False,
        },
        {on("b"): "a", on("a"): "table", on("d"): "c", on("c"): "table", on("e"): "table"},
    )

    problem3 = Planning_problem(
        domain,
        {
            on("a"): "table", on("b"): "table", on("c"): "a",
            on("d"): "b", on("e"): "table",
            clear("a"): False, clear("b"): False, clear("c"): True,
            clear("d"): True, clear("e"): True,
        },
        {on("e"): "d", on("d"): "c", on("c"): "b", on("b"): "table", on("a"): "table"},
    )

    return {"problem1": problem1, "problem2": problem2, "problem3": problem3}

def make_large_problems(domain: STRIPS_domain | None = None) -> Dict[str, Planning_problem]:
    if domain is None:
        domain = make_large_domain()

    problem4 = Planning_problem(
        domain,
        {
            on("a"): "b", on("b"): "c", on("c"): "d",
            on("d"): "e", on("e"): "f", on("f"): "table",
            clear("a"): True, clear("b"): False, clear("c"): False,
            clear("d"): False, clear("e"): False, clear("f"): False,
            on("g"): "h", on("h"): "i", on("i"): "j",
            on("j"): "k", on("k"): "l", on("l"): "table",
            clear("g"): True, clear("h"): False, clear("i"): False,
            clear("j"): False, clear("k"): False, clear("l"): False,
        },
        {
            on("f"): "e", on("e"): "d", on("d"): "c",
            on("c"): "b", on("b"): "a", on("a"): "table",
            on("l"): "k", on("k"): "j", on("j"): "i",
            on("i"): "h", on("h"): "g", on("g"): "table",
        },
    )

    problem5 = Planning_problem(
        domain,
        {
            on("a"): "b", on("b"): "c", on("c"): "d",
            on("d"): "e", on("e"): "f", on("f"): "table",
            clear("a"): True, clear("b"): False, clear("c"): False,
            clear("d"): False, clear("e"): False, clear("f"): False,
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

    problem6 = Planning_problem(
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
            on("d"): "c", on("c"): "b", on("b"): "a", on("a"): "table",
            on("h"): "g", on("g"): "f", on("f"): "e", on("e"): "table",
            on("l"): "k", on("k"): "j", on("j"): "i", on("i"): "table",
        },
    )

    return {"problem4": problem4, "problem5": problem5, "problem6": problem6}


def get_subgoals(problem_name: str) -> List[Goal]:
    subgoals = _SUBGOALS.get(problem_name)
    if subgoals is None:
        raise ValueError(f"Unknown problem: {problem_name}")
    return subgoals


_SUBGOALS_SMALL = {
    "problem1": [
        {on("c"): "table", on("e"): "table", clear("a"): True, clear("d"): True},
        {on("c"): "table", on("b"): "c", clear("b"): False},
        {on("a"): "b", on("b"): "c", on("c"): "table", on("d"): "table", on("e"): "table"},
    ],
    "problem2": [
        {on("a"): "table", on("b"): "table", on("c"): "table", on("d"): "table", on("e"): "table"},
        {on("b"): "a", on("a"): "table", on("c"): "table"},
        {on("b"): "a", on("a"): "table", on("d"): "c", on("c"): "table", on("e"): "table"},
    ],
    "problem3": [
        {on("d"): "table", clear("b"): True},
        {on("c"): "b", on("d"): "c", clear("d"): True},
        {on("e"): "d", on("d"): "c", on("c"): "b", on("b"): "table", on("a"): "table"},
    ],
}

_SUBGOALS_LARGE = {
    "problem4": [
        {on(b): "table" for b in "abcdefghijkl"},
        {on("f"): "e", on("e"): "d", on("d"): "c", on("c"): "b", on("b"): "a", on("a"): "table"},
        {
            on("f"): "e", on("e"): "d", on("d"): "c", on("c"): "b", on("b"): "a", on("a"): "table",
            on("l"): "k", on("k"): "j", on("j"): "i", on("i"): "h", on("h"): "g", on("g"): "table",
        },
    ],
    "problem5": [
        {on(b): "table" for b in "abcdefghijkl"},
        {on("f"): "g", on("g"): "h", on("h"): "i", on("i"): "j", on("j"): "k", on("k"): "l", on("l"): "table"},
        {
            on("a"): "b", on("b"): "c", on("c"): "d", on("d"): "e",
            on("e"): "f", on("f"): "g", on("g"): "h", on("h"): "i",
            on("i"): "j", on("j"): "k", on("k"): "l", on("l"): "table",
        },
    ],
    "problem6": [
        {on(b): "table" for b in "abcdefghijkl"},
        {on("d"): "c", on("c"): "b", on("b"): "a", on("a"): "table"},
        {
            on("d"): "c", on("c"): "b", on("b"): "a", on("a"): "table",
            on("h"): "g", on("g"): "f", on("f"): "e", on("e"): "table",
            on("l"): "k", on("k"): "j", on("j"): "i", on("i"): "table",
        },
    ],
}

_SUBGOALS = _SUBGOALS_SMALL | _SUBGOALS_LARGE
