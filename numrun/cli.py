import sys, subprocess, os, tempfile, json

# إعداد المسارات
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from database import Database
except ImportError:
    from numrun.database import Database

db = Database()

C = {
    "B": "\033[1;34m", "C": "\033[1;36m", "G": "\033[1;32m", "R": "\033[1;31m",
    "Y": "\033[1;33m", "M": "\033[1;35m", "W": "\033[1;37m", "GR": "\033[90m",
    "RST": "\033[0m", "BOLD": "\033[1m"
}

def get_pro_help():
    logo = fr"""{C['C']}    _   __              {C['B']}  ____ 
{C['C']}   / | / /_  ______ ___ {C['B']} / __  \__  ______ 
{C['C']}  /  |/ / / / / __ `__ \{C['B']}/ /_/  / / /  / __ \\
{C['C']} / /|  / /_/ / / / / / / {C['B']}_  __/ /_/  / / / /
{C['C']}/_/ |_/\__,_/_/ /_/ /_/{C['B']}_/ |_|\__,_/_/ /_/ {C['Y']}v0.1.0{C['RST']}"""
    print(logo)
    w = 58
    print(f"\n {C['W']}╭─ {C['G']}COMMANDS{C['W']} {'─'*(w-10)}╮")
    print(f" │ {C['G']}nr <ID/Alias>{C['W']:<5} {C['GR']}•{C['W']} Run command by ID or Alias             │")
    print(f" │ {C['G']}nr save <cmd>{C['W']:<5} {C['GR']}•{C['W']} Save (use -a for alias, -g for group)   │")
    print(f" │ {C['G']}nr list{C['W']:<10} {C['GR']}•{C['W']} Show all saved commands                      │")
    print(f" ╰{'─'*w}╯")
    print(f"\n {C['W']}╭─ {C['M']}QUICK NOTES{C['W']} {'─'*(w-13)}╮")
    print(f" │ {C['M']}nr note add{C['W']:<8} {C['GR']}•{C['W']} Create a new note                          │")
    print(f" │ {C['M']}nr note ls{C['W']:<9} {C['GR']}•{C['W']} List all notes                              │")
    print(f" │ {C['M']}nr note view <ID>{C['W']:<3} {C['GR']}•{C['W']} Display note content                 │")
    print(f" ╰{'─'*w}╯{C['RST']}")

def show_list():
    rows = db.get_all_commands()
    if not rows:
        print(f"\n {C['R']}⚠ No commands found.{C['RST']}\n")
        return
    sep = f" {C['C']}├{'─'*5}┼{'─'*12}┼{'─'*24}┼{'─'*12}┤"
    print(f"\n {C['C']}╭{'─'*5}┬{'─'*12}┬{'─'*24}┬{'─'*12}╮")
    print(f" │ {C['W']}ID  {C['C']}│ {C['W']}ALIAS      {C['C']}│ {C['W']}COMMAND                 {C['C']}│ {C['W']}GROUP      {C['C']}│")
    print(sep)
    for r in rows:
        alias = (r['alias'] or "---")[:10]
        cmd_disp = (r['command'][:21] + "..") if len(r['command']) > 21 else r['command']
        print(f" │ {C['Y']}{str(r['cmd_number']):<3} {C['C']}│ {C['G']}{alias:<10} {C['C']}│ {C['W']}{cmd_disp:<22} {C['C']}│ {C['M']}{r['group_name']:<10} {C['C']}│")
    print(f" {C['C']}╰{'─'*5}┴{'─'*12}┴{'─'*24}┴{'─'*12}╯{C['RST']}")

def run_by_id(identifier):
    all_cmds = db.get_all_commands()
    for r in all_cmds:
        if str(r['cmd_number']) == identifier or (r['alias'] and r['alias'] == identifier):
            print(f"{C['B']}🚀 Running:{C['RST']} {r['command']}")
            subprocess.run(r['command'], shell=True)
            db.increment_usage(r['cmd_number'])
            return True
    return False

def main():
    if len(sys.argv) < 2:
        get_pro_help()
        return

    cmd = sys.argv[1]
    
    if cmd in ["-h", "--help"]:
        get_pro_help()
    elif cmd == "list":
        show_list()
    elif cmd == "save":
        args = sys.argv[2:]
        if not args: return
        group, alias = 'general', None
        if "-g" in args:
            idx = args.index("-g"); group = args[idx+1]; args = args[:idx] + args[idx+2:]
        if "-a" in args:
            idx = args.index("-a"); alias = args[idx+1]; args = args[:idx] + args[idx+2:]
        
        command = " ".join(args)
        if command:
            db.add_command(command, alias=alias, group=group)
            print(f" {C['G']}✅ Saved.{C['RST']}")
    elif cmd == "del" and len(sys.argv) > 2:
        db.delete_cmd(sys.argv[2]); print("🗑️ Deleted.")
    elif cmd == "note":
        args = sys.argv[2:]
        if not args or args[0] == "ls":
            for n in db.get_all_notes(): print(f" {n['note_id']} 📄 {C['W']}{n['title']}{C['RST']}")
        elif args[0] == "add":
            title = " ".join(args[1:]) or "Untitled"
            with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tf:
                subprocess.call([os.environ.get('EDITOR', 'nano'), tf.name])
                with open(tf.name, 'r') as f: content = f.read()
            if content.strip(): db.add_note(title, content); print("✅ Note Saved.")
            os.remove(tf.name)
        elif args[0] == "view" and len(args) > 1:
            # دالة عرض الملاحظة مدمجة هنا للتبسيط
            res = db.get_note(args[1])
            if res: print(f"\n{C['BOLD']}{res['title']}{C['RST']}\n{res['content']}")
    else:
        # إذا لم يكن أمراً محجوزاً، جرب تشغيله كـ ID
        if not run_by_id(cmd):
            print(f"{C['R']}❌ Unknown command or ID: {cmd}{C['RST']}")

if __name__ == "__main__":
    main()
