import sys, subprocess, os, tempfile, json

# دعم NixOS: ضمان الوصول للملفات المحلية
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
    print(f"\n {C['W']}╭─ {C['G']}COMMANDS & GROUPS{C['W']} {'─'*(w-19)}╮")
    print(f" │ {C['G']}nr save <cmd>{C['W']:<5} {C['GR']}•{C['W']} Save (use -g for group)                   │")
    print(f" │ {C['G']}nr run-group <N>{C['W']:<4} {C['GR']}•{C['W']} Execute group commands                 │")
    print(f" │ {C['G']}nr list{C['W']:<10} {C['GR']}•{C['W']} Show all commands                            │")
    print(f" ╰{'─'*w}╯")
    print(f"\n {C['W']}╭─ {C['M']}QUICK NOTES{C['W']} {'─'*(w-13)}╮")
    print(f" │ {C['M']}nr note add{C['W']:<8} {C['GR']}•{C['W']} Create a new note                          │")
    print(f" │ {C['M']}nr note ls{C['W']:<9} {C['GR']}•{C['W']} List all notes                              │")
    print(f" │ {C['M']}nr note view <ID>{C['W']:<3} {C['GR']}•{C['W']} Display note content                 │")
    print(f" ╰{'─'*w}╯")
    print(f"\n {C['W']}╭─ {C['Y']}SYSTEM{C['W']} {'─'*(w-8)}╮")
    print(f" │ {C['Y']}nr export{C['W']:<10} {C['GR']}•{C['W']} Export data to JSON                        │")
    print(f" │ {C['Y']}nr del <ID>{C['W']:<8} {C['GR']}•{C['W']} Delete a command                          │")
    print(f" ╰{'─'*w}╯{C['RST']}")

def show_list():
    rows = db.get_all_commands()
    if not rows: print(f" {C['R']}Empty.{C['RST']}"); return
    top, sep, bot = f" {C['C']}╭{'─'*5}┬{'─'*12}┬{'─'*22}┬{'─'*12}╮", f" {C['C']}├{'─'*5}┼{'─'*12}┼{'─'*22}┼{'─'*12}┤", f" {C['C']}╰{'─'*5}┴{'─'*12}┴{'─'*22}┴{'─'*12}╯"
    print(f"\n{top}\n │{C['W']} ID  {C['C']}│{C['W']} ALIAS      {C['C']}│{C['W']} COMMAND              {C['C']}│{C['W']} GROUP      {C['C']}│\n{sep}")
    for r in rows:
        alias = str(r[5])[:10] if r[5] else "---"
        print(f" │ {r[0]:<3} │ {alias:<10} │ {r[1][:20]:<20} │ {r[2]:<10} │")
    print(f"{bot}{C['RST']}")

def view_note(nid):
    res = db.get_note(nid)
    if not res: print(f" {C['R']}❌ Not found.{C['RST']}"); return
    title, content, date = res
    w = 56
    print(f"\n {C['M']}╭{'─'*w}╮\n │ {C['BOLD']}{C['W']}{title.center(w)}{C['RST']}{C['M']} │\n ├{'─'*w}┤")
    for line in content.splitlines():
        print(f" {C['M']}│{C['RST']}  {line[:w-4]:<{w-4}}  {C['M']}│")
    print(f" ╰{'─'*w}╯{C['RST']}")

def main():
    if len(sys.argv) < 2: return
    cmd = sys.argv[1]
    
    if cmd in ["-h", "--help"]: get_pro_help()
    elif cmd == "list": show_list()
    elif cmd == "save":
        group, parts = 'general', sys.argv[2:]
        if "-g" in parts:
            idx = parts.index("-g"); group = parts[idx+1]; parts = parts[:idx] + parts[idx+2:]
        if parts: db.add_command(" ".join(parts), group=group); print("✅ Saved.")
    elif cmd == "run-group" and len(sys.argv) > 2:
        for c, cid in db.get_by_group(sys.argv[2]):
            print(f"🚀 {C['G']}Running:{C['RST']} {c}")
            subprocess.run(c, shell=True); db.increment_usage(cid)
    elif cmd == "note":
        args = sys.argv[2:]
        if not args or args[0] == "ls":
            for n in db.get_all_notes(): print(f" {n[0]} 📄 {C['W']}{n[1]}{C['RST']}")
        elif args[0] == "add":
            title = " ".join(args[1:]) or "Untitled"
            with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tf:
                subprocess.call([os.environ.get('EDITOR', 'nano'), tf.name])
                with open(tf.name, 'r') as f: content = f.read()
            if content.strip(): db.add_note(title, content); print("✅ Note Saved.")
            os.remove(tf.name)
        elif args[0] == "view" and len(args) > 1: view_note(args[1])
    elif cmd == "export":
        path = os.path.expanduser("~/numrun_backup.json")
        with open(path, "w") as f: json.dump(db.get_backup_data(), f, indent=4)
        print(f"✅ Exported to: {path}")
    elif cmd == "del" and len(sys.argv) > 2:
        db.delete_cmd(sys.argv[2]); print("🗑️ Deleted.")

if __name__ == "__main__": main()
