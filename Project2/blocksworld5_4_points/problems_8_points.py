"""Large Blocks World problems (12 blocks) for 8-point requirements.

These problems require solutions with >= 20 actions.
"""

from __future__ import annotations

from typing import Dict

import Project2  # noqa: F401

from stripsProblem import Planning_problem, create_blocks_world, on, clear


def make_large_domain():
    """Create a domain with 12 blocks for complex problems."""
    blocks = {"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l"}
    return create_blocks_world(blocks)


def make_large_problems(domain=None) -> Dict[str, Planning_problem]:
    """Create 3 large problems requiring >= 20 actions each."""
    if domain is None:
        domain = make_large_domain()

    # Problem 4: Two 6-block towers -> one 12-block tower
    # Start: a-b-c-d-e-f tower, g-h-i-j-k-l tower
    # Goal: single tower a-b-c-d-e-f-g-h-i-j-k-l (a at top, l at bottom)
    # Requires: dismantle (10 moves) + build (11 moves) = ~21 moves minimum
    problem4 = Planning_problem(
        domain,
        {
            # Tower 1: a on b on c on d on e on f on table
            on("a"): "b",
            on("b"): "c",
            on("c"): "d",
            on("d"): "e",
            on("e"): "f",
            on("f"): "table",
            clear("a"): True,
            clear("b"): False,
            clear("c"): False,
            clear("d"): False,
            clear("e"): False,
            clear("f"): False,
            # Tower 2: g on h on i on j on k on l on table
            on("g"): "h",
            on("h"): "i",
            on("i"): "j",
            on("j"): "k",
            on("k"): "l",
            on("l"): "table",
            clear("g"): True,
            clear("h"): False,
            clear("i"): False,
            clear("j"): False,
            clear("k"): False,
            clear("l"): False,
        },
        {
            # Goal: single tower a-b-c-d-e-f-g-h-i-j-k-l
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
    )

    # Problem 5: Single 12-tower -> reversed 12-tower
    # Start: tower a-b-c-d-e-f-g-h-i-j-k-l (a at top, l at bottom)
    # Goal: tower l-k-j-i-h-g-f-e-d-c-b-a (l at top, a at bottom)
    # Requires: dismantle (11 moves) + build reversed (11 moves) = 22 moves minimum
    problem5 = Planning_problem(
        domain,
        {
            # Start: single tower
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
            clear("a"): True,
            clear("b"): False,
            clear("c"): False,
            clear("d"): False,
            clear("e"): False,
            clear("f"): False,
            clear("g"): False,
            clear("h"): False,
            clear("i"): False,
            clear("j"): False,
            clear("k"): False,
            clear("l"): False,
        },
        {
            # Goal: reversed tower l-k-j-i-h-g-f-e-d-c-b-a (l at top, a at bottom)
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
    )

    # Problem 6: 2 towers of 6 -> reversed single 12-tower
    # Start: towers a-b-c-d-e-f on table, g-h-i-j-k-l on table
    # Goal: reversed tower l-k-j-i-h-g-f-e-d-c-b-a
    # Requires: dismantle 2 towers (10 moves) + build reversed tower (11 moves) = ~21 moves
    problem6 = Planning_problem(
        domain,
        {
            # Tower 1: a-b-c-d-e-f (a at top)
            on("a"): "b",
            on("b"): "c",
            on("c"): "d",
            on("d"): "e",
            on("e"): "f",
            on("f"): "table",
            clear("a"): True,
            clear("b"): False,
            clear("c"): False,
            clear("d"): False,
            clear("e"): False,
            clear("f"): False,
            # Tower 2: g-h-i-j-k-l (g at top)
            on("g"): "h",
            on("h"): "i",
            on("i"): "j",
            on("j"): "k",
            on("k"): "l",
            on("l"): "table",
            clear("g"): True,
            clear("h"): False,
            clear("i"): False,
            clear("j"): False,
            clear("k"): False,
            clear("l"): False,
        },
        {
            # Goal: reversed tower l-k-j-i-h-g-f-e-d-c-b-a
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
    )

    return {"problem4": problem4, "problem5": problem5, "problem6": problem6}
