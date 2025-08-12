.PHONY: run test fmt lint

run:
	python -m llm_redteam_sim.run --model $$MODEL --out out/latest

test:
	pytest -q

fmt:
	ruff check --fix src tests || true
	black src tests || true

lint:
	ruff check src tests
