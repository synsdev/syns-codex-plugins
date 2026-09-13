#!/usr/bin/env python3
"""Render a self-contained Syns structure review from JSON data."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any


def esc(value: Any) -> str:
    return html.escape(str(value if value is not None else ""))


def rows(items: list[dict[str, Any]], cells: list[tuple[str, str]]) -> str:
    rendered = []
    for item in items:
        rendered.append("<tr>" + "".join(f'<td data-label="{esc(label)}">{esc(item.get(key, ""))}</td>' for key, label in cells) + "</tr>")
    return "".join(rendered) or f'<tr><td colspan="{len(cells)}"><em>None</em></td></tr>'


def bullets(items: list[Any], empty: str = "None recorded") -> str:
    return "".join(f"<li>{esc(x)}</li>" for x in items) or f"<li>{esc(empty)}</li>"


def key_values(value: Any) -> str:
    if isinstance(value, dict):
        return "".join(f'<div><strong>{esc(k)}</strong><span>{esc(v)}</span></div>' for k, v in value.items())
    if isinstance(value, list):
        return "".join(f'<div><span>{esc(v)}</span></div>' for v in value)
    return f'<div><span>{esc(value)}</span></div>'


def facts(value: Any) -> str:
    if isinstance(value, dict):
        return "".join(f'<article><strong>{esc(k)}</strong><p>{esc(v)}</p></article>' for k, v in value.items())
    if isinstance(value, list):
        return "".join(f'<article><p>{esc(v)}</p></article>' for v in value)
    return f'<article><p>{esc(value)}</p></article>'


def tree(items: list[dict[str, Any]]) -> str:
    rendered = []
    current_band = None
    for item in items:
        band = item.get("band", "Repository")
        if band != current_band:
            rendered.append(f'<li class="tree-band"><span>{esc(band)}</span></li>')
            current_band = band
        origin = esc(item.get("origin", "neutral"))
        sources = item.get("sources", [])
        if isinstance(sources, list):
            sources = " · ".join(map(str, sources))
        materialization = item.get("materialization", {})
        if isinstance(materialization, dict):
            kind = materialization.get("kind", "")
            digest = materialization.get("content_sha256", "")
            materialization = f"{kind}{' · ' + str(digest) if digest else ''}" if kind else ""
        lineage = " · ".join(x for x in (str(sources), str(materialization)) if x)
        rendered.append(
            f'<li class="tree-row origin-{origin}">'
            f'<code>{esc(item.get("path"))}</code>'
            f'<span>{esc(item.get("question"))}</span>'
            f'<span>{origin}</span>'
            f'<small>{esc(lineage)}</small>'
            "</li>"
        )
    return "".join(rendered) or '<li class="tree-row"><em>No paths proposed</em></li>'


def validate(data: dict[str, Any]) -> None:
    source_paths = {str(x.get("path")) for x in data.get("sources", [])}
    mapped = {str(x.get("old")) for x in data.get("mapping", [])}
    missing = source_paths - mapped
    if missing:
        raise ValueError(f"every inventoried source needs a mapping disposition; missing: {', '.join(sorted(missing))}")
    allowed = {"exact-content", "copy", "exact-patch", "empty-directory-slot"}
    tree_items = data.get("tree", [])
    missing_materialization = []
    for item in tree_items:
        materialization = item.get("materialization")
        if not isinstance(materialization, dict) or materialization.get("kind") not in allowed:
            missing_materialization.append(str(item.get("path")))
            continue
        if materialization["kind"] != "empty-directory-slot" and not re.fullmatch(r"[0-9a-f]{64}", str(materialization.get("content_sha256", ""))):
            missing_materialization.append(str(item.get("path")))
    if missing_materialization:
        raise ValueError("exact materialization missing or unbound: " + ", ".join(missing_materialization))


def render(data: dict[str, Any], template: str) -> str:
    validate(data)
    digests = data.get("digests", {})
    digest_html = "".join(f'<div><span>{esc(k)}</span><code>{esc(v)}</code></div>' for k, v in digests.items())
    candidates = rows(data.get("candidates", []), [("reference", "Reference"), ("mode", "Mode"), ("decision", "Decision"), ("reason", "Reason")])
    mapping = rows(data.get("mapping", []), [("old", "Current"), ("action", "Action"), ("new", "Proposed"), ("reason", "Reason")])
    unknowns = bullets(data.get("unknowns", []))
    omissions = bullets(data.get("omissions", []))
    fact_owners = rows(data.get("fact_owners", []), [("domain", "Domain / fact"), ("owner", "Canonical owner"), ("derived", "Derived in memory / elsewhere")])
    validation = rows(data.get("validation", []), [("check", "Check"), ("expected", "Expected result"), ("scope", "Scope")])
    plan = key_values(data.get("evaluation_plan", {}))
    replacements = {
        "{{TITLE}}": esc(data.get("title", "Proposed Syns repository")),
        "{{SUMMARY}}": esc(data.get("summary", "Review the exact repository package before any files are written.")),
        "{{DISCLOSURE}}": esc(data.get("disclosure", "")),
        "{{DIGESTS}}": digest_html,
        "{{SOURCES}}": rows(data.get("sources", []), [("path", "Source"), ("kind", "Kind"), ("disposition", "Disposition")]),
        "{{WORK_MODEL}}": facts(data.get("work_model", {"Status": "Not established"})),
        "{{HISTORY}}": rows(data.get("history", []), [("evidence", "History evidence"), ("interpretation", "Interpretation"), ("limit", "Limit")]),
        "{{SYNS_REPOSITORIES}}": rows(data.get("syns_repositories", []), [("repository", "Repository"), ("decision", "Decision"), ("reason", "Reason"), ("boundary", "Boundary")]),
        "{{CANDIDATES}}": candidates,
        "{{TREE}}": tree(data.get("tree", [])),
        "{{MAPPING}}": mapping,
        "{{UNKNOWNS}}": unknowns,
        "{{OMISSIONS}}": omissions,
        "{{FACT_OWNERS}}": fact_owners,
        "{{VALIDATION}}": validation,
        "{{EVALUATION_PLAN}}": plan,
        "{{FORM_ACTION}}": esc(data.get("form_action", "/decision")),
    }
    for marker, value in replacements.items():
        template = template.replace(marker, value)
    return template


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("data", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--template", type=Path, default=Path(__file__).resolve().parents[1] / "assets" / "structure-review-template.html")
    args = parser.parse_args()
    data = json.loads(args.data.read_text())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(data, args.template.read_text()))
    print(args.output)


if __name__ == "__main__":
    main()
