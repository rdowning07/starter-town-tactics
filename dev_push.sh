#!/bin/bash

set -e

# Dev Push Script: Add, commit, and force push with a default message

echo "📦 Staging changes..."
git add .

MESSAGE=${1:-"Dev push: tested + forced"}
echo "✍️  Commit message: $MESSAGE"
git commit -m "$MESSAGE"

echo "🚀 Pushing to main with --force..."
git push origin main --force

echo "✅ Done."
