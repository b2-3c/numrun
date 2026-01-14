import sys
import argparse
import subprocess
import json
import os
import tempfile
from .database import Database
from .setup_completion import install as install_completion

db = Database()

def main():
    parser = argparse.ArgumentParser(prog="numrun", description="Advanced Command Manager")
    subparsers = parser.add_subparsers(dest="command")

    # تعريف الأوامر
    subparsers.add_parser("save").add_argument("cmd")
    add_p = subparsers.add_parser("add")
    add_p.add_argument("num", type=int)
    add_p.add_argument("cmd")
    subparsers.add_parser("list")
    
    edit_p = subparsers.add_parser("edit")
    edit_p.add_argument("num", type=int)
    
    tag_p = subparsers.add_parser("tag")
    tag_p.add_argument("num", type=int)
    tag_p.add_argument("tag_name")

    search_p = subparsers.add_parser("search")
    search_p.add_argument("query")
    
    subparsers.add_parser("export")
    subparsers.add_parser("setup-completion")
    
    del_p = subparsers.add_parser("del")
    del_p.add_argument("num", type=int)

    # التنفيذ المباشر إذا كان المدخل رقم
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        execute_cmd(int(sys.argv[1]))
        return

    args = parser.parse_args()

    if args.command == "save":
        num = db.add_command(args.cmd)
        print(f"✅ Saved as #{num}")
    elif args.command == "list":
        rows = db.get_all()
        print(f"\033[1m{'ID':<3} | {'Command':<40} | {'Tags':<15} | {'Used'}\033[0m")
        print("-" * 75)
        for r in rows:
            print(f"{r[0]:<3} | {r[1][:40]:<40} | {r[2] if r[2] else '':<15} | {r[3]}")
    elif args.command == "edit":
        edit_command(args.num)
    elif args.command == "tag":
        db.add_tag(args.num, args.tag_name)
        print(f"🏷️ Tag '{args.tag_name}' added to #{args.num}")
    elif args.command == "search":
        for r in db.search(args.query):
            print(f"\033[1;32m{r[0]}\033[0m → {r[1]}")
    elif args.command == "del":
        db.delete(args.num)
        print(f"🗑️ Deleted #{args.num}")
    elif args.command == "setup-completion":
        install_completion()
    elif args.command == "export":
        data = [{"num": r[0], "cmd": r[1], "tags": r[2], "usage": r[3]} for r in db.get_all()]
        print(json.dumps(data, indent=2))
    else:
        parser.print_help()

def edit_command(num):
    res = db.get_by_num(num)
    if not res: return
    editor = os.environ.get('EDITOR', 'nano')
    with tempfile.NamedTemporaryFile(suffix=".sh", mode='w+', delete=False) as tf:
        tf.write(res[0])
        path = tf.name
    subprocess.run([editor, path])
    with open(path, 'r') as f:
        new_cmd = f.read().strip()
    if new_cmd:
        db.update_command(num, new_cmd)
        print("📝 Updated!")
    os.unlink(path)

def execute_cmd(num):
    res = db.get_by_num(num)
    if res:
        print(f"\033[1;34mRunning:\033[0m {res[0]}")
        db.increment_usage(num)
        subprocess.run(res[0], shell=True)
    else:
        print("❌ Not found")

if __name__ == "__main__":
    main()
