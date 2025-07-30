#!/bin/bash
# Enhanced bootstrap: restores session context + validates architecture contracts

echo "🔁 [BOOTSTRAP] Loading Starter Town Tactics session context..."

# Step 1: View key documents
echo "📄 Loading resumegpt.md"
cat resumegpt.md
echo -e "\n📄 Loading plan.md"
cat plan.md

# Step 2: Load context contracts
echo -e "\n🔒 Loading context_registry.py"
cat context_registry.py

# Step 3: Cursor pre-index (if using Cursor)
if [ -f ".cursor/config.json" ]; then
  echo -e "\n🧠 [Cursor] Project configuration found. Indexing key files..."
  jq '.indexedFiles' .cursor/config.json
else
  echo -e "\n⚠️ [Cursor] No config.json found. Skipping Cursor indexing."
fi

# Step 4: Git project status summary
echo -e "\n🧾 Git status:"
git status -sb

echo -e "\n✅ Bootstrap complete. You may now resume dev or load context into ChatGPT/Cursor."
