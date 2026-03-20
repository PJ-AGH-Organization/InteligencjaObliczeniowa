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
    """Create 3 small problems (5 blocks, >= 50 states, >= 4 actions).

    Problems have diverse goal structures:
    - Problem 1: One 3-tower (a->b->c) + 2 separate blocks
    - Problem 2: Two 2-towers (b->a and d->c) + 1 separate block
    - Problem 3: One 4-tower (e->d->c->b) + 1 separate block
    """
    if domain is None:
        domain = make_domain()

    # Problem 1: Build a 3-tower from scattered blocks
    # Initial: c on a, e on d, b alone
    # Goal: tower a->b->c, with d,e separate on table
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

    # Problem 2: Build two separate 2-towers
    # Initial: tall tower a->b->c->d->e
    # Goal: two 2-towers (b->a and d->c) with e separate
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

    # Problem 3: Build a 4-tower from blocked initial state
    # Initial: d on b (blocks b), c on a, e on table
    # Goal: 4-tower e->d->c->b with a separate
    # Requires minimum 4 actions: d off b, c to b, d to c, e to d
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


# =============================================================================
# Large problems (12 blocks) - 8 point requirements (>= 20 actions)
# =============================================================================


def make_large_problems(domain: STRIPS_domain | None = None) -> Dict[str, Planning_problem]:
    """Create 3 large problems (12 blocks, >= 20 actions).

    Problems have diverse goal structures:
    - Problem 4: Two 6-towers (reversed order: f->e->...->a and l->k->...->g)
    - Problem 5: One 12-tower (a->b->c->...->l)
    - Problem 6: Four 3-towers (c->b->a, f->e->d, i->h->g, l->k->j)
    """
    if domain is None:
        domain = make_large_domain()

    # Problem 4: Two 6-block towers -> Two reversed 6-block towers
    # Initial: towers a->b->c->d->e->f and g->h->i->j->k->l (top to bottom)
    # Goal: reversed towers f->e->d->c->b->a and l->k->j->i->h->g
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
            # Reversed tower 1: f->e->d->c->b->a
            on("f"): "e", on("e"): "d", on("d"): "c",
            on("c"): "b", on("b"): "a", on("a"): "table",
            # Reversed tower 2: l->k->j->i->h->g
            on("l"): "k", on("k"): "j", on("j"): "i",
            on("i"): "h", on("h"): "g", on("g"): "table",
        },
    )

    # Problem 5: Two 6-towers -> One 12-tower
    # Initial: towers a->b->c->d->e->f and g->h->i->j->k->l
    # Goal: single tower a->b->c->d->e->f->g->h->i->j->k->l
    problem5 = Planning_problem(
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

    # Problem 6: 12-tower -> Three 4-towers
    # Initial: one tall tower a->b->c->...->l
    # Goal: three 4-towers: d->c->b->a, h->g->f->e, l->k->j->i
    # Requires 11 (dismantle) + 9 (build 3 towers * 3 actions) = 20 actions
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
            # Tower 1: d->c->b->a (4 blocks)
            on("d"): "c", on("c"): "b", on("b"): "a", on("a"): "table",
            # Tower 2: h->g->f->e (4 blocks)
            on("h"): "g", on("g"): "f", on("f"): "e", on("e"): "table",
            # Tower 3: l->k->j->i (4 blocks)
            on("l"): "k", on("k"): "j", on("j"): "i", on("i"): "table",
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
    # Problem 1: Build 3-tower a->b->c with d,e separate
    # Initial: c on a, e on d, b alone
    "problem1": [
        {on("c"): "table", clear("a"): True},  # Move c off a
        {on("c"): "table", on("b"): "c"},  # Put b on c
        {on("a"): "b", on("b"): "c", on("c"): "table", on("d"): "table", on("e"): "table"},  # Full goal
    ],
    # Problem 2: Build two 2-towers (b->a and d->c) + e separate
    # Initial: tower a->b->c->d->e
    "problem2": [
        {on("a"): "table", on("b"): "table", on("c"): "table"},  # Dismantle upper part
        {on("a"): "table", on("b"): "a", on("c"): "table"},  # Build first 2-tower b->a
        {on("b"): "a", on("a"): "table", on("d"): "c", on("c"): "table", on("e"): "table"},  # Full goal
    ],
    # Problem 3: Build 4-tower e->d->c->b with a separate
    # Initial: d on b (blocks b), c on a
    "problem3": [
        {on("d"): "table", clear("b"): True},  # Move d off b to unblock it
        {on("c"): "b", on("b"): "table"},  # Put c on b
        {on("d"): "c", on("c"): "b"},  # Build d->c->b
        {on("e"): "d", on("d"): "c", on("c"): "b", on("b"): "table", on("a"): "table"},  # Full goal
    ],
}

# Large problems subgoals (12 blocks)
_SUBGOALS_LARGE = {
    # Problem 4: Two 6-towers -> Two reversed 6-towers
    # Goal: f->e->d->c->b->a and l->k->j->i->h->g
    "problem4": [
        # Phase 1: Dismantle towers to table
        {on("a"): "table", on("b"): "table", on("c"): "table", on("d"): "table", on("e"): "table"},
        {on(b): "table" for b in "abcdefghijkl"},
        # Phase 2: Build first reversed tower f->e->d->c->b->a
        {on("b"): "a", on("a"): "table"},
        {on("c"): "b", on("b"): "a"},
        {on("d"): "c", on("c"): "b"},
        {on("e"): "d", on("d"): "c"},
        {on("f"): "e", on("e"): "d", on("d"): "c", on("c"): "b", on("b"): "a", on("a"): "table"},
        # Phase 3: Build second reversed tower l->k->j->i->h->g
        {on("f"): "e", on("h"): "g", on("g"): "table"},
        {on("f"): "e", on("i"): "h", on("h"): "g"},
        {
            on("f"): "e", on("e"): "d", on("d"): "c", on("c"): "b", on("b"): "a", on("a"): "table",
            on("l"): "k", on("k"): "j", on("j"): "i", on("i"): "h", on("h"): "g", on("g"): "table",
        },
    ],
    # Problem 5: Two 6-towers -> One 12-tower a->b->c->...->l
    "problem5": [
        # Phase 1: Dismantle first tower
        {on("a"): "table", on("b"): "table", on("c"): "table", on("d"): "table", on("e"): "table"},
        {on(b): "table" for b in "abcdefghijkl"},
        # Phase 2: Build 12-tower from bottom up
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
    # Problem 6: 12-tower -> Three 4-towers (d->c->b->a, h->g->f->e, l->k->j->i)
    "problem6": [
        # Phase 1: Dismantle the tall tower
        {on("a"): "table", on("b"): "table", on("c"): "table"},
        {on("a"): "table", on("b"): "table", on("c"): "table", on("d"): "table", on("e"): "table", on("f"): "table"},
        {on(b): "table" for b in "abcdefghijkl"},
        # Phase 2: Build three 4-towers
        {on("b"): "a", on("a"): "table"},  # Start tower 1
        {on("c"): "b", on("b"): "a"},  # Continue tower 1
        {on("d"): "c", on("c"): "b", on("b"): "a", on("a"): "table"},  # Complete tower 1
        {on("d"): "c", on("f"): "e", on("e"): "table"},  # Start tower 2
        {on("d"): "c", on("g"): "f", on("f"): "e"},  # Continue tower 2
        {on("d"): "c", on("h"): "g", on("g"): "f", on("f"): "e", on("e"): "table"},  # Complete tower 2
        {
            on("d"): "c", on("c"): "b", on("b"): "a", on("a"): "table",
            on("h"): "g", on("g"): "f", on("f"): "e", on("e"): "table",
            on("l"): "k", on("k"): "j", on("j"): "i", on("i"): "table",
        },  # Full goal
    ],
}

_SUBGOALS = _SUBGOALS_SMALL | _SUBGOALS_LARGE
