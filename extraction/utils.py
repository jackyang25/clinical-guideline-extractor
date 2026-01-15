"""File I/O utilities."""

from __future__ import annotations

import json
from pathlib import Path


def ensure_dir(path: Path) -> None:
    """Ensure a directory exists."""

    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: object) -> None:
    """Write JSON to disk with stable formatting."""

    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    """Write text to disk."""

    path.write_text(text, encoding="utf-8")
