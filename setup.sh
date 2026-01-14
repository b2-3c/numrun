#!/usr/bin/env bash

echo "🚀 Starting NumRun Installation..."

# التحقق إذا كنا داخل venv
if [[ -n "$VIRTUAL_ENV" ]]; then
    pip install -e .
else
    pip install --user -e .
fi

# تفعيل التكملة التلقائية
numrun setup-completion

# إضافة الاختصارات
RC_FILE="$HOME/.bashrc"
[[ $SHELL == *"zsh"* ]] && RC_FILE="$HOME/.zshrc"

if ! grep -q "alias nr=" "$RC_FILE"; then
    echo "alias nr='numrun'" >> "$RC_FILE"
    echo "✅ Added 'nr' alias"
fi

echo "🎉 Installation complete!"
echo "⚠️  IMPORTANT: Run 'rm ~/.numrun.db' if you see database errors."
echo "⚠️  Run 'source $RC_FILE' to start using 'nr'"
