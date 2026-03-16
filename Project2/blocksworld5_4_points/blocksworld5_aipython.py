"""Compatibility wrapper.

The code for Blocks World (5 blocks) is split into modules:
- `Project2.blocksworld5.problems`
- `Project2.blocksworld5.solve`
- `Project2.blocksworld5.viz`

You can still run this file as a module:
`uv run python -m Project2.blocksworld5.blocksworld5_aipython`

Preferred entry point (supports `--viz`):
`uv run python -m Project2.blocksworld5`
"""

from __future__ import annotations

from .heuristics import goal_mismatch_heur
from .problems import make_domain, make_problems
from .solve import reachable_state_count, solve_forward

blocks5_domain = make_domain()
_problems = make_problems(blocks5_domain)

# Re-export for convenience/backwards compatibility
problem1 = _problems["problem1"]
problem2 = _problems["problem2"]
problem3 = _problems["problem3"]


def main() -> int:
    for i, prob in enumerate([problem1, problem2, problem3], start=1):
        n = reachable_state_count(prob, limit=10_000)
        print(f"problem{i}: reachable states (<=10k cap) = {n}")

    print("\nForward planning (A*):")
    for i, prob in enumerate([problem1, problem2, problem3], start=1):
        res0 = solve_forward(prob, heur=None)
        print(
            f"problem{i} no-heur: solved={res0.solved}, cost={res0.cost}, expanded={res0.expanded}, time={res0.seconds:.3f}s"
        )

        res1 = solve_forward(prob, heur=goal_mismatch_heur)
        print(
            f"problem{i} mismatch-heur: solved={res1.solved}, cost={res1.cost}, expanded={res1.expanded}, time={res1.seconds:.3f}s"
        )
        if res1.plan is not None:
            print(f"  plan length={len(res1.plan)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
