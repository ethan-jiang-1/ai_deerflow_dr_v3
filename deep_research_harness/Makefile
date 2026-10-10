# Deep Research Harness — Makefile
# make verify = the application unit gate; semantic owner: COMMANDS.md.

.PHONY: install verify test lint smoke create watch status record-stream

install:
	@echo "[install] no-op: use uv sync for runtime and integration dependencies."
	@echo "[install] environment preparation is: uv sync (see COMMANDS.md)."

# tests/integration is deliberately a directory without __init__.py, so unittest
# discovery skips it here; the integration lane is `make smoke` (not an accident).
test:
	PYTHONPATH=src python3 -m unittest discover -s tests

verify: test
	@echo "[verify] harness unittest gate passed."

# Lint convenience lane (ruff; CI does not enforce it — see pyproject dev group).
# Requires the synced environment (`uv sync`), same as the smoke lane.
lint:
	UV_CACHE_DIR=$$(pwd)/../.uv-cache uv run --no-sync ruff check src tests tools cli.py

# Integration lane (framework-dependent): requires the synced environment (`uv sync`).
smoke:
	UV_CACHE_DIR=$$(pwd)/../.uv-cache uv sync && UV_CACHE_DIR=$$(pwd)/../.uv-cache uv run --no-sync python -m unittest discover -s tests/integration -v

# Stream recording; CONFIG defaults to fixture, real API requires CONFIG=base.
record-stream:
	UV_CACHE_DIR=$$(pwd)/../.uv-cache uv run --no-sync python tools/record_stream.py "$(PROBLEM)" $(CONFIG)

# Human entry surface (seven verbs over the substrate). See COMMANDS.md.
CONFIG ?= fixture

create:
	@test -n "$(PROBLEM)" || { echo "PROBLEM is required: make create PROBLEM=\"研究问题…\""; exit 1; }
	UV_CACHE_DIR=$$(pwd)/../.uv-cache uv run --no-sync python3 cli.py create "$(PROBLEM)" --config $(CONFIG)

watch:
	python3 cli.py watch $(BUNDLE)

status:
	python3 cli.py status $(BUNDLE)
