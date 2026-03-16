"""Blocks World (5 blocks) problems in AIPython STRIPS format."""

from __future__ import annotations

from typing import Dict

import Project2  # noqa: F401

from stripsProblem import Planning_problem, create_blocks_world, on, clear


def make_domain():
    blocks = {"a", "b", "c", "d", "e"}
    return create_blocks_world(blocks)


def make_problems(domain=None) -> Dict[str, Planning_problem]:
    if domain is None:
        domain = make_domain()

    problem1 = Planning_problem(
        domain,
        {
            on("a"): "table",
            on("b"): "table",
            on("c"): "a",
            on("d"): "table",
            on("e"): "d",
            clear("a"): False,
            clear("b"): True,
            clear("c"): True,
            clear("d"): False,
            clear("e"): True,
        },
        {
            on("a"): "b",
            on("b"): "c",
            on("c"): "table",
            on("e"): "table",
        },
    )

    problem2 = Planning_problem(
        domain,
        {
            on("a"): "b",
            on("b"): "c",
            on("c"): "d",
            on("d"): "e",
            on("e"): "table",
            clear("a"): True,
            clear("b"): False,
            clear("c"): False,
            clear("d"): False,
            clear("e"): False,
        },
        {
            on("e"): "d",
            on("d"): "c",
            on("c"): "table",
            on("a"): "b",
        },
    )

    problem3 = Planning_problem(
        domain,
        {
            on("a"): "table",
            on("b"): "table",
            on("c"): "a",
            on("d"): "table",
            on("e"): "table",
            clear("a"): False,
            clear("b"): True,
            clear("c"): True,
            clear("d"): True,
            clear("e"): True,
        },
        {
            on("a"): "b",
            on("b"): "c",
            on("c"): "table",
            on("d"): "e",
        },
    )

    return {"problem1": problem1, "problem2": problem2, "problem3": problem3}
