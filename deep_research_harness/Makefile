# Deep Research Harness — Makefile
# make verify is the application unit gate: stdlib unittest, zero external
# dependencies, offline-safe (UV_OFFLINE=1 is honored by construction). It never
# reads, imports, executes, or links OpenSpec content.

.PHONY: install verify test smoke create watch status

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

# Human entry surface (six verbs over the substrate). See COMMANDS.md.
CONFIG ?= fixture

create:
	@test -n "$(PROBLEM)" || { echo "PROBLEM is required: make create PROBLEM=\"研究问题…\""; exit 1; }
	UV_CACHE_DIR=$$(pwd)/../.uv-cache uv run --no-sync python3 cli.py create "$(PROBLEM)" --config $(CONFIG)

watch:
	python3 cli.py watch $(BUNDLE)

status:
	python3 cli.py status $(BUNDLE)
