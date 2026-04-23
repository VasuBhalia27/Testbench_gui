"""Utilities for locating project paths used by automation."""

from pathlib import Path
from typing import Optional


def smartbu_repo_path() -> str:
    """Return the absolute path to the SmartBU directory inside the workspace.

    The repository is assumed to be a sibling of the ``automation`` folder
    (i.e. layout is ``<workspace>/SmartBU``).  This routine does not depend on
    the current working directory and will work regardless of where the
    workspace is checked out (C:, D:, etc.).

    Raises:
        FileNotFoundError: if the directory cannot be located.
    """
    # ``__file__`` points to automation/core/path_utils.py
    current = Path(__file__).resolve()
    # walk upwards until we either hit a workspace root (heuristic) or run out
    for parent in current.parents:
        candidate = parent / "SmartBU"
        if candidate.is_dir():
            return str(candidate)
    # fallback: assume two levels up
    candidate = current.parents[2] / "SmartBU"
    if candidate.is_dir():
        return str(candidate)
    raise FileNotFoundError("SmartBU folder not found relative to automation core")
