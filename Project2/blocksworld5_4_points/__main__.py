"""Entry point for `python -m Project2.blocksworld5_4_points`.

Examples (from repo root):
- Solve all problems and generate visualizations:
    uv run python -m Project2.blocksworld5_4_points --viz
- Solve only problem2 with mismatch heuristic:
    uv run python -m Project2.blocksworld5_4_points --problem problem2 --heur mismatch --viz
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .heuristics import goal_mismatch_heur
from .problems import make_domain, make_problems
from .solve import extract_state_assignments, reachable_state_count, solve_forward
from .viz import save_solution_path_images


def _parse_args(argv=None):
    p = argparse.ArgumentParser(prog="Project2.blocksworld5_4_points")
    p.add_argument("--problem", default="all", help="problem1|problem2|problem3|all")
    p.add_argument("--heur", default="mismatch", help="mismatch|zero")
    p.add_argument("--viz", action="store_true", help="save PNG frames + one PDF for the solution path")
    p.add_argument("--out", default="Project2/blocksworld5_4_points/outputs", help="base output directory")
    p.add_argument("--state-limit", type=int, default=10_000, help="cap when counting reachable states")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = _parse_args(argv)

    domain = make_domain()
    problems = make_problems(domain)

    selected = problems.keys() if args.problem == "all" else [args.problem]
    for name in selected:
        if name not in problems:
            raise SystemExit(f"Unknown problem: {name}. Choose from: {', '.join(problems)}")

    heur = None
    heur_name = "zero"
    if args.heur == "mismatch":
        heur = goal_mismatch_heur
        heur_name = "mismatch"
    elif args.heur == "zero":
        heur = None
        heur_name = "zero"
    else:
        raise SystemExit("--heur must be: mismatch|zero")

    base_out = Path(args.out)

    for name in selected:
        prob = problems[name]
        n_states = reachable_state_count(prob, limit=args.state_limit)
        print(f"{name}: reachable states (<= {args.state_limit} cap) = {n_states}")

        res = solve_forward(prob, heur=heur)
        print(
            f"{name} ({heur_name}): solved={res.solved}, cost={res.cost}, expanded={res.expanded}, time={res.seconds:.3f}s"
        )

        if res.solved and args.viz and res.path is not None:
            states = extract_state_assignments(res.path)
            out_dir = base_out / name / heur_name
            pdf = save_solution_path_images(states, res.plan, out_dir)
            print(f"  wrote {len(states)} frames + {pdf}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
