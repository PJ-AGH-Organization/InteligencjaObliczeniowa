from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Set

import Project2

from stripsProblem import Planning_problem, STRIPS_domain
from stripsForwardPlanner import Forward_STRIPS
from searchMPP import SearcherMPP
from searchProblem import Path


class TimeoutSearcherMPP(SearcherMPP):

    def __init__(self, problem, timeout: Optional[float] = None):
        super().__init__(problem)
        self.timeout = timeout
        self.timed_out = False

    def search(self):
        start_time = time.perf_counter()

        while not self.empty_frontier():
            if self.timeout is not None:
                elapsed = time.perf_counter() - start_time
                if elapsed >= self.timeout:
                    self.timed_out = True
                    return None

            self.path = self.frontier.pop()
            if self.path.end() not in self.explored:
                self.explored.add(self.path.end())
                self.num_expanded += 1
                if self.problem.is_goal(self.path.end()):
                    self.solution = self.path
                    return self.path
                else:
                    neighs = self.problem.neighbors(self.path.end())
                    for arc in neighs:
                        self.add_to_frontier(Path(self.path, arc))

        return None

StateAssignment = Dict[str, object]
Goal = Dict[str, object]
Heuristic = Callable[[StateAssignment, Goal], float]
SubgoalList = List[Goal]

def goal_mismatch_heur(state: StateAssignment, goal: Goal) -> float:
    """Count how many goal conditions are not yet satisfied.

    This heuristic is admissible (never overestimates) because each
    unsatisfied goal requires at least one action to achieve.
    """
    return float(sum(1 for feat, val in goal.items() if state.get(feat) != val))

def extract_action_names(path) -> List[str]:
    actions: List[str] = []
    current = path
    while getattr(current, "arc", None) is not None and current.arc is not None:
        actions.append(str(current.arc.action))
        current = current.initial
    actions.reverse()
    return actions


def extract_state_assignments(path) -> List[StateAssignment]:
    nodes = list(path.nodes())
    nodes.reverse()
    return [getattr(st, "assignment", st) for st in nodes]


def reachable_state_count(problem: Planning_problem, limit: int = 10_000) -> int:
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
    timed_out: bool = False


def solve_forward(
    problem: Planning_problem,
    heur: Optional[Heuristic] = None,
    timeout: Optional[float] = None,
) -> SolveResult:
    if heur is None:
        heur = lambda *_: 0

    sp = Forward_STRIPS(problem, heur=heur)
    searcher = TimeoutSearcherMPP(sp, timeout=timeout)

    t0 = time.perf_counter()
    path = searcher.search()
    dt = time.perf_counter() - t0

    if path is None:
        return SolveResult(
            solved=False,
            plan=None,
            cost=None,
            expanded=searcher.num_expanded,
            seconds=dt,
            path=None,
            timed_out=searcher.timed_out,
        )

    return SolveResult(
        solved=True,
        plan=extract_action_names(path),
        cost=path.cost,
        expanded=searcher.num_expanded,
        seconds=dt,
        path=path,
        timed_out=False,
    )


@dataclass(frozen=True)
class SubgoalSolveResult:

    solved: bool
    total_plan: Optional[List[str]]
    total_cost: Optional[float]
    total_expanded: int
    total_seconds: float
    subgoal_results: List[SolveResult]
    paths: List[object]
    timed_out: bool = False


def solve_with_subgoals(
    domain: STRIPS_domain,
    initial_state: StateAssignment,
    subgoals: SubgoalList,
    heur: Optional[Heuristic] = None,
    timeout: Optional[float] = None,
) -> SubgoalSolveResult:
    start_time = time.perf_counter()
    current_state = dict(initial_state)
    total_plan: List[str] = []
    total_cost = 0.0
    total_expanded = 0
    subgoal_results: List[SolveResult] = []
    paths: List[object] = []

    for i, subgoal in enumerate(subgoals):
        remaining_timeout = None
        if timeout is not None:
            elapsed = time.perf_counter() - start_time
            remaining_timeout = timeout - elapsed
            if remaining_timeout <= 0:
                total_time = time.perf_counter() - start_time
                return SubgoalSolveResult(
                    solved=False,
                    total_plan=None,
                    total_cost=None,
                    total_expanded=total_expanded,
                    total_seconds=total_time,
                    subgoal_results=subgoal_results,
                    paths=paths,
                    timed_out=True,
                )

        sub_problem = Planning_problem(domain, current_state, subgoal)

        result = solve_forward(sub_problem, heur=heur, timeout=remaining_timeout)
        subgoal_results.append(result)

        if not result.solved:
            total_time = time.perf_counter() - start_time
            return SubgoalSolveResult(
                solved=False,
                total_plan=None,
                total_cost=None,
                total_expanded=total_expanded + result.expanded,
                total_seconds=total_time,
                subgoal_results=subgoal_results,
                paths=paths,
                timed_out=result.timed_out,
            )

        if result.plan:
            total_plan.extend(result.plan)
        if result.cost is not None:
            total_cost += result.cost
        total_expanded += result.expanded
        if result.path is not None:
            paths.append(result.path)

        if result.path is not None:
            final_states = extract_state_assignments(result.path)
            if final_states:
                current_state = dict(final_states[-1])

    total_time = time.perf_counter() - start_time
    return SubgoalSolveResult(
        solved=True,
        total_plan=total_plan,
        total_cost=total_cost,
        total_expanded=total_expanded,
        total_seconds=total_time,
        subgoal_results=subgoal_results,
        paths=paths,
        timed_out=False,
    )
