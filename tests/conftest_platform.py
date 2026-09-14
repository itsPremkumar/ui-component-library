"""Conftest for workspace tests."""
import sys
from pathlib import Path

# Add workspace root and src/ to sys.path so all modules resolve
_WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
_REPO_ROOT = _WORKSPACE_ROOT.parent  # it-company-ops/

for p in (_WORKSPACE_ROOT, _REPO_ROOT, _REPO_ROOT / "src"):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)
