set dotenv-load := false

# List commands.
default:
    @just --list

# Run uv sync --locked --all-groups.
setup:
    uv sync --locked --all-groups

# Apply Ruff formatting and safe Ruff fixes.
format:
    uv run ruff format .
    uv run ruff check --fix .

# Check formatting without writes.
format-check:
    uv run ruff format --check .

# Run Ruff lint checks.
lint:
    uv run ruff check .

# Run Pyright.
typecheck:
    uv run pyright

# Run the full CPU-only test suite.
test:
    uv run pytest

# Run tests with terminal and XML coverage.
test-cov:
    uv run pytest --cov=watermark_lab.stats --cov=watermark_lab.records --cov-report=term-missing --cov-report=xml

# Run format-check, lint, typecheck, and test.
check: format-check lint typecheck test

# Generate the Stage 1 ignored raw run and selected artifacts.
lab-01:
    uv run python labs/01_biased_coin.py

# Validate the selected artifact schema and recompute its summary.
verify-lab-01:
    uv run python scripts/verify_lab_01.py
