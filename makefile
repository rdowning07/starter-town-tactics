# Makefile for starter-town-tactics

PYTHON := python3
TEST_DIR := tests
SRC_DIR := game

# Default target
.PHONY: help
help:
	@echo "Usage:"
	@echo "  make test         - Run all unit tests"
	@echo "  make coverage     - Run tests with coverage and show summary"
	@echo "  make htmlcov      - Generate HTML coverage report and open it"
	@echo "  make clean        - Remove __pycache__ and coverage files"
	@echo "  make lint         - Run flake8 linting"
	@echo "  make typecheck    - Run mypy static type checks"

.PHONY: test
test:
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
	mypy $(SRC_DIR)
