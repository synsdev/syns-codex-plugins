#!/usr/bin/env python3
"""Verify package files against checksums.json."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    package = args.package
    manifest = json.loads((package / "checksums.json").read_text())
    errors = []
    for rel, expected in manifest.items():
        path = package / rel
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        if actual != expected:
            errors.append(f"{rel}: expected {expected}, got {actual}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"verified {len(manifest)} files; SKILL.md {manifest['SKILL.md']}")


if __name__ == "__main__":
    main()
