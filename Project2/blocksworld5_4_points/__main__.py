"""Entry point for `python -m Project2.blocksworld5_4_points`.

Examples:
- Solve all small problems:     uv run python -m Project2.blocksworld5_4_points
- Solve with subgoals:          uv run python -m Project2.blocksworld5_4_points --subgoals
- Solve large problems:         uv run python -m Project2.blocksworld5_4_points --large --subgoals
- Generate visualizations:      uv run python -m Project2.blocksworld5_4_points --viz
- Without heuristic:            uv run python -m Project2.blocksworld5_4_points --heur zero
- With timeout:                 uv run python -m Project2.blocksworld5_4_points --timeout 300
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .problems import make_domain, make_problems, make_large_domain, make_large_problems, get_subgoals
from .solve import (
    goal_mismatch_heur,
    extract_state_assignments,
    reachable_state_count,
    solve_forward,
    solve_with_subgoals,
)
from .viz import save_solution_path_images


def save_results(out_dir: Path, results: dict[str, Any]) -> Path:
    """Save solve results to JSON file in the output directory."""
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    return json_path


def _parse_args(argv=None):
    p = argparse.ArgumentParser(prog="Project2.blocksworld5_4_points")
    p.add_argument("--problem", default="all", help="problem1|problem2|problem3|all (or problem4|problem5|problem6 with --large)")
    p.add_argument("--heur", default="mismatch", help="mismatch|zero")
    p.add_argument("--viz", action="store_true", help="save PNG frames + one PDF for the solution path")
    p.add_argument("--out", default="Project2/blocksworld5_4_points/outputs", help="base output directory")
    p.add_argument("--state-limit", type=int, default=10_000, help="cap when counting reachable states")
    p.add_argument("--subgoals", action="store_true", help="solve with subgoals (6-point requirement)")
    p.add_argument("--large", action="store_true", help="use large problems with 8 blocks (8-point requirement)")
    p.add_argument("--timeout", type=float, default=None, help="timeout in seconds (default: no timeout)")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = _parse_args(argv)

    # Select domain and problems based on --large flag
    if args.large:
        domain = make_large_domain()
        problems = make_large_problems(domain)
        default_problems = ["problem4", "problem5", "problem6"]
    else:
        domain = make_domain()
        problems = make_problems(domain)
        default_problems = ["problem1", "problem2", "problem3"]

    selected = default_problems if args.problem == "all" else [args.problem]
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

            res = solve_with_subgoals(domain, initial_state, subgoals, heur=heur, timeout=args.timeout)

            status = "TIMEOUT" if res.timed_out else ("solved" if res.solved else "failed")
            print(f"{name} with subgoals ({heur_name}):")
            print(f"  status={status}, total_cost={res.total_cost}, total_expanded={res.total_expanded}, time={res.total_seconds:.3f}s")

            # Prepare results dict
            results: dict[str, Any] = {
                "problem": name,
                "mode": "subgoals",
                "heuristic": heur_name,
                "reachable_states": n_states,
                "reachable_states_limit": args.state_limit,
                "solved": res.solved,
                "timed_out": res.timed_out,
                "timeout_seconds": args.timeout,
                "total_cost": res.total_cost,
                "total_expanded": res.total_expanded,
                "time_seconds": res.total_seconds,
                "num_subgoals": len(subgoals),
                "subgoals_breakdown": [],
                "total_plan": [],
            }

            if res.solved:
                print(f"  Subgoals breakdown ({len(subgoals)} subgoals):")
                for i, (sg, sr) in enumerate(zip(subgoals, res.subgoal_results), 1):
                    print(f"    Subgoal {i}: cost={sr.cost}, expanded={sr.expanded}, actions={sr.plan}")
                    results["subgoals_breakdown"].append({
                        "subgoal_index": i,
                        "cost": sr.cost,
                        "expanded": sr.expanded,
                        "actions": sr.plan,
                    })
                print(f"  Total plan ({len(res.total_plan)} actions): {res.total_plan}")
                results["total_plan"] = res.total_plan

            out_dir = base_out / name / f"subgoals_{heur_name}"
            json_path = save_results(out_dir, results)
            print(f"  wrote results to {json_path}")

            if res.solved and args.viz and res.paths:
                # Combine all states from all subgoal paths
                all_states = []
                for path in res.paths:
                    states = extract_state_assignments(path)
                    if all_states:
                        states = states[1:]  # Skip first state (duplicate of previous end)
                    all_states.extend(states)

                pdf = save_solution_path_images(all_states, res.total_plan, out_dir)
                print(f"  wrote {len(all_states)} frames + {pdf}")
        else:
            # Standard solving (4-point requirement)
            res = solve_forward(prob, heur=heur, timeout=args.timeout)

            status = "TIMEOUT" if res.timed_out else ("solved" if res.solved else "failed")
            print(
                f"{name} ({heur_name}): status={status}, cost={res.cost}, expanded={res.expanded}, time={res.seconds:.3f}s"
            )

            # Prepare results dict
            results: dict[str, Any] = {
                "problem": name,
                "mode": "standard",
                "heuristic": heur_name,
                "reachable_states": n_states,
                "reachable_states_limit": args.state_limit,
                "solved": res.solved,
                "timed_out": res.timed_out,
                "timeout_seconds": args.timeout,
                "cost": res.cost,
                "expanded": res.expanded,
                "time_seconds": res.seconds,
                "plan": res.plan if res.solved else [],
            }

            out_dir = base_out / name / heur_name
            json_path = save_results(out_dir, results)
            print(f"  wrote results to {json_path}")

            if res.solved and args.viz and res.path is not None:
                states = extract_state_assignments(res.path)
                pdf = save_solution_path_images(states, res.plan, out_dir)
                print(f"  wrote {len(states)} frames + {pdf}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
