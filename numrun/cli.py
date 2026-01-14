import sys
import argparse
import subprocess
import json
import os
import tempfile
import platform

# محاولة الاستيراد بأكثر من طريقة لضمان العمل في كل البيئات
try:
    from numrun.database import Database
    from numrun.setup_completion import install as install_completion
except ImportError:
    from database import Database
    from setup_completion import install as install_completion

db = Database()

# الألوان
C = {
    "BLUE": "\033[1;34m",
    "CYAN": "\033[1;36m",
    "GREEN": "\033[1;32m",
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
    "GRAY": "\033[90m"
}

def get_fastfetch_help():
    # لاحظ حرف r الصغير قبل علامة الاقتباس
    logo = fr"""
{C['BLUE']}    _   __              {C['CYAN']}____            
{C['BLUE']}   / | / /_  ______ ___ {C['CYAN']}/ __ \__  ______ 
{C['BLUE']}  /  |/ / / / / __ `__ \{C['CYAN']}/ /_/ / / / / __ \\
{C['BLUE']} / /|  / /_/ / / / / / / {C['CYAN']}_  __/ /_/ / / / /
{C['BLUE']}/_/ |_/\__,_/_/ /_/ /_/{C['CYAN']}_/ |_|\__,_/_/ /_/ 
    """
    
    saved_count = len(db.get_all())
    info = f"""
{C['BLUE']}{C['BOLD']}OS{C['RESET']}: {platform.system()} {platform.release()}
{C['BLUE']}{C['BOLD']}Version{C['RESET']}: 0.2.0
{C['BLUE']}{C['BOLD']}Commands{C['RESET']}: {saved_count} saved
{C['BLUE']}{C['BOLD']}Shell{C['RESET']}: {os.environ.get('SHELL', 'N/A').split('/')[-1]}
{C['GRAY']}----------------------------------------{C['RESET']}
{C['CYAN']}{C['BOLD']}COMMANDS{C['RESET']}:
{C['GREEN']}save{C['RESET']}   "cmd"   | {C['GREEN']}list{C['RESET']}    Show all
{C['GREEN']}edit{C['RESET']}   <id>    | {C['GREEN']}tag{C['RESET']}     <id> <t>
{C['GREEN']}search{C['RESET']} <q>      | {C['GREEN']}del{C['RESET']}     <id>
{C['GREEN']}setup-completion{C['RESET']} | {C['GREEN']}export{C['RESET']}
    """
    
    logo_lines = logo.strip("\n").split("\n")
    info_lines = info.strip("\n").split("\n")
    
    output = "\n"
    for i in range(max(len(logo_lines), len(info_lines))):
        l = logo_lines[i] if i < len(logo_lines) else " " * 28
        r = info_lines[i] if i < len(info_lines) else ""
        output += f"{l}  {r}\n"
    return output

def main():
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        execute_cmd(int(sys.argv[1]))
        return

    parser = argparse.ArgumentParser(prog="numrun", add_help=False)
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("save").add_argument("cmd")
    subparsers.add_parser("list")
    p_add = subparsers.add_parser("add"); p_add.add_argument("num", type=int); p_add.add_argument("cmd")
    p_edit = subparsers.add_parser("edit"); p_edit.add_argument("num", type=int)
    p_tag = subparsers.add_parser("tag"); p_tag.add_argument("num", type=int); p_tag.add_argument("tag_name")
    subparsers.add_parser("search").add_argument("query")
    p_del = subparsers.add_parser("del"); p_del.add_argument("num", type=int)
    subparsers.add_parser("setup-completion")
    subparsers.add_parser("export")

    if len(sys.argv) == 1 or sys.argv[1] in ["-h", "--help"]:
        print(get_fastfetch_help())
        return

    args = parser.parse_args()

    if args.command == "save":
        num = db.add_command(args.cmd)
        print(f"✅ Saved as #{num}")
    elif args.command == "list":
        rows = db.get_all()
        print(f"\n{C['BOLD']}{'ID':<3} | {'Command':<40} | {'Tags':<15}{C['RESET']}")
        print(f"{C['GRAY']}{'-' * 65}{C['RESET']}")
        for r in rows:
            print(f"{C['CYAN']}{r[0]:<3}{C['RESET']} | {r[1][:40]:<40} | {r[2] if r[2] else '':<15}")
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
        data = [{"id": r[0], "cmd": r[1], "tags": r[2]} for r in db.get_all()]
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

def execute_cmd(num):
    res = db.get_by_num(num)
    if res:
        print(f"{C['BLUE']}🚀 Running:{C['RESET']} {res[0]}")
        db.increment_usage(num)
        subprocess.run(res[0], shell=True)
    else:
        print(f"❌ #{num} not found.")

if __name__ == "__main__":
    main()
