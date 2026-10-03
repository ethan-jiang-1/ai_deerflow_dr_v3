# Deep Research Harness — Makefile
# make verify is the application unit gate: stdlib unittest, zero external
# dependencies, offline-safe (UV_OFFLINE=1 is honored by construction). It never
# reads, imports, executes, or links OpenSpec content.

.PHONY: install verify test smoke

install:
	@echo "[install] nothing to install: the harness has no external dependencies; the"
	@echo "[install] deerflow-harness editable source lands with the wiring change."

test:
	PYTHONPATH=src python3 -m unittest discover -s tests

verify: test
	@echo "[verify] harness unittest gate passed."

# Integration lane (framework-dependent): requires the synced environment (`uv sync`).
smoke:
	UV_CACHE_DIR=$$(pwd)/../.uv-cache uv run --no-sync python -m unittest discover -s tests/integration -v
