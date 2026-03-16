"""Matplotlib visualizations for Blocks World states.

We visualize the *solution path* states (start -> goal), not every expanded node.
Producing images for all expanded states is usually enormous.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle

StateAssignment = Dict[str, object]


@dataclass(frozen=True)
class BlocksLayout:
    stacks: List[List[str]]  # bottom->top per stack


def _parse_on_relations(state: StateAssignment) -> Dict[str, str]:
    """Extract mapping block -> support from AIPython blocks world state."""
    on_of: Dict[str, str] = {}
    for key, value in state.items():
        if isinstance(key, str) and key.endswith("_is_on"):
            block = key[: -len("_is_on")]
            if isinstance(value, str):
                on_of[block] = value
    return on_of


def _compute_stacks(on_of: Dict[str, str]) -> BlocksLayout:
    """Compute stacks from on-relations; ignores clear flags."""
    blocks = sorted(on_of.keys())

    # inverse mapping: support -> block on it (there should be at most one)
    above: Dict[str, str] = {}
    for block, support in on_of.items():
        above[support] = block

    stacks: List[List[str]] = []

    # find roots (blocks directly on table)
    roots = [b for b in blocks if on_of.get(b) == "table"]
    roots.sort()

    for root in roots:
        stack = [root]
        current = root
        while current in above:
            nxt = above[current]
            if nxt in stack:
                break
            stack.append(nxt)
            current = nxt
        stacks.append(stack)

    # If a block isn't reachable from any table root (shouldn't happen), place it alone.
    placed = {b for stack in stacks for b in stack}
    for b in blocks:
        if b not in placed:
            stacks.append([b])

    return BlocksLayout(stacks=stacks)


def draw_state(
    state: StateAssignment,
    *,
    title: Optional[str] = None,
    figsize: Tuple[float, float] = (8.0, 3.0),
):
    """Return (fig, ax) visualizing a single blocks-world state."""
    on_of = _parse_on_relations(state)
    layout = _compute_stacks(on_of)

    fig, ax = plt.subplots(figsize=figsize)
    ax.set_axis_off()
    if title:
        ax.set_title(title)

    # simple geometry
    block_w = 1.0
    block_h = 0.6
    gap_x = 0.6
    base_y = 0.4

    # draw table line
    max_stack_h = max((len(s) for s in layout.stacks), default=1)
    width = len(layout.stacks) * (block_w + gap_x) + gap_x
    height = base_y + (max_stack_h + 1) * block_h
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.plot([0, width], [base_y, base_y], linewidth=2)

    for i, stack in enumerate(layout.stacks):
        x0 = gap_x + i * (block_w + gap_x)
        for j, block in enumerate(stack):
            y0 = base_y + j * block_h
            rect = Rectangle((x0, y0), block_w, block_h, fill=False, linewidth=2)
            ax.add_patch(rect)
            ax.text(x0 + block_w / 2, y0 + block_h / 2, block, ha="center", va="center")

    fig.tight_layout()
    return fig, ax


def save_solution_path_images(
    states: Sequence[StateAssignment],
    actions: Optional[Sequence[str]],
    out_dir: Path,
    *,
    pdf_name: str = "solution_path.pdf",
) -> Path:
    """Save PNG frames for each state + a single PDF with all frames.

    states: list of state assignments from start->goal
    actions: list of action names; if provided, len(actions) = len(states)-1
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = out_dir / pdf_name
    with PdfPages(pdf_path) as pdf:
        for idx, st in enumerate(states):
            action_txt = None
            if actions is not None and idx > 0 and (idx - 1) < len(actions):
                action_txt = actions[idx - 1]
            title = f"Step {idx}/{len(states) - 1}"
            if action_txt:
                title += f"  (after: {action_txt})"

            fig, _ = draw_state(st, title=title)

            png_path = out_dir / f"step_{idx:03d}.png"
            fig.savefig(png_path, dpi=160)
            pdf.savefig(fig)
            plt.close(fig)

    return pdf_path
