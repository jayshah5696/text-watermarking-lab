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

# Run the full local test suite. Stage 3 tests use only small MLX arrays.
test:
    uv run pytest

# Run tests with terminal and XML coverage.
test-cov:
    uv run pytest --cov=watermark_lab --cov-report=term-missing --cov-report=xml

# Run format-check, lint, typecheck, and test.
check: format-check lint typecheck test

# Generate the Stage 1 ignored raw run and selected artifacts.
lab-01:
    uv run python labs/01_biased_coin.py

# Validate the selected artifact schema and recompute its summary.
verify-lab-01:
    uv run python scripts/verify_lab_01.py

# Generate the deterministic Stage 2 toy-vocabulary trace.
lab-02:
    uv run python labs/02_toy_greenlist.py

# Recompute and validate the selected Stage 2 trace.
verify-lab-02:
    uv run python scripts/verify_lab_02.py

# Generate paired Stage 3 traces with the pinned MLX model fixture.
lab-03:
    uv run python labs/03_manual_generation.py

# Recompute and validate Stage 3 evidence from the local model cache.
verify-lab-03:
    uv run python scripts/verify_lab_03.py

# Generate paired Stage 4 traces with the pinned Transformers reference adapter.
lab-04:
    uv run python labs/04_transformers_reference.py

# Recompute and validate Stage 4 evidence from the local model cache.
verify-lab-04:
    uv run python scripts/verify_lab_04.py
