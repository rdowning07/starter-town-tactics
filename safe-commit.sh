#!/bin/bash

# Usage: ./bin/safe-commit.sh "Your commit message here"

if [ -z "$1" ]; then
  echo "❌ Please provide a commit message."
  echo "Usage: ./bin/safe-commit.sh \"your message\""
  exit 1
fi

echo "🧹 Running pre-commit checks..."
pre-commit run --all-files

echo "📦 Staging all changes..."
git add .

echo "✅ Committing: $1"
git commit -m "$1"

echo "🚀 Pushing to origin/main..."
git push origin main

# Try to open the GitHub repo page
remote_url=$(git config --get remote.origin.url)
web_url=${remote_url%.git}
web_url=${web_url/git@github.com:/https:\/\/github.com\/}

echo "🌐 Opening GitHub repository in your browser: $web_url"
open "$web_url"

echo "🎉 Done!"
