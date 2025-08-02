# Makefile for starter-town-tactics

PYTHON := python3
VENV ?= venv
MAKEFLAGS += --no-print-directory
TEST_DIR := tests
SRC_DIR := game

# Default target
.PHONY: help
help:
	@echo "Usage:"
	@echo "  make install      - Install dependencies"
	@echo "  make install-dev  - Install dev dependencies and pre-commit hooks"
	@echo "  make test         - Run all unit tests"
	@echo "  make coverage     - Run tests with coverage and show summary"
	@echo "  make htmlcov      - Generate HTML coverage report and open it"
	@echo "  make clean        - Remove __pycache__ and coverage files"
	@echo "  make lint         - Run flake8 linting"
	@echo "  make typecheck    - Run mypy static type checks"
	@echo "  make format       - Format code with black and isort"
	@echo "  make validate-assets - Validate asset structure and tilesets"
	@echo "  make viewer       - Launch asset viewer"
	@echo "  make check-all    - Run lint, typecheck, and test"
	@echo "  make play-overlay-demo - Run CLI overlay visualizer"
	@echo "  make play-sim-demo - Run SimRunner demo (interactive)"
	@echo "  make play-sim-demo-auto - Run SimRunner demo (auto-run)"
	@echo "  make play-scenario-demo - Run scenario-based demo (interactive)"
	@echo "  make play-scenario-demo-auto - Run scenario-based demo (auto-run)"
	@echo "  make test-keyboard-controller - Run keyboard controller tests only"
	@echo "  make test-action-point-manager - Run action point manager tests only"

.PHONY: install
install:
	pip install -r requirements.txt

.PHONY: install-dev
install-dev:
	pip install -r requirements.txt
	pre-commit install

.PHONY: test
test: validate-assets
	PYTHONPATH=. pytest -m "not integration" --cov=$(SRC_DIR) --cov-report=term-missing

.PHONY: coverage
coverage:
	PYTHONPATH=. pytest -m "not integration" --cov=$(SRC_DIR) --cov-report=term-missing

.PHONY: htmlcov
htmlcov:
	PYTHONPATH=. pytest -m "not integration" --cov=$(SRC_DIR) --cov-report=html
	open htmlcov/index.html

.PHONY: clean
clean:
	find . -type d -name '__pycache__' -exec rm -r {} +
	rm -rf .pytest_cache .mypy_cache .hypothesis htmlcov .coverage

.PHONY: lint
lint:
	flake8 $(SRC_DIR) $(TEST_DIR)

.PHONY: typecheck
typecheck:
	mypy $(SRC_DIR) $(TEST_DIR)

.PHONY: format
format:
	black $(SRC_DIR) $(TEST_DIR)
	isort $(SRC_DIR) $(TEST_DIR)

.PHONY: validate-assets
validate-assets:
	PYTHONPATH=. $(PYTHON) scripts/validate_assets.py
	PYTHONPATH=. $(PYTHON) scripts/validateassets.py

.PHONY: check-all
check-all: lint typecheck validate-assets test

.PHONY: play-overlay-demo
play-overlay-demo:
	PYTHONPATH=. $(PYTHON) devtools/cli_overlay_demo.py

.PHONY: test-keyboard-controller
test-keyboard-controller:
	PYTHONPATH=. pytest tests/test_keyboard_controller.py

.PHONY: test-action-point-manager
test-action-point-manager:
	PYTHONPATH=. pytest tests/test_action_point_manager.py

.PHONY: play-sim-demo
play-sim-demo:
	PYTHONPATH=. $(PYTHON) devtools/sim_runner_demo.py

.PHONY: play-sim-demo-auto
play-sim-demo-auto:
	PYTHONPATH=. $(PYTHON) devtools/sim_runner_demo.py --auto

.PHONY: play-scenario-demo
play-scenario-demo:
	PYTHONPATH=. $(PYTHON) devtools/sim_runner_demo.py --scenario

.PHONY: play-scenario-demo-auto
play-scenario-demo-auto:
	PYTHONPATH=. $(PYTHON) devtools/sim_runner_demo.py --scenario --auto

.PHONY: viewer
viewer:
	PYTHONPATH=. $(PYTHON) scripts/asset_viewer.py
