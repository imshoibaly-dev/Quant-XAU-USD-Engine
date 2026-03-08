"""
sitecustomize.py
-----------------
Python automatically executes this file on interpreter startup,
before any other imports — including in subprocesses and cached functions.

Streamlit Cloud installs packages into:
  /home/adminuser/venv/lib/pythonX.Y/site-packages/

This file lives in the repo root. setup.py installs it via
the packages list, placing it where Python will find it.
"""
import sys
import os
from pathlib import Path

# Find the repo root: walk up from this file until we find config.py
_here = Path(__file__).resolve().parent
_root = _here
for _ in range(6):
    if (_root / "config.py").exists():
        break
    _root = _root.parent
else:
    # Fallback: use this file's directory
    _root = _here

_root_str = str(_root)
if _root_str not in sys.path:
    sys.path.insert(0, _root_str)
