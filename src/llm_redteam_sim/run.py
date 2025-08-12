from __future__ import annotations
import argparse
import os
from pathlib import Path
from typing import List
from rich.progress import track

from .clients import get_client
from .checks import analyze
from .report import CaseResult, summarize, write_json, write_markdown


def load_prompts(path: Path, max_prompts: int | None = None) -> List[str]:
    raw = path.read_text(encoding="utf-8").splitlines()
    prompts: List[str] = []
    for line in raw:
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        prompts.append(s)
        if max_prompts and len(prompts) >= max_prompts:
            break
    return prompts


def main():
    ap = argparse.ArgumentParser(description="Run LLM red-team harness")
    ap.add_argument("--model", required=True)
    ap.add_argument("--attacks-dir", default=str(Path(__file__).parent / "attack_sets"))
    ap.add_argument("--out", default="out/latest")
    ap.add_argument("--system", default=None)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--max-prompts", type=int, default=0, help="limit prompts per file (0 = all)")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    client = get_client()
    provider = os.environ.get("LLM_PROVIDER", "openai")

    results: List[CaseResult] = []
    attacks_dir = Path(args.attacks_dir)
    files = sorted(p for p in attacks_dir.glob("*.txt"))

    for f in files:
        prompts = load_prompts(f, None if args.max_prompts <= 0 else args.max_prompts)
        for p in track(prompts, description=f"{f.name}"):
            r = client.generate(p, system=args.system, model=args.model, temperature=args.temperature)
            flags = analyze(r.text)
            results.append(CaseResult(
                attack_set=f.name,
                prompt=p,
                response=r.text,
                latency_s=r.latency_s,
                flags=flags,
            ))

    summary = summarize(results, model=args.model, provider=provider)
    write_json(results, out_dir)
    write_markdown(results, summary, out_dir)


if __name__ == "__main__":
    main()
