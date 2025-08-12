# llm-redteam-sim

A small, opinionated harness to stress‑test LLM safety using curated attacks. Generates JSON + Markdown summaries you can track in CI.

### Highlights
- Provider‑agnostic (OpenAI API or Ollama).  
- Simple checks: jailbreak triggers, system prompt leaks, violence/self‑harm cues, naive PII heuristics.
- Clean CLI, lightweight deps, clear code.

# 1) Clone and install
pip install -e .

# 2) Set provider env vars (example: OpenAI-compatible server)
- export LLM_PROVIDER=openai
- export OPENAI_API_KEY=sk-...
# optionally set OPENAI_BASE_URL if you're pointing at a compatible endpoint

# 3) Run harness
python -m llm_redteam_sim.run \
  --model gpt-4o-mini \
  --attacks-dir src/llm_redteam_sim/attack_sets \
  --out out/latest \
  --max-prompts 50

# 4) Open report
open out/latest/report.md

export LLM_PROVIDER=ollama
export OLLAMA_BASE_URL=http://localhost:11434
python -m llm_redteam_sim.run --model llama3.1:8b --out out/ollama
