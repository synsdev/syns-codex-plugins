#!/usr/bin/env python3
"""Collect bounded project-history and accessible Syns-repository context.

The output is evidence for an agent's proposal, not a recommendation. It never
logs in, mutates a repository, or exposes credential-bearing remote URLs.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

MAX_COMMITS = 200
CREDENTIAL_URL = re.compile(r"(https?://)([^/@\s]+)@")


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=30)


def safe_remote(url: str) -> str:
    return CREDENTIAL_URL.sub(r"\1<redacted>@", url.strip())


def git_context(root: Path) -> dict[str, Any]:
    if not shutil.which("git") or run(["git", "rev-parse", "--is-inside-work-tree"], root).returncode:
        return {"available": False, "reason": "not a Git worktree"}
    top = Path(run(["git", "rev-parse", "--show-toplevel"], root).stdout.strip())
    head = run(["git", "rev-parse", "HEAD"], root).stdout.strip()
    remotes_raw = run(["git", "remote", "-v"], root).stdout.splitlines()
    remotes = []
    for line in remotes_raw:
        parts = line.split()
        if len(parts) >= 2:
            item = {"name": parts[0], "url": safe_remote(parts[1])}
            if item not in remotes:
                remotes.append(item)
    fmt = "%H%x1f%aN%x1f%aI%x1f%s"
    history = run(["git", "log", "--all", f"--max-count={MAX_COMMITS}", f"--format={fmt}", "--name-only"], root).stdout
    commits: list[dict[str, Any]] = []
    authors: collections.Counter[str] = collections.Counter()
    paths: collections.Counter[str] = collections.Counter()
    current: dict[str, Any] | None = None
    for line in history.splitlines():
        if "\x1f" in line:
            sha, author, date, subject = line.split("\x1f", 3)
            current = {"sha": sha, "author": author, "date": date, "subject": subject, "paths": []}
            commits.append(current)
            authors[author] += 1
        elif line.strip() and current is not None:
            path = line.strip()
            current["paths"].append(path)
            paths[path] += 1
    submodules = []
    gm = top / ".gitmodules"
    if gm.is_file():
        submodules = [line.strip().split("=", 1)[1].strip() for line in gm.read_text(errors="replace").splitlines() if line.strip().startswith("path") and "=" in line]
    return {
        "available": True,
        "root": str(top),
        "head": head,
        "remotes": remotes,
        "submodules": submodules,
        "bounded_to_commits": MAX_COMMITS,
        "authors": [{"name": k, "commits": v} for k, v in authors.most_common()],
        "frequently_changed_paths": [{"path": k, "commits": v} for k, v in paths.most_common(50)],
        "commits": commits,
        "interpretation_boundary": "Commit subjects and authors are historical evidence. Checked-out files own current behavior; author count does not prove dispatcher count or current team membership.",
    }


def syns_context(root: Path) -> dict[str, Any]:
    if not shutil.which("syns"):
        return {"available": False, "reason": "syns CLI not found"}
    who = run(["syns", "whoami", "--json"], root)
    if who.returncode:
        return {"available": False, "reason": "not authenticated; no login was started for discovery"}
    try:
        identity = json.loads(who.stdout)
    except json.JSONDecodeError:
        identity = {"raw": who.stdout.strip()}
    repositories: list[dict[str, Any]] = []
    offset = 0
    while True:
        result = run(["syns", "repos", "--limit", "100", "--offset", str(offset), "--json"], root)
        if result.returncode:
            return {"available": False, "reason": result.stderr.strip() or "syns repos failed", "identity": identity}
        page = json.loads(result.stdout)
        repositories.extend(page.get("data", []))
        offset += len(page.get("data", []))
        if offset >= int(page.get("total", offset)) or not page.get("data"):
            break
    compact = []
    for item in repositories:
        compact.append({key: item.get(key) for key in ("owner", "name", "description", "commitSha", "status", "tags", "visibility", "role", "fileCount", "updatedAt", "forkedFrom")})
    return {
        "available": True,
        "identity": identity,
        "repositories": compact,
        "interpretation_boundary": "Metadata identifies reuse candidates only. Pull shortlisted repositories into the private run and inspect their files before proposing extend, derive, or merge. Never infer shared authority or collaborators from similar names.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--without-syns", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    payload = {
        "root": str(root),
        "git": git_context(root),
        "syns": {"available": False, "reason": "disabled"} if args.without_syns else syns_context(root),
    }
    text = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
        os.chmod(args.output, 0o600)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
