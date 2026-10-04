# Deep Research Harness — Makefile
# make verify is the application unit gate: stdlib unittest, zero external
# dependencies, offline-safe (UV_OFFLINE=1 is honored by construction). It never
# reads, imports, executes, or links OpenSpec content.

.PHONY: install verify test smoke create watch status record-stream

install:
	@echo "[install] nothing to install: the harness has no external dependencies."
	@echo "[install] environment preparation is: uv sync (see COMMANDS.md)."

# tests/integration is deliberately a directory without __init__.py, so unittest
# discovery skips it here; the integration lane is `make smoke` (not an accident).
test:
	PYTHONPATH=src python3 -m unittest discover -s tests

verify: test
	@echo "[verify] harness unittest gate passed."

# Integration lane (framework-dependent): requires the synced environment (`uv sync`).
smoke:
	UV_CACHE_DIR=$$(pwd)/../.uv-cache uv sync && UV_CACHE_DIR=$$(pwd)/../.uv-cache uv run --no-sync python -m unittest discover -s tests/integration -v

# Integration fixture recording (real API, explicit opt-in).
record-stream:
	UV_CACHE_DIR=$$(pwd)/../.uv-cache uv run --no-sync python -m tests.integration.record_stream "$(PROBLEM)" $(CONFIG)

# Human entry surface (six verbs over the substrate). See COMMANDS.md.
CONFIG ?= fixture

create:
	@test -n "$(PROBLEM)" || { echo "PROBLEM is required: make create PROBLEM=\"研究问题…\""; exit 1; }
	UV_CACHE_DIR=$$(pwd)/../.uv-cache uv run --no-sync python3 cli.py create "$(PROBLEM)" --config $(CONFIG)

watch:
	python3 cli.py watch $(BUNDLE)

status:
	python3 cli.py status $(BUNDLE)
