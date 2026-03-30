#!/usr/bin/env python3
"""Check if Project2/RAPORT.md matches outputs/**/results.json.

This is a lightweight consistency audit:
- Loads canonical results from `Project2/blocksworld5_4_points/outputs/**/results.json`.
- Parses the key Markdown tables in `Project2/RAPORT.md`.
- Compares costs/expanded/reachable_states and times (with the same rounding used in the report).

Exit code:
- 0 if all checks pass
- 1 if any mismatch is found

Usage:
  python Project2/check_report_consistency.py
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "Project2" / "RAPORT.md"
OUTPUTS = ROOT / "Project2" / "blocksworld5_4_points" / "outputs"


@dataclass(frozen=True)
class Std:
    reachable: int
    solved: bool
    cost: int | None
    expanded: int
    seconds: float


@dataclass(frozen=True)
class Sub:
    reachable: int
    solved: bool
    total_cost: int | None
    total_expanded: int
    seconds: float
    num_subgoals: int


def load_outputs() -> tuple[dict[str, dict[str, Std]], dict[str, dict[str, Sub]]]:
    std: dict[str, dict[str, Std]] = {}
    sub: dict[str, dict[str, Sub]] = {}

    for p in sorted(OUTPUTS.rglob("results.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        variant = p.parent.name
        problem = p.parent.parent.name
        mode = data.get("mode")

        if mode == "standard":
            std.setdefault(problem, {})[variant] = Std(
                reachable=int(data["reachable_states"]),
                solved=bool(data["solved"]),
                cost=int(data["cost"]) if data.get("cost") is not None else None,
                expanded=int(data["expanded"]),
                seconds=float(data["time_seconds"]),
            )
        elif mode == "subgoals":
            sub.setdefault(problem, {})[variant] = Sub(
                reachable=int(data["reachable_states"]),
                solved=bool(data["solved"]),
                total_cost=int(data["total_cost"]) if data.get("total_cost") is not None else None,
                total_expanded=int(data["total_expanded"]),
                seconds=float(data["time_seconds"]),
                num_subgoals=int(data.get("num_subgoals", 0)),
            )

    return std, sub


def _slice_after(text: str, marker: str) -> str:
    idx = text.find(marker)
    if idx < 0:
        raise ValueError(f"Marker not found: {marker}")
    return text[idx + len(marker) :]


def extract_md_table(text: str, marker: str) -> list[list[str]]:
    """Extract the first Markdown table appearing after marker.

    Returns rows (excluding header+separator). Cells are stripped.
    """
    chunk = _slice_after(text, marker)

    # Find first line that looks like a table header.
    lines = chunk.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith("|") and ln.count("|") >= 3:
            start = i
            break
    if start is None:
        raise ValueError(f"No table found after marker: {marker}")

    # Read consecutive table lines
    table_lines: list[str] = []
    for ln in lines[start:]:
        if not ln.strip().startswith("|"):
            break
        table_lines.append(ln.strip())

    if len(table_lines) < 3:
        raise ValueError(f"Table too short after marker: {marker}")

    # drop header and separator
    body = table_lines[2:]
    rows: list[list[str]] = []
    for ln in body:
        # split and drop empty first/last caused by leading/trailing |
        parts = [c.strip() for c in ln.split("|")][1:-1]
        rows.append(parts)
    return rows


def print_md_table(headers: list[str], rows: list[list[str]]) -> None:
    print("| " + " | ".join(headers) + " |")
    print("|" + "|".join(["---"] * len(headers)) + "|")
    for r in rows:
        print("| " + " | ".join(r) + " |")


def _tak_nie(v: bool) -> str:
    return "Tak" if v else "Nie"


def _fmt_time(x: float, digits: int) -> str:
    return f"{round(x, digits):.{digits}f}"


def build_outputs_tables(std: dict[str, dict[str, Std]], sub: dict[str, dict[str, Sub]]) -> dict[str, list[list[str]]]:
    """Build canonical tables (as in report) derived from outputs/results.json."""

    tables: dict[str, list[list[str]]] = {}

    # 4.1 small standard
    for variant, key in [("mismatch", "std_mismatch"), ("zero", "std_zero")]:
        rows: list[list[str]] = []
        for p in ["problem1", "problem2", "problem3"]:
            out = std[p][variant]
            rows.append(
                [
                    p,
                    str(out.reachable),
                    _tak_nie(out.solved),
                    str(out.cost if out.cost is not None else "-"),
                    str(out.expanded),
                    _fmt_time(out.seconds, 4),
                ]
            )
        tables[key] = rows

    # reduction table
    red_rows: list[list[str]] = []
    for p in ["problem1", "problem2", "problem3"]:
        z = std[p]["zero"].expanded
        mm = std[p]["mismatch"].expanded
        red = (z - mm) / z * 100.0
        red_rows.append([p, str(z), str(mm), f"{round(red, 1):.1f}%"])
    tables["std_reduction"] = red_rows

    # 4.2 small subgoals
    for variant, key in [("subgoals_mismatch", "sub_mismatch"), ("subgoals_zero", "sub_zero")]:
        rows = []
        for p in ["problem1", "problem2", "problem3"]:
            out = sub[p][variant]
            rows.append(
                [
                    p,
                    str(out.num_subgoals),
                    str(out.total_cost if out.total_cost is not None else "-"),
                    str(out.total_expanded),
                    _fmt_time(out.seconds, 4),
                ]
            )
        tables[key] = rows

    # standard vs subgoals (mismatch)
    comp_rows: list[list[str]] = []
    for p in ["problem1", "problem2", "problem3"]:
        n_std = std[p]["mismatch"].expanded
        n_sub = sub[p]["subgoals_mismatch"].total_expanded
        c_std = std[p]["mismatch"].cost
        c_sub = sub[p]["subgoals_mismatch"].total_cost
        comp_rows.append([p, str(n_std), str(n_sub), str(c_std), str(c_sub)])
    tables["std_vs_sub"] = comp_rows

    # 4.3 large subgoals
    large_ps = ["problem4", "problem5", "problem6"]
    rows_m: list[list[str]] = []
    for p in large_ps:
        out = sub[p]["subgoals_mismatch"]
        rows_m.append(
            [
                p,
                str(out.num_subgoals),
                str(out.total_cost if out.total_cost is not None else "-"),
                str(out.total_expanded),
                _fmt_time(out.seconds, 3),
            ]
        )
    tables["large_mismatch"] = rows_m

    rows_z: list[list[str]] = []
    for p in large_ps:
        out = sub[p]["subgoals_zero"]
        rows_z.append(
            [
                p,
                str(out.num_subgoals),
                "-" if out.total_cost is None else str(out.total_cost),
                str(out.total_expanded),
                _fmt_time(out.seconds, 1),
                "TIMEOUT" if (not out.solved) else "OK",
            ]
        )
    tables["large_zero"] = rows_z

    return tables


def extract_report_tables(report_text: str) -> dict[str, list[list[str]]]:
    tables: dict[str, list[list[str]]] = {}

    tables["std_mismatch"] = extract_md_table(report_text, "#### Heurystyka mismatch")
    tables["std_zero"] = extract_md_table(report_text, "#### Bez heurystyki (zero)")
    tables["std_reduction"] = extract_md_table(report_text, "#### Porównanie - redukcja węzłów dzięki heurystyce")
    tables["sub_mismatch"] = extract_md_table(report_text, "#### Heurystyka mismatch + subgoals")
    tables["sub_zero"] = extract_md_table(report_text, "#### Bez heurystyki (zero) + subgoals")
    tables["std_vs_sub"] = extract_md_table(report_text, "#### Porównanie: standardowy vs subgoals (heurystyka mismatch)")

    chunk = _slice_after(report_text, "### 4.3 Problemy duże")
    tables["large_mismatch"] = extract_md_table(chunk, "#### Heurystyka mismatch + subgoals")
    tables["large_zero"] = extract_md_table(chunk, "#### Bez heurystyki (zero) + subgoals")

    return tables


def as_int(cell: str) -> int:
    return int(cell.strip())


def as_float(cell: str) -> float:
    return float(cell.strip())


def assert_eq(label: str, got: Any, expected: Any, errors: list[str]) -> None:
    if got != expected:
        errors.append(f"{label}: got={got!r} expected={expected!r}")


def check_standard_tables(report_text: str, std: dict[str, dict[str, Std]], errors: list[str]) -> None:
    mismatch_rows = extract_md_table(report_text, "#### Heurystyka mismatch")
    zero_rows = extract_md_table(report_text, "#### Bez heurystyki (zero)")

    def check(rows: list[list[str]], variant: str) -> None:
        for cells in rows:
            # Problem | Stany | Rozwiązany | Koszt | Węzły | Czas
            problem = cells[0]
            reachable = as_int(cells[1])
            solved = cells[2].lower() in {"tak", "y", "yes"}
            cost = as_int(cells[3])
            expanded = as_int(cells[4])
            time_report = as_float(cells[5])

            out = std.get(problem, {}).get(variant)
            if out is None:
                errors.append(f"standard/{variant}: missing outputs for {problem}")
                continue

            assert_eq(f"standard/{variant}/{problem}.reachable", reachable, out.reachable, errors)
            assert_eq(f"standard/{variant}/{problem}.solved", solved, out.solved, errors)
            assert_eq(f"standard/{variant}/{problem}.cost", cost, out.cost, errors)
            assert_eq(f"standard/{variant}/{problem}.expanded", expanded, out.expanded, errors)

            # Report stores time rounded to 4 decimals for small problems
            time_expected = round(out.seconds, 4)
            assert_eq(f"standard/{variant}/{problem}.time", time_report, time_expected, errors)

    check(mismatch_rows, "mismatch")
    check(zero_rows, "zero")

    # Reduction table
    red_rows = extract_md_table(report_text, "#### Porównanie - redukcja węzłów dzięki heurystyce")
    for cells in red_rows:
        problem = cells[0]
        zero_nodes = as_int(cells[1])
        mm_nodes = as_int(cells[2])
        red_cell = cells[3].strip().replace("%", "")
        red_report = float(red_cell)

        out_zero = std.get(problem, {}).get("zero")
        out_mm = std.get(problem, {}).get("mismatch")
        if out_zero is None or out_mm is None:
            errors.append(f"reduction: missing outputs for {problem}")
            continue

        assert_eq(f"reduction/{problem}.zero_nodes", zero_nodes, out_zero.expanded, errors)
        assert_eq(f"reduction/{problem}.mismatch_nodes", mm_nodes, out_mm.expanded, errors)

        reduction = (out_zero.expanded - out_mm.expanded) / out_zero.expanded * 100.0
        red_expected = round(reduction, 1)
        assert_eq(f"reduction/{problem}.percent", red_report, red_expected, errors)

    # Average reduction line
    m = re.search(r"\*\*Średnia redukcja: ([0-9]+\.[0-9]+)%\*\*", report_text)
    if m:
        avg_report = float(m.group(1))
        probs = ["problem1", "problem2", "problem3"]
        vals = []
        for pr in probs:
            z = std.get(pr, {}).get("zero")
            mm = std.get(pr, {}).get("mismatch")
            if z and mm:
                vals.append((z.expanded - mm.expanded) / z.expanded * 100.0)
        if len(vals) == 3:
            avg_expected = round(sum(vals) / 3.0, 1)
            assert_eq("reduction/avg", avg_report, avg_expected, errors)
    else:
        errors.append("Average reduction line not found in report")


def check_subgoals_tables(report_text: str, sub: dict[str, dict[str, Sub]], errors: list[str]) -> None:
    mm_rows = extract_md_table(report_text, "#### Heurystyka mismatch + subgoals")
    z_rows = extract_md_table(report_text, "#### Bez heurystyki (zero) + subgoals")

    def check(rows: list[list[str]], variant: str, time_round: int) -> None:
        for cells in rows:
            # Small subgoals table: Problem | Liczba subgoals | Koszt | Węzły | Czas
            problem = cells[0]
            num_sub = as_int(cells[1])
            cost = as_int(cells[2])
            expanded = as_int(cells[3])
            time_report = as_float(cells[4])

            out = sub.get(problem, {}).get(variant)
            if out is None:
                errors.append(f"subgoals/{variant}: missing outputs for {problem}")
                continue

            assert_eq(f"subgoals/{variant}/{problem}.num_subgoals", num_sub, out.num_subgoals, errors)
            assert_eq(f"subgoals/{variant}/{problem}.cost", cost, out.total_cost, errors)
            assert_eq(f"subgoals/{variant}/{problem}.expanded", expanded, out.total_expanded, errors)

            time_expected = round(out.seconds, time_round)
            assert_eq(f"subgoals/{variant}/{problem}.time", time_report, time_expected, errors)

    # For small problems report uses 4 decimals
    check(mm_rows, "subgoals_mismatch", time_round=4)
    check(z_rows, "subgoals_zero", time_round=4)

    # Standard vs subgoals comparison table
    comp_rows = extract_md_table(report_text, "#### Porównanie: standardowy vs subgoals (heurystyka mismatch)")
    for cells in comp_rows:
        # Problem | węzły standard | węzły subgoals | koszt standard | koszt subgoals
        problem = cells[0]
        n_std = as_int(cells[1])
        n_sub = as_int(cells[2])
        c_std = as_int(cells[3])
        c_sub = as_int(cells[4])

        out_std = load_outputs_cache[0].get(problem, {}).get("mismatch")
        out_sub = sub.get(problem, {}).get("subgoals_mismatch")
        if out_std is None or out_sub is None:
            errors.append(f"std-vs-sub: missing outputs for {problem}")
            continue

        assert_eq(f"std-vs-sub/{problem}.nodes_std", n_std, out_std.expanded, errors)
        assert_eq(f"std-vs-sub/{problem}.nodes_sub", n_sub, out_sub.total_expanded, errors)
        assert_eq(f"std-vs-sub/{problem}.cost_std", c_std, out_std.cost, errors)
        assert_eq(f"std-vs-sub/{problem}.cost_sub", c_sub, out_sub.total_cost, errors)


def check_large_tables(report_text: str, sub: dict[str, dict[str, Sub]], errors: list[str]) -> None:
    # Large mismatch table marker is the same string; we disambiguate by slicing after 4.3 section.
    chunk = _slice_after(report_text, "### 4.3 Problemy duże")
    mm_rows = extract_md_table(chunk, "#### Heurystyka mismatch + subgoals")
    z_rows = extract_md_table(chunk, "#### Bez heurystyki (zero) + subgoals")

    for cells in mm_rows:
        # Problem | Liczba subgoals | Koszt | Węzły | Czas
        problem = cells[0]
        num_sub = as_int(cells[1])
        cost = as_int(cells[2])
        expanded = as_int(cells[3])
        time_report = as_float(cells[4])

        out = sub.get(problem, {}).get("subgoals_mismatch")
        if out is None:
            errors.append(f"large/mismatch: missing outputs for {problem}")
            continue

        assert_eq(f"large/mismatch/{problem}.num_subgoals", num_sub, out.num_subgoals, errors)
        assert_eq(f"large/mismatch/{problem}.cost", cost, out.total_cost, errors)
        assert_eq(f"large/mismatch/{problem}.expanded", expanded, out.total_expanded, errors)
        # Report uses 3 decimals here
        assert_eq(f"large/mismatch/{problem}.time", time_report, round(out.seconds, 3), errors)

    for cells in z_rows:
        # Problem | Liczba subgoals | Koszt | Węzły | Czas | Status
        problem = cells[0]
        num_sub = as_int(cells[1])
        cost_cell = cells[2].strip()
        expanded = as_int(cells[3])
        time_report = as_float(cells[4])
        status = cells[5].strip().upper()

        out = sub.get(problem, {}).get("subgoals_zero")
        if out is None:
            errors.append(f"large/zero: missing outputs for {problem}")
            continue

        assert_eq(f"large/zero/{problem}.num_subgoals", num_sub, out.num_subgoals, errors)
        # cost is '-' in report on timeout
        if out.total_cost is None:
            assert_eq(f"large/zero/{problem}.cost", cost_cell, "-", errors)
        assert_eq(f"large/zero/{problem}.expanded", expanded, out.total_expanded, errors)
        # Report uses 1 decimal for timeout times
        assert_eq(f"large/zero/{problem}.time", time_report, round(out.seconds, 1), errors)
        assert_eq(f"large/zero/{problem}.status", status, "TIMEOUT", errors)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--show",
        choices=["none", "report", "outputs", "both"],
        default="none",
        help="Print tables: from report, from outputs, or both",
    )
    args = ap.parse_args()

    if not REPORT.exists():
        print(f"Report not found: {REPORT}")
        return 1
    if not OUTPUTS.exists():
        print(f"Outputs not found: {OUTPUTS}")
        return 1

    report_text = REPORT.read_text(encoding="utf-8")

    global load_outputs_cache
    load_outputs_cache = load_outputs()  # (std, sub)
    std, sub = load_outputs_cache

    errors: list[str] = []

    check_standard_tables(report_text, std, errors)
    check_subgoals_tables(report_text, sub, errors)
    check_large_tables(report_text, sub, errors)

    if args.show != "none":
        rep_tables = extract_report_tables(report_text)
        out_tables = build_outputs_tables(std, sub)

        def show_block(src: str, tables: dict[str, list[list[str]]]) -> None:
            print(f"\n=== TABLES FROM {src.upper()} ===\n")

            print("4.1 Standard — mismatch")
            print_md_table(
                ["Problem", "Stany osiągalne", "Rozwiązany", "Koszt (akcje)", "Węzły rozwinięte", "Czas [s]"],
                tables["std_mismatch"],
            )

            print("\n4.1 Standard — zero")
            print_md_table(
                ["Problem", "Stany osiągalne", "Rozwiązany", "Koszt (akcje)", "Węzły rozwinięte", "Czas [s]"],
                tables["std_zero"],
            )

            print("\n4.1 Redukcja węzłów")
            print_md_table(["Problem", "Węzły (zero)", "Węzły (mismatch)", "Redukcja"], tables["std_reduction"])

            print("\n4.2 Subgoals — mismatch")
            print_md_table(
                ["Problem", "Liczba subgoals", "Koszt całkowity", "Węzły rozwinięte", "Czas [s]"],
                tables["sub_mismatch"],
            )

            print("\n4.2 Subgoals — zero")
            print_md_table(
                ["Problem", "Liczba subgoals", "Koszt całkowity", "Węzły rozwinięte", "Czas [s]"],
                tables["sub_zero"],
            )

            print("\n4.2 Standard vs subgoals (mismatch)")
            print_md_table(
                ["Problem", "Węzły (standard)", "Węzły (subgoals)", "Koszt (standard)", "Koszt (subgoals)"],
                tables["std_vs_sub"],
            )

            print("\n4.3 Duże — subgoals+mismatch")
            print_md_table(
                ["Problem", "Liczba subgoals", "Koszt całkowity", "Węzły rozwinięte", "Czas [s]"],
                tables["large_mismatch"],
            )

            print("\n4.3 Duże — subgoals+zero")
            # Report has an extra Status column; outputs table includes it too
            headers = ["Problem", "Liczba subgoals", "Koszt całkowity", "Węzły rozwinięte", "Czas [s]", "Status"]
            print_md_table(headers, tables["large_zero"])

        if args.show in {"report", "both"}:
            show_block("report", rep_tables)
        if args.show in {"outputs", "both"}:
            show_block("outputs", out_tables)

    if errors:
        print("REPORT/OUTPUTS CONSISTENCY: FAIL\n")
        for e in errors:
            print("- " + e)
        return 1

    print("REPORT/OUTPUTS CONSISTENCY: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
