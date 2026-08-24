# Determine container runtime, preferring Docker on macOS
OS = $(shell uname)
CONTAINER_RUNTIMES = podman docker
ifeq ($(OS), Darwin)
	CONTAINER_RUNTIMES = docker podman
endif

CONTAINER_RUNTIME ?= $(shell type -P $(CONTAINER_RUNTIMES) | head -n 1)

.PHONY: ci fix format lint lock radon setup test typecheck test

fix:
	uv run --locked ruff check --fix
	uv run --locked ruff format

lint:
	uv run --locked ruff check src/

format:
	uv run --locked ruff format src/ tests/

format-check:
	uv run --locked ruff format --check src/ tests/

typecheck:
	uv run --locked ty check src/

test:
	uv run --locked pytest tests/

radon:
	@uv run --locked radon cc src/ -s --min C | grep -q . \
		&& { echo "FAIL: Cyclomatic complexity C or higher detected"; exit 1; } \
		|| echo "PASS: All functions rated A or B"

ci: lint format typecheck radon test
	@echo ""
	@echo "✅ All CI checks passed!"

setup:
	uv sync --locked --group dev

upgrade:
	uv lock --upgrade
