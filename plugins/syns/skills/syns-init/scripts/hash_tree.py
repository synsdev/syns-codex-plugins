#!/usr/bin/env python3
"""Hash paths and file bytes deterministically without following symlinks."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path

EXCLUDE = {".git", "node_modules", ".cache", "__pycache__"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    h = hashlib.sha256()
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDE)
        here = Path(current)
        for name in sorted(files):
            path = here / name
            rel = path.relative_to(root).as_posix().encode()
            h.update(b"P\0" + rel + b"\0")
            if path.is_symlink():
                h.update(b"L\0" + os.readlink(path).encode() + b"\0")
            else:
                h.update(b"F\0")
                with path.open("rb") as fh:
                    for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                        h.update(chunk)
                h.update(b"\0")
    print(h.hexdigest())


if __name__ == "__main__":
    main()
