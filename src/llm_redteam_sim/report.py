from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any
from tabulate import tabulate


@dataclass
class CaseResult:
    attack_set: str
    prompt: str
    response: str
    latency_s: float
    flags: Dict[str, bool]


@dataclass
class RunSummary:
    model: str
    provider: str
    total: int
    flagged: int
    rates: Dict[str, float]


def summarize(results: List[CaseResult], *, model: str, provider: str) -> RunSummary:
    total = len(results)
    counts: Dict[str, int] = {}
    for r in results:
        for k, v in r.flags.items():
            if k == "any_flag":
                continue
            counts[k] = counts.get(k, 0) + int(bool(v))
    flagged = sum(1 for r in results if r.flags.get("any_flag"))
    rates = {k: (counts.get(k, 0) / total if total else 0.0) for k in sorted(counts)}
    return RunSummary(model=model, provider=provider, total=total, flagged=flagged, rates=rates)


def write_json(results: List[CaseResult], out_dir: Path):
    data = [
        {
            "attack_set": r.attack_set,
            "prompt": r.prompt,
            "response": r.response,
            "latency_s": r.latency_s,
            "flags": r.flags,
        }
        for r in results
    ]
    (out_dir / "report.json").write_text(json.dumps(data, indent=2), encoding="utf-8")


def write_markdown(results: List[CaseResult], summary: RunSummary, out_dir: Path, max_examples: int = 8):
    lines = []
    lines.append(f"# llm-redteam-sim report\n")
    lines.append(f"Model: **{summary.model}**  ")
    lines.append(f"Provider: **{summary.provider}**  ")
    lines.append(f"Cases: **{summary.total}**, Flagged: **{summary.flagged}**\n")

    if summary.rates:
        table = [[k, f"{v*100:.1f}%"] for k, v in summary.rates.items()]
        lines.append("## Flag rates\n")
        lines.append(tabulate(table, headers=["check", "rate"], tablefmt="github"))
        lines.append("")

    bad = [r for r in results if r.flags.get("any_flag")]
    if bad:
        lines.append("## Sample flagged responses\n")
        for r in bad[:max_examples]:
            lines.append(f"### {r.attack_set}\n")
            lines.append("**Prompt**:\n")
            lines.append("`````\n" + r.prompt.strip() + "\n`````\n")
            lines.append("**Response**:\n")
            lines.append("`````\n" + (r.response.strip() or "<empty>") + "\n`````\n")
            hit = ", ".join([k for k, v in r.flags.items() if k != "any_flag" and v]) or "<none>"
            lines.append(f"Flags: {hit}\n")
    (out_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")
