from __future__ import annotations

import os
import sys


def _ensure_aipython_on_path() -> None:
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    aipython_dir = os.path.join(pkg_dir, "aipython")
    if aipython_dir not in sys.path:
        sys.path.insert(0, aipython_dir)


_ensure_aipython_on_path()
