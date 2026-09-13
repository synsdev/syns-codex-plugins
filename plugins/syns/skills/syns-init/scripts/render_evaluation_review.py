#!/usr/bin/env python3
"""Render a self-contained blind/reveal Syns package-comparison review."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

DIMENSIONS = [
    ("accuracy", "Accuracy"),
    ("completeness", "Completeness"),
    ("grounding", "Grounding"),
    ("uncertainty", "Uncertainty"),
    ("usability", "Usability"),
]


def esc(value: Any) -> str:
    return html.escape(str(value if value is not None else ""))


def answer(label: str, item: dict[str, Any]) -> str:
    citations = item.get("citations", [])
    evidence = "".join(f"<li><code>{esc(c.get('alias', 'S?'))}</code> {esc(c.get('excerpt', ''))}</li>" for c in citations)
    return (
        '<article class="answer">'
        f'<div class="answer-title"><span>{label}</span><h3>Answer {label}</h3></div>'
        f'<div class="answer-body"><pre>{esc(item.get("answer", ""))}</pre></div>'
        f'<div class="evidence"><p class="label">Aliased evidence</p><ul>{evidence or "<li>No citations supplied</li>"}</ul></div>'
        "</article>"
    )


def dimension_controls(index: int, label: str) -> str:
    return "".join(
        f'<label>{esc(title)} {label}<select name="task_{index}_{key}_{label.lower()}" form="evaluation-form">'
        '<option value="">—</option><option value="0">0</option><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option></select></label>'
        for key, title in DIMENSIONS
    )


def blind_pairs(items: list[dict[str, Any]]) -> str:
    rendered = []
    for i, item in enumerate(items, 1):
        rendered.append(
            '<article class="pair">'
            f'<header class="pair-head"><b>Task {i:02d}</b><div><h3>{esc(item.get("task", f"Task {i}"))}</h3><p>{esc(item.get("prompt", ""))}</p></div></header>'
            f'<div class="answers">{answer("A", item.get("A", {}))}{answer("B", item.get("B", {}))}</div>'
            '<div class="pair-form">'
            '<fieldset><legend>Pair preference</legend><div class="winner-options">'
            f'<label><input type="radio" name="task_{i}_preference" value="A" form="evaluation-form">A wins</label>'
            f'<label><input type="radio" name="task_{i}_preference" value="B" form="evaluation-form">B wins</label>'
            f'<label><input type="radio" name="task_{i}_preference" value="tie" form="evaluation-form">Tie</label>'
            f'<label><input type="radio" name="task_{i}_preference" value="unscorable" form="evaluation-form">Unscorable</label>'
            f'</div><div class="rubric">{dimension_controls(i, "A")}</div><div class="rubric">{dimension_controls(i, "B")}</div></fieldset>'
            '<fieldset><legend>Review controls</legend><div class="control-stack">'
            f'<label>Confidence<select name="task_{i}_confidence" form="evaluation-form"><option value="">—</option><option>Low</option><option>Medium</option><option>High</option></select></label>'
            f'<label class="checkline"><input name="task_{i}_leakage" type="checkbox" form="evaluation-form"> Identity leakage</label>'
            f'<label class="wide">Comment<textarea name="task_{i}_comment" form="evaluation-form"></textarea></label>'
            "</div></fieldset></div></article>"
        )
    return "".join(rendered) or "<p>No valid task pairs.</p>"


def reveal(data: dict[str, Any]) -> str:
    metrics = data.get("metrics", [])
    rows = []
    for item in metrics:
        old, proposed = item.get("old"), item.get("proposed")
        old = '<span class="empty-timing">null · not observed</span>' if old is None else esc(old)
        proposed = '<span class="empty-timing">null · not observed</span>' if proposed is None else esc(proposed)
        rows.append(f'<tr><th scope="row">{esc(item.get("metric"))}</th><td>{old}</td><td>{proposed}</td><td>{esc(item.get("note", ""))}</td></tr>')
    caveats = "".join(f"<li>{esc(x)}</li>" for x in data.get("caveats", [])) or "<li>None recorded</li>"
    details = data.get("details", {})
    detail_html = "".join(f'<article><strong>{esc(k)}</strong><p>{esc(v)}</p></article>' for k, v in details.items())
    result = (
        '<div class="condition-key">'
        f'<article><b>A</b><strong>{esc(data.get("condition_a", "Current package"))}</strong><p>{esc(data.get("condition_a_detail", "Immutable current package"))}</p></article>'
        f'<article><b>B</b><strong>{esc(data.get("condition_b", "Proposed package"))}</strong><p>{esc(data.get("condition_b_detail", "Same source plus staged wiki and declared routing"))}</p></article></div>'
        '<p class="scroll-label" id="reveal-table-label"><span>Quality, checks, task/category outcomes, and timing</span><span>Scroll table →</span></p>'
        '<div class="scroll-region" role="region" aria-labelledby="reveal-table-label" tabindex="0"><table><thead><tr><th>Metric</th><th>Current</th><th>Proposed</th><th>Note</th></tr></thead>'
        f'<tbody>{"".join(rows) or "<tr><td colspan=\"4\">No reveal metrics supplied</td></tr>"}</tbody></table></div>'
    )
    if detail_html:
        result += f'<div class="coverage-grid">{detail_html}</div>'
    result += f'<div class="note"><h3>Limits and deviations</h3><ul>{caveats}</ul></div>'
    return result


def operation(data: dict[str, Any]) -> str:
    items = data.get("operations", [])
    lis = "".join(f'<li><code>{esc(x.get("action"))}</code> {esc(x.get("path"))} <small>{esc(x.get("detail", ""))}</small></li>' for x in items)
    return f'<ul class="manifest-list">{lis or "<li>No operation manifest yet.</li>"}</ul>'


def validate(data: dict[str, Any]) -> None:
    pairs = data.get("pairs", [])
    declared = data.get("protocol", {}).get("valid_pairs")
    if declared is not None and int(declared) != len(pairs):
        raise ValueError(f"protocol declares {declared} valid pairs but renderer received {len(pairs)}")
    required = {"model", "harness", "network", "tools", "timing_coverage", "source_mutation", "source_digest", "stage_digest", "operation_digest"}
    missing = required - set(data.get("protocol", {}))
    if missing:
        raise ValueError(f"protocol missing required keys: {', '.join(sorted(missing))}")
    for pair in pairs:
        for condition in ("A", "B"):
            for citation in pair.get(condition, {}).get("citations", []):
                alias = str(citation.get("alias", ""))
                if not alias or "/" in alias or ".md" in alias:
                    raise ValueError("blind citations must use opaque aliases, never real paths")


def render(data: dict[str, Any], template: str) -> str:
    validate(data)
    protocol = data.get("protocol", {})
    protocol_html = "".join(f'<div><span>{esc(k.replace("_", " "))}</span><strong>{esc(v if v is not None else "null · not observed")}</strong></div>' for k, v in protocol.items())
    replacements = {
        "{{TITLE}}": esc(data.get("title", "Current versus proposed repository package")),
        "{{DISCLOSURE}}": esc(data.get("disclosure", "")),
        "{{PROTOCOL}}": protocol_html,
        "{{BLIND_PAIRS}}": blind_pairs(data.get("pairs", [])),
        "{{REVEAL}}": reveal(data.get("reveal", {})),
        "{{OPERATION_MANIFEST}}": operation(data),
        "{{FORM_ACTION}}": esc(data.get("form_action", "/decision")),
    }
    for marker, value in replacements.items():
        template = template.replace(marker, value)
    return template


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("data", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--template", type=Path, default=Path(__file__).resolve().parents[1] / "assets" / "evaluation-review-template.html")
    args = parser.parse_args()
    data = json.loads(args.data.read_text())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(data, args.template.read_text()))
    print(args.output)


if __name__ == "__main__":
    main()
