#!/usr/bin/env python3
"""Build byte-identical hosted and plugin syns-init packages from one source."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ["SKILL.md", "catalog.json", "references", "assets", "scripts", "evals", "fixtures"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_package(destination: Path) -> dict[str, str]:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    for name in INCLUDE:
        source = ROOT / name
        target = destination / name
        if source.is_dir():
            shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            shutil.copy2(source, target)
    manifest: dict[str, str] = {}
    for path in sorted(p for p in destination.rglob("*") if p.is_file()):
        rel = path.relative_to(destination).as_posix()
        manifest[rel] = sha256(path)
    (destination / "checksums.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("destinations", nargs="+", type=Path)
    args = parser.parse_args()
    first = None
    for destination in args.destinations:
        manifest = copy_package(destination)
        if first is None:
            first = manifest
        elif manifest != first:
            raise SystemExit(f"package drift: {destination}")
        print(f"{destination}: {len(manifest)} files; SKILL.md {manifest['SKILL.md']}")


if __name__ == "__main__":
    main()
