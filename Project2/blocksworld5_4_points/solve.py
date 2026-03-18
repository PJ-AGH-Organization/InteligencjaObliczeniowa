"""Search helpers and heuristics for AIPython forward STRIPS planning."""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Set

import Project2  # noqa: F401

from stripsProblem import Planning_problem, STRIPS_domain
from stripsForwardPlanner import Forward_STRIPS
from searchMPP import SearcherMPP

StateAssignment = Dict[str, object]
Goal = Dict[str, object]
Heuristic = Callable[[StateAssignment, Goal], float]
SubgoalList = List[Goal]


# =============================================================================
# Heuristics
# =============================================================================


def goal_mismatch_heur(state: StateAssignment, goal: Goal) -> float:
    """Count how many goal conditions are not yet satisfied.

    This heuristic is ADMISSIBLE (never overestimates) because each
    unsatisfied goal requires at least one action to achieve.
    """
    return float(sum(1 for feat, val in goal.items() if state.get(feat) != val))


# =============================================================================
# Path utilities
# =============================================================================


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


@dataclass(frozen=True)
class SubgoalSolveResult:
    """Result of solving a problem with subgoals."""

    solved: bool
    total_plan: Optional[List[str]]
    total_cost: Optional[float]
    total_expanded: int
    total_seconds: float
    subgoal_results: List[SolveResult]
    paths: List[object]


def solve_with_subgoals(
    domain: STRIPS_domain,
    initial_state: StateAssignment,
    subgoals: SubgoalList,
    heur: Optional[Heuristic] = None,
) -> SubgoalSolveResult:
    """Solve a planning problem by decomposing it into subgoals.

    Args:
        domain: The STRIPS domain
        initial_state: Starting state assignment
        subgoals: List of subgoal dicts to achieve in order
        heur: Optional heuristic function

    Returns:
        SubgoalSolveResult with combined plan from all subgoals
    """
    current_state = dict(initial_state)
    total_plan: List[str] = []
    total_cost = 0.0
    total_expanded = 0
    total_time = 0.0
    subgoal_results: List[SolveResult] = []
    paths: List[object] = []

    for i, subgoal in enumerate(subgoals):
        # Create a sub-problem from current state to this subgoal
        sub_problem = Planning_problem(domain, current_state, subgoal)

        # Solve this sub-problem
        result = solve_forward(sub_problem, heur=heur)
        subgoal_results.append(result)

        if not result.solved:
            return SubgoalSolveResult(
                solved=False,
                total_plan=None,
                total_cost=None,
                total_expanded=total_expanded + result.expanded,
                total_seconds=total_time + result.seconds,
                subgoal_results=subgoal_results,
                paths=paths,
            )

        # Accumulate results
        if result.plan:
            total_plan.extend(result.plan)
        if result.cost is not None:
            total_cost += result.cost
        total_expanded += result.expanded
        total_time += result.seconds
        if result.path is not None:
            paths.append(result.path)

        # Update current state to the final state after this subgoal
        if result.path is not None:
            final_states = extract_state_assignments(result.path)
            if final_states:
                current_state = dict(final_states[-1])

    return SubgoalSolveResult(
        solved=True,
        total_plan=total_plan,
        total_cost=total_cost,
        total_expanded=total_expanded,
        total_seconds=total_time,
        subgoal_results=subgoal_results,
        paths=paths,
    )
