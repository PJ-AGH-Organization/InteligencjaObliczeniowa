"""Search helpers for AIPython forward STRIPS planning."""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Set, Tuple

import Project2  # noqa: F401

from stripsProblem import Planning_problem
from stripsForwardPlanner import Forward_STRIPS
from searchMPP import SearcherMPP

StateAssignment = Dict[str, object]
Goal = Dict[str, object]
Heuristic = Callable[[StateAssignment, Goal], float]


def extract_action_names(path) -> List[str]:
    actions: List[str] = []
    current = path
    while getattr(current, "arc", None) is not None and current.arc is not None:
        actions.append(str(current.arc.action))
        current = current.initial
    actions.reverse()
    return actions


def extract_state_assignments(path) -> List[StateAssignment]:
    """Return state assignments from start->goal along the solution path."""
    # Path.nodes() yields from end backwards; we reverse for chronological order.
    nodes = list(path.nodes())
    nodes.reverse()
    return [getattr(st, "assignment", st) for st in nodes]


def reachable_state_count(problem: Planning_problem, limit: int = 10_000) -> int:
    """BFS over Forward_STRIPS neighbors; returns number of unique states (capped)."""
    search_problem = Forward_STRIPS(problem)
    start = search_problem.start_node()

    seen: Set[object] = {start}
    q: deque[object] = deque([start])

    while q and len(seen) < limit:
        st = q.popleft()
        for arc in search_problem.neighbors(st):
            nxt = arc.to_node
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
                if len(seen) >= limit:
                    break

    return len(seen)


@dataclass(frozen=True)
class SolveResult:
    solved: bool
    plan: Optional[List[str]]
    cost: Optional[float]
    expanded: int
    seconds: float
    path: object | None


def solve_forward(problem: Planning_problem, heur: Optional[Heuristic] = None) -> SolveResult:
    """Run A* (SearcherMPP) on forward STRIPS."""
    if heur is None:
        heur = lambda *_: 0  # type: ignore[assignment]

    sp = Forward_STRIPS(problem, heur=heur)
    searcher = SearcherMPP(sp)

    t0 = time.perf_counter()
    path = searcher.search()
    dt = time.perf_counter() - t0

    if path is None:
        return SolveResult(False, None, None, searcher.num_expanded, dt, None)

    return SolveResult(True, extract_action_names(path), path.cost, searcher.num_expanded, dt, path)
