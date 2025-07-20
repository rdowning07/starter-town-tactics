# Starter Town Tactics

A tactical RPG prototype in Python inspired by Final Fantasy Tactics. This project is designed for hands-on learning with game systems, AI behavior, and developer tools like pre-commit, linting, and test automation.

---

## 🚀 Features

- Grid-based tactical movement
- Modular game architecture
- Pre-configured dev tools: `black`, `isort`, `mypy`, `pylint`, `pytest`, `pre-commit`
- Structured unit tests and CI-ready

---

## 🛠️ Installation

```bash
git clone https://github.com/rdowning07/starter-town-tactics.git
cd starter-town-tactics
python3 -m venv .venv
source .venv/bin/activate   # or `.venv\Scripts\activate` on Windows
pip install -r requirements.txt
pre-commit install
```

---

## 🧪 Running Tests

```bash
pytest
```

---

## 🧹 Linting and Type Checks

```bash
black .
isort .
pylint game tests
mypy game
```

To run all checks:

```bash
pre-commit run --all-files
```

---

## 📂 Project Structure

```
starter-town-tactics/
├── .vscode/                  # Editor settings (optional)
├── game/                     # Core game logic
│   ├── __init__.py
│   ├── grid.py
│   └── main.py
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── test_example.py
│   ├── test_grid.py
│   └── tests_fail.py
├── .pylintrc                 # Linting config
├── .pre-commit-config.yaml   # Pre-commit hooks
├── pytest.ini                # Pytest config
├── requirements.txt          # Dependencies
├── hello.py                  # Temporary dev/test file
└── README.md
```

---

## 📈 Continuous Integration (optional)

Add the following GitHub Actions file to `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]

jobs:
  lint-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pre-commit
      - name: Run pre-commit
        run: pre-commit run --all-files
      - name: Run tests
        run: pytest
```

---

## 🧭 Roadmap

-

---

## 📜 License

MIT

---

## 👤 Author

Rob Downing [https://github.com/rdowning07](https://github.com/rdowning07)

