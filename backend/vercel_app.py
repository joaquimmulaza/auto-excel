"""Vercel FastAPI entrypoint (service root = backend/).

Registers a synthetic ``backend`` package pointing at this directory so the
existing ``backend.app.*`` imports keep working when only ``backend/`` is
deployed as a Vercel service.
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

_root = Path(__file__).resolve().parent
if "backend" not in sys.modules:
    _pkg = types.ModuleType("backend")
    _pkg.__path__ = [str(_root)]  # type: ignore[attr-defined]
    sys.modules["backend"] = _pkg

from backend.app.main import app  # noqa: E402

__all__ = ["app"]
