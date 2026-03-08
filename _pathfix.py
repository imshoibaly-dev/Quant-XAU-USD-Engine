"""
_pathfix.py
-----------
Imported at the top of every module that uses internal imports.
Guarantees the repo root is on sys.path regardless of how Python
was invoked (Streamlit Cloud, subprocess, cached function, etc.).
"""
import sys
import os
from pathlib import Path

# Walk up from this file's location to find the repo root
# (the directory that contains config.py)
_here = Path(__file__).resolve().parent
_root = _here
for _ in range(5):
    if (_root / "config.py").exists():
        break
    _root = _root.parent

_root_str = str(_root)
if _root_str not in sys.path:
    sys.path.insert(0, _root_str)
os.environ["PYTHONPATH"] = _root_str + os.pathsep + os.environ.get("PYTHONPATH", "")
