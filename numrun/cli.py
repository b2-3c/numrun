import sys
import argparse
import subprocess
import json
import os
import tempfile
import platform
import re

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
{C['BLUE']}{C['BOLD']}OS{C['RESET']}: {platform.system()} {platform.release()}
{C['BLUE']}{C['BOLD']}Version{C['RESET']}: 0.3.0 (Pro)
{C['BLUE']}{C['BOLD']}Database{C['RESET']}: {len(db.get_all())} snippets
{C['BLUE']}{C['BOLD']}Features{C['RESET']}: Dynamic Args, Auto-Guard
{C['GRAY']}----------------------------------------{C['RESET']}
{C['CYAN']}{C['BOLD']}QUICK COMMANDS{C['RESET']}:
{C['GREEN']}save{C['RESET']} "cmd" | {C['GREEN']}list{C['RESET']} | {C['GREEN']}edit{C['RESET']} <id>
{C['GREEN']}tag{C['RESET']} <id> <t> | {C['GREEN']}search{C['RESET']} <q> | {C['GREEN']}del{C['RESET']} <id>
{C['YELLOW']}Tip: Use $1, $2 in commands for arguments!{C['RESET']}
    """
    l_lines, i_lines = logo.strip("\n").split("\n"), info.strip("\n").split("\n")
    return "\n" + "\n".join(f"{l_lines[i] if i<len(l_lines) else ' '*28}  {i_lines[i] if i<len(i_lines) else ''}" 
                            for i in range(max(len(l_lines), len(i_lines))))

def execute_cmd(num, extra_args):
    res = db.get_by_num(num)
    if not res:
        print(f"{C['RED']}❌ Error: #{num} not found.{C['RESET']}")
        return
    
    cmd = res[0]
    
    # 1. دعم المتغيرات الديناميكية (Dynamic Args)
    # استبدال $1 بـ أول معامل إضافي، $2 بالثاني... وهكذا
    for i, arg in enumerate(extra_args, 1):
        cmd = cmd.replace(f"${i}", arg)
    
    # 2. الحماية الذكية (Auto-Guard)
    if any(danger in cmd.lower() for danger in ["rm ", "rmdir", "mkfs", "dd ", "> /dev/sd"]):
        confirm = input(f"{C['YELLOW']}⚠️  DANGER DETECTED: {C['RESET']}{cmd}\nConfirm execution? (y/N): ")
        if confirm.lower() != 'y':
            print(f"{C['RED']}Aborted.{C['RESET']}")
            return

    print(f"{C['BLUE']}🚀 Running:{C['RESET']} {cmd}")
    db.increment_usage(num)
    try:
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        print(f"\n{C['YELLOW']}Stopped by user.{C['RESET']}")

def main():
    # معالجة التشغيل المباشر: numrun 1 [arg1] [arg2]
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        execute_cmd(int(sys.argv[1]), sys.argv[2:])
        return

    parser = argparse.ArgumentParser(prog="numrun", add_help=False)
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("save").add_argument("cmd")
    subparsers.add_parser("list")
    subparsers.add_parser("search").add_argument("query")
    subparsers.add_parser("setup-completion")
    subparsers.add_parser("export")
    
    p_edit = subparsers.add_parser("edit"); p_edit.add_argument("num", type=int)
    p_tag = subparsers.add_parser("tag"); p_tag.add_argument("num", type=int); p_tag.add_argument("tag_name")
    p_del = subparsers.add_parser("del"); p_del.add_argument("num", type=int)

    if len(sys.argv) == 1 or sys.argv[1] in ["-h", "--help"]:
        print(get_fastfetch_help())
        return

    args = parser.parse_args()

    if args.command == "save":
        num = db.add_command(args.cmd)
        print(f"{C['GREEN']}✅ Saved as #{num}{C['RESET']}")
    elif args.command == "list":
        rows = db.get_all()
        print(f"\n{C['BOLD']}{'ID':<3} | {'Command':<35} | {'Tags':<12} | {'Used'}{C['RESET']}")
        print(f"{C['GRAY']}{'-' * 70}{C['RESET']}")
        for r in rows:
            # r: (id, command, tags, usage, last_used)
            use_color = C['GREEN'] if r[3] > 5 else C['CYAN']
            print(f"{use_color}{r[0]:<3}{C['RESET']} | {r[1][:35]:<35} | {r[2] if r[2] else '':<12} | {r[3]}")
    elif args.command == "edit":
        edit_command(args.num)
    elif args.command == "tag":
        db.add_tag(args.num, args.tag_name)
        print(f"🏷️ Tagged #{args.num}")
    elif args.command == "search":
        for r in db.search(args.query):
            print(f"{C['GREEN']}{r[0]}{C['RESET']} → {r[1]}")
    elif args.command == "del":
        db.delete(args.num)
        print(f"🗑️ Deleted #{args.num}")
    elif args.command == "setup-completion":
        install_completion()
    elif args.command == "export":
        data = [{"id": r[0], "cmd": r[1], "tags": r[2], "usage": r[3], "last": r[4]} for r in db.get_all()]
        print(json.dumps(data, indent=2))

def edit_command(num):
    res = db.get_by_num(num)
    if not res: return
    editor = os.environ.get('EDITOR', 'nano')
    with tempfile.NamedTemporaryFile(suffix=".sh", mode='w+', delete=False) as tf:
        tf.write(res[0]); path = tf.name
    subprocess.run([editor, path])
    with open(path, 'r') as f:
        new_cmd = f.read().strip()
    if new_cmd:
        db.update_command(num, new_cmd); print("📝 Updated!")
    os.unlink(path)

if __name__ == "__main__":
    main()
