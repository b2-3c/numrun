#!/usr/bin/env bash

echo "🚀 Starting NumRun Installation..."

PROJECT_DIR=$(pwd)
CLI_PATH="$PROJECT_DIR/numrun/cli.py"

if [[ ! -f "$CLI_PATH" ]]; then
    echo "❌ Error: Could not find cli.py at $CLI_PATH"
    echo "Please run this script from the root of the numrun folder."
    exit 1
fi

if [[ -n "$VIRTUAL_ENV" ]]; then
    pip install -e .
else
    pip install --user -e .
fi

RC_FILE="$HOME/.bashrc"
[[ $SHELL == *"zsh"* ]] && RC_FILE="$HOME/.zshrc"

if ! grep -q "alias nr=" "$RC_FILE"; then
    echo "" >> "$RC_FILE"
    echo "# NumRun Alias" >> "$RC_FILE"
    echo "alias nr='python3 $CLI_PATH'" >> "$RC_FILE"
    echo "✅ Added 'nr' alias pointing to $CLI_PATH"
else
    sed -i "/alias nr=/c\alias nr='python3 $CLI_PATH'" "$RC_FILE"
    echo "🔄 Updated existing 'nr' alias"
fi

echo "🎉 Installation complete!"
echo "⚠️  IMPORTANT: Run 'rm ~/.numrun.db' if you see database errors."
echo "⚠️  Run 'source $RC_FILE' to start using 'nr'"
