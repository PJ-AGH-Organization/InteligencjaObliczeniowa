"""Project2 package bootstrap.

This repository vendors the AIPython code under `Project2/aipython/`.
Those modules use *top-level* imports like `from stripsProblem import ...`.

To keep them working when importing from `Project2.*`, we ensure that
`Project2/aipython/` is on `sys.path`.
"""

from __future__ import annotations

import os
import sys


def _ensure_aipython_on_path() -> None:
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    aipython_dir = os.path.join(pkg_dir, "aipython")
    if aipython_dir not in sys.path:
        sys.path.insert(0, aipython_dir)


_ensure_aipython_on_path()
