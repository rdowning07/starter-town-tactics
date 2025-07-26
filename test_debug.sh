#!/bin/bash

set -e

echo "🧪 Running full test suite with pytest..."

# Use pytest with verbose output
pytest -v --tb=short tests/ "$@"

echo "✅ All tests passed."
