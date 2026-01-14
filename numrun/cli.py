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

    if any(danger in cmd.lower() for danger in ["rm ", "dd ", "mkfs"]):
        confirm = input(f"{C['YELLOW']}⚠️  GUARD: {C['RESET']}{cmd}\nExecute? (y/N): ")
        if confirm.lower() != 'y': return True

    print(f"{C['BLUE']}🚀 Running:{C['RESET']} {cmd}")
    db.increment_usage(cmd_id)
    subprocess.run(cmd, shell=True)
    return True

def main():
    if len(sys.argv) < 2:
        print(f"{C['CYAN']}NumRun v0.3.5 - Type 'nr -h' for help{C['RESET']}")
        return

    first_arg = sys.argv[1]
    
    if first_arg in ["-h", "--help"]:
        # (دالة المساعدة كما هي في الإصدارات السابقة مع تحديث طفيف)
        print(f"{C['BOLD']}Usage:{C['RESET']} nr <id|name> | nr save <cmd> | nr list | nr del <id>")
        return

    if execute_cmd(first_arg, sys.argv[2:]):
        return

    if first_arg == "save":
        if len(sys.argv) < 3: return
        full_command = " ".join(sys.argv[2:])
        base_word = sys.argv[2].lower()
        suggested = (base_word[0] + base_word[-1]) if len(base_word) > 1 else base_word
        reserved = ["save", "list", "del", "nick", "search"]
        
        use_alias = None
        if suggested not in reserved and not suggested.isdigit() and not db.is_alias_exists(suggested):
            choice = input(f"💡 Suggestion: Use '{C['YELLOW']}{suggested}{C['RESET']}' as shortcut? (y/n) or enter custom: ")
            if choice.lower() == 'y': use_alias = suggested
            elif choice.lower() != 'n' and choice.strip() != "": use_alias = choice.strip()
        else:
            custom = input(f"📝 Enter a custom shortcut (or leave empty): ")
            if custom.strip(): use_alias = custom.strip()

        num = db.add_command(full_command, use_alias)
        msg = f" with shortcut '{C['YELLOW']}{use_alias}{C['RESET']}'" if use_alias else ""
        print(f"✅ {C['GREEN']}Saved as #{num}{msg}{C['RESET']}")

    elif first_arg == "list":
        rows = db.get_all()
        if not rows:
            print(f"{C['YELLOW']}📭 Your list is empty.{C['RESET']}"); return

        # تنسيق الجدول المتقدم
        header = f"{C['BOLD']}{C['BLUE']}{'ID':<4} | {'ALIAS':<10} | {'COMMAND':<40} | {'USES':<6} | {'LAST USED'}{C['RESET']}"
        sep = f"{C['GRAY']}{'-'*4}-+-{'-'*10}-+-{'-'*40}-+-{'-'*6}-+-{'-'*16}{C['RESET']}"
        
        print(f"\n{C['CYAN']}📋 Command Inventory:{C['RESET']}")
        print(header); print(sep)

        for r in rows:
            cid, cmd, alias, uses, last = r[0], r[1], (r[2] or "-"), r[3], (r[4] or "Never")
            display_cmd = (cmd[:37] + "..") if len(cmd) > 37 else cmd
            u_color = C['GREEN'] if uses > 5 else C['RESET']
            
            print(f"{cid:<4} | {C['YELLOW']}{alias:<10}{C['RESET']} | {display_cmd:<40} | {u_color}{uses:<6}{C['RESET']} | {C['GRAY']}{last}{C['RESET']}")
        
        print(sep)
        print(f"{C['GRAY']}Total: {len(rows)} commands.{C['RESET']}\n")

    elif first_arg == "nick":
        if len(sys.argv) < 4: return
        if db.set_alias(sys.argv[2], sys.argv[3]):
            print(f"✅ #{sys.argv[2]} is now '{sys.argv[3]}'")
        else:
            print(f"{C['RED']}❌ Error: Name taken or ID invalid.{C['RESET']}")

    elif first_arg == "del":
        if len(sys.argv) > 2:
            db.delete(int(sys.argv[2]))
            print("🗑️ Deleted.")

if __name__ == "__main__":
    main()
