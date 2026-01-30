#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# NumRun Installation Script (v2.0.4) - Nested Path Fix
# -----------------------------------------------------------------------------

# الألوان
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🚀 Starting NumRun Installation (v2.0.4)...${NC}"

# 1. تحديد المسار المطلق للمجلد الذي يحتوي على السكريبت
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# البحث عن cli.py في المجلد الحالي أو المجلدات الفرعية
if [[ -f "$SCRIPT_DIR/cli.py" ]]; then
    FULL_CLI_PATH=$(realpath "$SCRIPT_DIR/cli.py")
elif [[ -f "$SCRIPT_DIR/numrun/cli.py" ]]; then
    FULL_CLI_PATH=$(realpath "$SCRIPT_DIR/numrun/cli.py")
elif [[ -f "$SCRIPT_DIR/numrun/numrun/cli.py" ]]; then
    FULL_CLI_PATH=$(realpath "$SCRIPT_DIR/numrun/numrun/cli.py")
else
    echo -e "${RED}❌ Error: Could not find cli.py in $SCRIPT_DIR or its subdirectories.${NC}"
    echo -e "${YELLOW}Please make sure you are running setup.sh from the root of your project.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Found cli.py at: $FULL_CLI_PATH${NC}"

# 2. تثبيت الاعتماديات (rich)
echo -e "${YELLOW}⚙️ Checking Python dependencies...${NC}"
install_rich() {
    if [[ -n "$VIRTUAL_ENV" ]]; then
        pip3 install rich --quiet
    else
        pip3 install --user rich --quiet || pip3 install --user rich --break-system-packages --quiet
    fi
}

if command -v pip3 &> /dev/null; then
    install_rich
    echo -e "${GREEN}✅ 'rich' dependency is ready.${NC}"
else
    echo -e "${RED}❌ Error: pip3 is not installed.${NC}"
    exit 1
fi

# 3. إعداد الاسم المستعار (Alias) لجميع الطرفيات
echo -e "${YELLOW}🔗 Setting up 'nr' alias...${NC}"

ALIAS_LINE="alias nr='python3 $FULL_CLI_PATH'"
RC_FILES=("$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.bash_profile")

for RC in "${RC_FILES[@]}"; do
    if [ -f "$RC" ]; then
        # تنظيف أي اختصارات قديمة لـ nr
        sed -i '/alias nr=/d' "$RC"
        # إضافة الاختصار الجديد بمسار مطلق
        echo "" >> "$RC"
        echo "# NumRun Alias" >> "$RC"
        echo "$ALIAS_LINE" >> "$RC"
        echo -e "${GREEN}✅ Updated 'nr' in $RC${NC}"
    fi
done

# 4. رسالة الإكمال
echo -e "\n${GREEN}🎉 Installation complete! NumRun v2.0.4 is ready.${NC}"
echo -e "${CYAN}To activate now, run:${NC}"
if [[ $SHELL == *"zsh"* ]]; then
    echo -e "${YELLOW}source ~/.zshrc${NC}"
else
    echo -e "${YELLOW}source ~/.bashrc${NC}"
fi
echo -e "${CYAN}Then try: ${YELLOW}nr -i${NC}"
