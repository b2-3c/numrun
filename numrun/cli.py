import sys
import argparse
import subprocess
import os
import platform

try:
    from numrun.database import Database
    from numrun.setup_completion import install as install_completion
except ImportError:
    from database import Database
    from setup_completion import install as install_completion

db = Database()

C = {
    "BLUE": "\033[1;34m", "CYAN": "\033[1;36m", "GREEN": "\033[1;32m",
    "RED": "\033[1;31m", "YELLOW": "\033[1;33m", "RESET": "\033[0m",
    "BOLD": "\033[1m", "GRAY": "\033[90m"
}

def get_fastfetch_help():
    logo = fr"""
{C['BLUE']}    _   __              {C['CYAN']}____            
{C['BLUE']}   / | / /_  ______ ___ {C['CYAN']}/ __ \__  ______ 
{C['BLUE']}  /  |/ / / / / __ `__ \{C['CYAN']}/ /_/ / / / / __ \\
{C['BLUE']} / /|  / /_/ / / / / / / {C['CYAN']}_  __/ /_/ / / / /
{C['BLUE']}/_/ |_/\__,_/_/ /_/ /_/{C['CYAN']}_/ |_|\__,_/_/ /_/ 
    """
    info = f"""
{C['BLUE']}{C['BOLD']}OS{C['RESET']}: {platform.system()}
{C['BLUE']}{C['BOLD']}Version{C['RESET']}: 0.3.0
{C['BLUE']}{C['BOLD']}Database{C['RESET']}: {len(db.get_all())} saved
{C['GRAY']}----------------------------------------{C['RESET']}
{C['CYAN']}{C['BOLD']}AVAILABLE COMMANDS:{C['RESET']}

  {C['GREEN']}nr{C['RESET']}               Open visual search (FZF)
  {C['GREEN']}nr <id>{C['RESET']}          Run command by its ID number
  {C['GREEN']}nr save <cmd>{C['RESET']}    Save a new command (Quotes optional)
  {C['GREEN']}nr list{C['RESET']}          Show all saved commands
  {C['GREEN']}nr search <q>{C['RESET']}    Search commands by text
  {C['GREEN']}nr del <id>{C['RESET']}      Delete a command

{C['CYAN']}{C['BOLD']}EXAMPLES:{C['RESET']}
  {C['GRAY']}# Save a command:{C['RESET']}
  nr save sudo nano /etc/nixos/configuration.nix
  
  {C['GRAY']}# Run command number 5:{C['RESET']}
  nr 5

  {C['GRAY']}# Run with dynamic arguments ($1, $2):{C['RESET']}
  nr 1 my_folder_name
    """
    l_lines, i_lines = logo.strip("\n").split("\n"), info.strip("\n").split("\n")
    return "\n" + "\n".join(f"{l_lines[i] if i<len(l_lines) else ' '*28}  {i_lines[i] if i<len(i_lines) else ''}" 
                            for i in range(max(len(l_lines), len(i_lines))))

def execute_cmd(num, extra_args):
    res = db.get_by_num(num)
    if not res:
        print(f"{C['RED']}❌ Error: #{num} not found.{C['RESET']}"); return
    cmd = res[0]
    for i, arg in enumerate(extra_args, 1):
        cmd = cmd.replace(f"${i}", arg)
    if any(danger in cmd.lower() for danger in ["rm ", "rmdir", "dd "]):
        confirm = input(f"{C['YELLOW']}⚠️  GUARD: {C['RESET']}{cmd}\nExecute? (y/N): ")
        if confirm.lower() != 'y': return
    print(f"{C['BLUE']}🚀 Running:{C['RESET']} {cmd}")
    db.increment_usage(num)
    subprocess.run(cmd, shell=True)

def main():
    # 1. المساعدة المخصصة
    if len(sys.argv) == 1:
        from cli import interactive_select # محاولة التشغيل التفاعلي
        interactive_select()
        return
        
    if sys.argv[1] in ["-h", "--help"]:
        print(get_fastfetch_help())
        return

    # 2. التشغيل بالرقم nr 1
    if sys.argv[1].isdigit():
        execute_cmd(int(sys.argv[1]), sys.argv[2:])
        return

    # 3. معالجة الأوامر الفرعية
    cmd_type = sys.argv[1]

    if cmd_type == "save":
        if len(sys.argv) < 3:
            print(f"{C['RED']}❌ Usage: nr save <your command>{C['RESET']}")
            return
        # جمع كل الكلمات بعد كلمة save في نص واحد
        full_command = " ".join(sys.argv[2:])
        num = db.add_command(full_command)
        print(f"✅ {C['GREEN']}Saved as #{num}{C['RESET']}")

    elif cmd_type == "list":
        rows = db.get_all()
        for r in rows:
            print(f"{C['CYAN']}{r[0]:<3}{C['RESET']} | {r[1]}")

    elif cmd_type == "search":
        if len(sys.argv) < 3:
            print(f"{C['RED']}❌ Usage: nr search <keyword>{C['RESET']}")
            return
        for r in db.search(sys.argv[2]):
            print(f"{C['GREEN']}{r[0]}{C['RESET']} → {r[1]}")

    elif cmd_type == "del":
        if len(sys.argv) < 3:
            print(f"{C['RED']}❌ Usage: nr del <id>{C['RESET']}")
            return
        db.delete(int(sys.argv[2]))
        print(f"🗑️ {C['YELLOW']}Deleted.{C['RESET']}")

    elif cmd_type == "setup-completion":
        install_completion()
        
    else:
        print(f"{C['RED']}❌ Unknown command: {cmd_type}{C['RESET']}")
        print("Type 'nr -h' for help.")

if __name__ == "__main__":
    main()
