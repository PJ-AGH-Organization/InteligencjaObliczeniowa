"""Entry point for `python -m Project2.blocksworld5_4_points`.

Examples (from repo root):
- Solve all problems and generate visualizations:
    uv run python -m Project2.blocksworld5_4_points --viz
- Solve only problem2 without heuristic:
    uv run python -m Project2.blocksworld5_4_points --problem problem2 --heur zero --viz
- Solve with subgoals (6-point requirement):
    uv run python -m Project2.blocksworld5_4_points --subgoals
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .heuristics import goal_mismatch_heur
from .problems import make_domain, make_problems
from .solve import extract_state_assignments, reachable_state_count, solve_forward, solve_with_subgoals
from .subgoals import get_subgoals
from .viz import save_solution_path_images


def _parse_args(argv=None):
    p = argparse.ArgumentParser(prog="Project2.blocksworld5_4_points")
    p.add_argument("--problem", default="all", help="problem1|problem2|problem3|all")
    p.add_argument("--heur", default="mismatch", help="mismatch|zero")
    p.add_argument("--viz", action="store_true", help="save PNG frames + one PDF for the solution path")
    p.add_argument("--out", default="Project2/blocksworld5_4_points/outputs", help="base output directory")
    p.add_argument("--state-limit", type=int, default=10_000, help="cap when counting reachable states")
    p.add_argument("--subgoals", action="store_true", help="solve with subgoals (6-point requirement)")
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

        if args.subgoals:
            # 6-point requirement: solve with subgoals
            subgoals = get_subgoals(name)
            initial_state = prob.initial_state

            res = solve_with_subgoals(domain, initial_state, subgoals, heur=heur)
            print(f"{name} with subgoals ({heur_name}):")
            print(f"  solved={res.solved}, total_cost={res.total_cost}, total_expanded={res.total_expanded}, time={res.total_seconds:.3f}s")

            if res.solved:
                print(f"  Subgoals breakdown ({len(subgoals)} subgoals):")
                for i, (sg, sr) in enumerate(zip(subgoals, res.subgoal_results), 1):
                    print(f"    Subgoal {i}: cost={sr.cost}, expanded={sr.expanded}, actions={sr.plan}")
                print(f"  Total plan ({len(res.total_plan)} actions): {res.total_plan}")

            if res.solved and args.viz and res.paths:
                # Combine all states from all subgoal paths
                all_states = []
                for path in res.paths:
                    states = extract_state_assignments(path)
                    if all_states:
                        states = states[1:]  # Skip first state (duplicate of previous end)
                    all_states.extend(states)

                out_dir = base_out / name / f"subgoals_{heur_name}"
                pdf = save_solution_path_images(all_states, res.total_plan, out_dir)
                print(f"  wrote {len(all_states)} frames + {pdf}")
        else:
            # Standard solving (4-point requirement)
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
