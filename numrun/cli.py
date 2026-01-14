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
    "RED": "\033[1;31m", "YELLOW": "\033[1;33m", "MAGENTA": "\033[1;35m",
    "RESET": "\033[0m", "BOLD": "\033[1m", "GRAY": "\033[90m"
}

def get_advanced_help():
    rows = db.get_all()
    total_cmds = len(rows)
    total_uses = sum(r[3] for r in rows)
    
    # تصحيح حرف N في اللوجو
    logo = fr"""
{C['BLUE']}    _   __              {C['CYAN']}____            
{C['BLUE']}   / | / /_  ______ ___ {C['CYAN']}/ __ \__  ______ 
{C['BLUE']}  /  |/ / / / / __ `__ \{C['CYAN']}/ /_/ / / / / __ \\
{C['BLUE']} / /|  / /_/ / / / / / / {C['CYAN']}_  __/ /_/ / / / /
{C['BLUE']}/_/ |_/\__,_/_/ /_/ /_/{C['CYAN']}_/ |_|\__,_/_/ /_/ """
    
    dashboard = f"""
{C['CYAN']}┏━━━━ {C['BOLD']}DASHBOARD{C['RESET']}{C['CYAN']} ━━━━━━━━━━━━━━━━━━━━━━┓{C['RESET']}
{C['CYAN']}┃{C['RESET']}  {C['BLUE']}System{C['RESET']}: {platform.system():<10} {C['BLUE']}Saved{C['RESET']}: {total_cmds:<5} {C['CYAN']}┃{C['RESET']}
{C['CYAN']}┃{C['RESET']}  {C['BLUE']}Status{C['RESET']}: Stable      {C['BLUE']}Runs{C['RESET']}:  {total_uses:<5} {C['CYAN']}┃{C['RESET']}
{C['CYAN']}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{C['RESET']}

{C['BOLD']}{C['YELLOW']}CORE COMMANDS:{C['RESET']}
{C['GREEN']}nr <id|alias>{C['RESET']}   Run saved command
{C['GREEN']}nr save <cmd>{C['RESET']}    Add new (Auto-Shortcut)
{C['GREEN']}nr list{C['RESET']}          Advanced Table View
{C['GREEN']}nr nick <id> <n>{C['RESET']} Manually set Alias
{C['GREEN']}nr del <id>{C['RESET']}      Delete from database

{C['CYAN']}»{C['RESET']} {C['GRAY']}Use $1, $2 for dynamic command arguments.{C['RESET']}"""

    l_lines, d_lines = logo.strip("\n").split("\n"), dashboard.strip("\n").split("\n")
    output = "\n"
    for i in range(max(len(l_lines), len(d_lines))):
        left = l_lines[i] if i < len(l_lines) else " " * 28
        right = d_lines[i] if i < len(d_lines) else ""
        output += f"{left}  {right}\n"
    return output

def execute_cmd(identifier, extra_args):
    res = db.get_by_alias(identifier)
    cmd_id = None
    if res: cmd, cmd_id = res[0], res[1]
    elif identifier.isdigit():
        res = db.get_by_num(int(identifier))
        if res: cmd, cmd_id = res[0], int(identifier)
    
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
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help"]:
        print(get_advanced_help()); return

    first_arg = sys.argv[1]
    if execute_cmd(first_arg, sys.argv[2:]): return

    if first_arg == "save":
        if len(sys.argv) < 3: return
        full_command = " ".join(sys.argv[2:])
        base_word = sys.argv[2].lower()
        # اقتراح ذكي (أول حرف + آخر حرف)
        suggested = (base_word[0] + base_word[-1]) if len(base_word) > 1 else base_word
        reserved = ["save", "list", "del", "nick", "search"]
        
        use_alias = None
        if suggested not in reserved and not suggested.isdigit() and not db.is_alias_exists(suggested):
            choice = input(f"💡 Suggestion: Use '{C['YELLOW']}{suggested}{C['RESET']}' as shortcut? (y/n) or type custom: ")
            if choice.lower() == 'y': use_alias = suggested
            elif choice.lower() != 'n' and choice.strip(): use_alias = choice.strip()
        else:
            custom = input(f"📝 Enter custom shortcut (optional): ")
            if custom.strip(): use_alias = custom.strip()

        num = db.add_command(full_command, use_alias)
        msg = f" with shortcut '{C['YELLOW']}{use_alias}{C['RESET']}'" if use_alias else ""
        print(f"✅ {C['GREEN']}Saved as #{num}{msg}{C['RESET']}")

    elif first_arg == "list":
        rows = db.get_all()
        if not rows: print(f"{C['YELLOW']}📭 Empty list.{C['RESET']}"); return
        header = f"{C['BOLD']}{C['BLUE']}{'ID':<4} | {'ALIAS':<10} | {'COMMAND':<40} | {'USES':<6} | {'LAST USED'}{C['RESET']}"
        print(f"\n{C['CYAN']}📋 Command Inventory:{C['RESET']}\n{header}")
        for r in rows:
            u_color = C['GREEN'] if r[3] > 5 else C['RESET']
            print(f"{r[0]:<4} | {C['YELLOW']}{str(r[2] or '-'):<10}{C['RESET']} | {r[1][:37]:<40} | {u_color}{r[3]:<6}{C['RESET']} | {C['GRAY']}{str(r[4] or 'Never')}{C['RESET']}")

    elif first_arg == "nick":
        if len(sys.argv) < 4: return
        if db.set_alias(sys.argv[2], sys.argv[3]): print(f"✅ Assigned '{sys.argv[3]}'")
    
    elif first_arg == "del":
        if len(sys.argv) > 2: db.delete(int(sys.argv[2])); print("🗑️ Deleted.")

if __name__ == "__main__":
    main()
