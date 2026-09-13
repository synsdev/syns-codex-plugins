#!/usr/bin/env python3
"""Create a conservative, content-free source inventory for syns-init."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

EXCLUDED_DIRS = {".git", "node_modules", "dist", "build", "target", ".next", ".nuxt", ".venv", ".tox", ".cache", "__pycache__"}
TEXT_SUFFIXES = {".md", ".mdx", ".txt", ".yaml", ".yml", ".json", ".toml"}
SPECIAL = {"AGENTS.md", "CLAUDE.md", ".syns.yaml"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    records = []
    exclusions = []
    for current, dirs, files in os.walk(root, followlinks=False):
        here = Path(current)
        kept_dirs = []
        for name in sorted(dirs):
            rel = (here / name).relative_to(root).as_posix()
            if name in EXCLUDED_DIRS:
                exclusions.append({"path": rel + "/", "reason": "generated, dependency, cache, or VCS tree"})
            else:
                kept_dirs.append(name)
        dirs[:] = kept_dirs
        for name in sorted(files):
            path = here / name
            rel = path.relative_to(root).as_posix()
            if name.startswith(".env"):
                exclusions.append({"path": rel, "reason": "credential-bearing dotenv file"})
                continue
            if path.is_symlink():
                records.append({"path": rel, "kind": "symlink", "target": os.readlink(path)})
                continue
            is_native = rel.startswith("openspec/") or rel.startswith(".specify/") or rel.startswith("specs/")
            if path.suffix.lower() not in TEXT_SUFFIXES and name not in SPECIAL and not is_native:
                continue
            stat = path.stat()
            records.append({"path": rel, "kind": "text", "bytes": stat.st_size, "sha256": digest(path)})
    result = {"root": str(root), "files": records, "exclusions": exclusions}
    payload = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload)
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
