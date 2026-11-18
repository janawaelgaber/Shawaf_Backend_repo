"""SCRUM-120. Prints repo_tree as JSON: {"paths": [...]} and exits 1 if the layout is wrong.

Run from anywhere:  python scripts/repo_tree.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "apps/web",
    "apps/backend/src",
    "ai/api",
    "ai/workers",
    "ai/packages",
    "deployment",
    "contracts",
    ".github/workflows/backend.yml",
]
FORBIDDEN = ["apps/api", "apps/ml-api", "apps/worker"]


def main() -> int:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    forbidden = [p for p in FORBIDDEN if (ROOT / p).exists()]
    print(json.dumps({"paths": [p for p in REQUIRED if p not in missing]}, indent=2))
    for p in missing:
        print(f"MISSING: {p}", file=sys.stderr)
    for p in forbidden:
        print(f"FORBIDDEN: {p}", file=sys.stderr)
    return 1 if missing or forbidden else 0


if __name__ == "__main__":
    raise SystemExit(main())
