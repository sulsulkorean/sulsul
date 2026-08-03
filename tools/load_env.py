"""Load local secrets from .env.local / .env into os.environ.

No python-dotenv dependency. Existing shell env wins (never overwrite).
GitHub Actions already injects secrets; those stay untouched.
"""

from __future__ import annotations

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANDIDATES = (".env.local", ".env")


def load_env(root: str | None = None) -> list[str]:
    """Return the filenames that contributed at least one new variable."""
    base = root or ROOT
    loaded = []
    for name in CANDIDATES:
        path = os.path.join(base, name)
        if not os.path.isfile(path):
            continue
        added = 0
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip("'").strip('"')
                if not key or key in os.environ:
                    continue
                os.environ[key] = value
                added += 1
        if added:
            loaded.append(name)
    return loaded
