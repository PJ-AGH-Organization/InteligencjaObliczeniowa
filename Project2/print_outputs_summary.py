#!/usr/bin/env python3
"""Print a concise summary of results stored under blocksworld outputs/.

Reads all `results.json` files under the given base directory (default:
`Project2/blocksworld5_4_points/outputs`) and prints a table.

Usage:
  python Project2/print_outputs_summary.py
  python Project2/print_outputs_summary.py --base Project2/blocksworld5_4_points/outputs
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class Row:
    problem: str
    variant: str
    mode: str
    heuristic: str
    solved: bool
    timed_out: bool
    cost: float | None
    expanded: int | None
    seconds: float | None
    plan_len: int | None


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _iter_results(base: Path) -> Iterable[tuple[Path, dict[str, Any]]]:
    for p in sorted(base.rglob("results.json")):
        try:
            yield p, _read_json(p)
        except Exception as e:  # pragma: no cover
            raise RuntimeError(f"Failed to read {p}: {e}") from e


def _to_row(problem: str, variant: str, data: dict[str, Any]) -> Row:
    mode = str(data.get("mode", ""))
    heuristic = str(data.get("heuristic", ""))
    solved = bool(data.get("solved", False))
    timed_out = bool(data.get("timed_out", False))

    if mode == "standard":
        cost = data.get("cost")
        expanded = data.get("expanded")
        seconds = data.get("time_seconds")
        plan = data.get("plan") or []
        plan_len = len(plan) if solved else 0
    elif mode == "subgoals":
        cost = data.get("total_cost")
        expanded = data.get("total_expanded")
        seconds = data.get("time_seconds")
        plan = data.get("total_plan") or []
        plan_len = len(plan) if solved else 0
    else:
        cost = data.get("cost")
        expanded = data.get("expanded")
        seconds = data.get("time_seconds")
        plan_len = None

    return Row(
        problem=problem,
        variant=variant,
        mode=mode,
        heuristic=heuristic,
        solved=solved,
        timed_out=timed_out,
        cost=float(cost) if cost is not None else None,
        expanded=int(expanded) if expanded is not None else None,
        seconds=float(seconds) if seconds is not None else None,
        plan_len=int(plan_len) if plan_len is not None else None,
    )


def _fmt_float(x: float | None, digits: int = 3) -> str:
    if x is None:
        return "-"
    return f"{x:.{digits}f}"


def _fmt_int(x: int | None) -> str:
    return "-" if x is None else str(x)


def _print_table(rows: list[Row]) -> None:
    headers = [
        "problem",
        "variant",
        "mode",
        "heur",
        "solved",
        "timeout",
        "cost",
        "expanded",
        "time[s]",
        "plan",
    ]

    cells: list[list[str]] = []
    for r in rows:
        cells.append(
            [
                r.problem,
                r.variant,
                r.mode,
                r.heuristic,
                "Y" if r.solved else "N",
                "Y" if r.timed_out else "N",
                _fmt_float(r.cost, digits=0) if r.cost is not None and abs(r.cost - round(r.cost)) < 1e-9 else _fmt_float(r.cost, digits=1),
                _fmt_int(r.expanded),
                _fmt_float(r.seconds, digits=3),
                _fmt_int(r.plan_len),
            ]
        )

    col_widths = [len(h) for h in headers]
    for row in cells:
        for i, c in enumerate(row):
            col_widths[i] = max(col_widths[i], len(c))

    def fmt_row(row: list[str]) -> str:
        return "  ".join(c.ljust(col_widths[i]) for i, c in enumerate(row))

    print(fmt_row(headers))
    print("  ".join("-" * w for w in col_widths))
    for row in cells:
        print(fmt_row(row))


def _comparison_block(rows: list[Row], mode: str, mismatch_variant: str, zero_variant: str) -> None:
    by_problem: dict[str, dict[str, Row]] = {}
    for r in rows:
        if r.mode != mode:
            continue
        by_problem.setdefault(r.problem, {})[r.variant] = r

    pairs = []
    for problem, m in by_problem.items():
        if mismatch_variant in m and zero_variant in m:
            pairs.append((problem, m[mismatch_variant], m[zero_variant]))

    if not pairs:
        return

    print(f"\nComparison ({mode}): {mismatch_variant} vs {zero_variant}")
    print("problem  expanded_zero  expanded_mismatch  reduction[%]  time_zero[s]  time_mismatch[s]  speedup")
    print("-------  ------------  ----------------  -----------  -----------  ---------------  -------")

    for problem, mm, zz in sorted(pairs, key=lambda x: x[0]):
        if (zz.expanded is None) or (mm.expanded is None) or zz.expanded == 0:
            red = None
        else:
            red = (zz.expanded - mm.expanded) / zz.expanded * 100.0

        if (zz.seconds is None) or (mm.seconds is None) or mm.seconds == 0:
            speedup = None
        else:
            speedup = zz.seconds / mm.seconds

        print(
            f"{problem:<7}  {str(zz.expanded):>12}  {str(mm.expanded):>16}  "
            f"{('-' if red is None else f'{red:>10.1f}')}  "
            f"{_fmt_float(zz.seconds, 3):>11}  {_fmt_float(mm.seconds, 3):>15}  "
            f"{('-' if speedup is None else f'{speedup:>7.1f}') }"
        )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--base",
        default="Project2/blocksworld5_4_points/outputs",
        help="Base directory containing problem*/.../results.json",
    )
    args = ap.parse_args()

    base = Path(args.base)
    if not base.exists():
        raise SystemExit(f"Base directory not found: {base}")

    rows: list[Row] = []
    for path, data in _iter_results(base):
        # expected structure: <base>/problemX/<variant>/results.json
        try:
            variant = path.parent.name
            problem = path.parent.parent.name
        except Exception:
            continue
        rows.append(_to_row(problem=problem, variant=variant, data=data))

    if not rows:
        print(f"No results.json found under: {base}")
        return 0

    rows.sort(key=lambda r: (r.problem, r.mode, r.variant))
    _print_table(rows)

    # Standard comparisons
    _comparison_block(rows, mode="standard", mismatch_variant="mismatch", zero_variant="zero")
    # Subgoals comparisons
    _comparison_block(rows, mode="subgoals", mismatch_variant="subgoals_mismatch", zero_variant="subgoals_zero")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
