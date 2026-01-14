import sys
import subprocess
import os
import platform

try:
    from numrun.database import Database
except ImportError:
    from database import Database

db = Database()

C = {
    "BLUE": "\033[1;34m", "CYAN": "\033[1;36m", "GREEN": "\033[1;32m",
    "RED": "\033[1;31m", "YELLOW": "\033[1;33m", "RESET": "\033[0m",
    "BOLD": "\033[1m", "GRAY": "\033[90m"
}

def execute_cmd(identifier, extra_args):
    res = db.get_by_alias(identifier)
    cmd_id = None
    if res:
        cmd, cmd_id = res[0], res[1]
    elif identifier.isdigit():
        res = db.get_by_num(int(identifier))
        if res:
            cmd, cmd_id = res[0], int(identifier)
    
    if not cmd_id: return False

    for i, arg in enumerate(extra_args, 1):
        cmd = cmd.replace(f"${i}", arg)

    if any(danger in cmd.lower() for danger in ["rm ", "dd "]):
        confirm = input(f"{C['YELLOW']}⚠️  GUARD: {C['RESET']}{cmd}\nExecute? (y/N): ")
        if confirm.lower() != 'y': return True

    print(f"{C['BLUE']}🚀 Running:{C['RESET']} {cmd}")
    db.increment_usage(cmd_id)
    subprocess.run(cmd, shell=True)
    return True

def main():
    if len(sys.argv) < 2: return

    first_arg = sys.argv[1]
    
    # محاولة التشغيل أولاً
    if execute_cmd(first_arg, sys.argv[2:]):
        return

    if first_arg == "save":
        if len(sys.argv) < 3: return
        
        full_command = " ".join(sys.argv[2:])
        base_word = sys.argv[2].lower()
        
        # توليد الاقتراح (أول حرف + آخر حرف)
        suggested = (base_word[0] + base_word[-1]) if len(base_word) > 1 else base_word
        reserved = ["save", "list", "del", "nick", "search"]
        
        use_alias = None
        
        # فحص الاقتراح
        if suggested not in reserved and not suggested.isdigit() and not db.is_alias_exists(suggested):
            choice = input(f"💡 Suggestion: Use '{C['YELLOW']}{suggested}{C['RESET']}' as shortcut? (y/n) or enter custom: ")
            if choice.lower() == 'y':
                use_alias = suggested
            elif choice.lower() != 'n' and choice.strip() != "":
                use_alias = choice.strip()
        else:
            custom = input(f"📝 Enter a custom shortcut (or leave empty): ")
            if custom.strip(): use_alias = custom.strip()

        # الحفظ النهائي في قاعدة البيانات
        if use_alias and db.is_alias_exists(use_alias):
            print(f"{C['RED']}⚠️ Shortcut '{use_alias}' already exists.{C['RESET']}")
            use_alias = None

        num = db.add_command(full_command, use_alias)
        msg = f" with shortcut '{C['YELLOW']}{use_alias}{C['RESET']}'" if use_alias else ""
        print(f"✅ {C['GREEN']}Saved as #{num}{msg}{C['RESET']}")

    elif first_arg == "list":
        for r in db.get_all():
            alias = f"({C['YELLOW']}{r[2]}{C['RESET']})" if r[2] else ""
            print(f"{C['CYAN']}{r[0]:<3}{C['RESET']} | {r[1][:50]:<50} {alias}")

    elif first_arg == "del":
        if len(sys.argv) > 2:
            db.delete(int(sys.argv[2]))
            print("🗑️ Deleted.")

if __name__ == "__main__":
    main()
