import sys, subprocess, os, tempfile, json, getpass

# تصحيح مسار الاستدعاء لبيئة NixOS
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
    logo = fr"""{C['C']}    _   __              {C['B']}____ 
{C['C']}   / | / /_  ______ ___ {C['B']}/ __ \__  ______ 
{C['C']}  /  |/ / / / / __ `__ \{C['B']}/ /_/ / / / / __ \\
{C['C']} / /|  / /_/ / / / / / / {C['B']}_  __/ /_/ / / / /
{C['C']}/_/ |_/\__,_/_/ /_/ /_/{C['B']}_/ |_|\__,_/_/ /_/ {C['Y']}v0.1.0{C['RST']}"""
    print(logo)
    w = 58
    print(f"\n {C['W']}╭─ {C['G']}COMMANDS & GROUPS{C['W']} {'─'*(w-19)}╮")
    print(f" │ {C['G']}nr save <cmd>{C['W']:<5} {C['GR']}•{C['W']} Save (use -g for group)           │")
    print(f" │ {C['G']}nr run-group <N>{C['W']:<4} {C['GR']}•{C['W']} Execute all commands in group      │")
    print(f" │ {C['G']}nr list{C['W']:<10} {C['GR']}•{C['W']} View inventory table               │")
    print(f" ╰{'─'*w}╯")
    print(f"\n {C['W']}╭─ {C['M']}SECURE NOTEBOOK{C['W']} {'─'*(w-17)}╮")
    print(f" │ {C['M']}nr note add -e{C['W']:<5} {C['GR']}•{C['W']} Create encrypted note             │")
    print(f" │ {C['M']}nr note view <ID>{C['W']:<3} {C['GR']}•{C['W']} Open secure note                  │")
    print(f" ╰{'─'*w}╯")
    print(f"\n {C['W']}╭─ {C['Y']}SYSTEM TOOLS{C['W']} {'─'*(w-14)}╮")
    print(f" │ {C['Y']}nr export{C['W']:<10} {C['GR']}•{C['W']} Export data to JSON                │")
    print(f" │ {C['Y']}nr stats{C['W']:<11} {C['GR']}•{C['W']} View usage statistics              │")
    print(f" ╰{'─'*w}╯{C['RST']}")

def show_list():
    rows = db.get_all_commands()
    if not rows: print(f" {C['R']}Empty.{C['RST']}"); return
    top, sep, bot = f" {C['C']}╭{'─'*5}┬{'─'*12}┬{'─'*22}┬{'─'*12}╮", f" {C['C']}├{'─'*5}┼{'─'*12}┼{'─'*22}┼{'─'*12}┤", f" {C['C']}╰{'─'*5}┴{'─'*12}┴{'─'*22}┴{'─'*12}╯"
    print(f"\n{top}\n │{C['W']} ID  {C['C']}│{C['W']} ALIAS      {C['C']}│{C['W']} COMMAND              {C['C']}│{C['W']} GROUP      {C['C']}│\n{sep}")
    for r in rows:
        print(f" │ {r[0]:<3} │ {str(r[5])[:10]:<10} │ {r[1][:20]:<20} │ {r[2]:<10} │")
    print(f"{bot}{C['RST']}")

def main():
    if len(sys.argv) < 2:
        # FZF Search Logic (يظل كما هو)
        return

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
            print(f"🚀 {c}"); subprocess.run(c, shell=True); db.increment_usage(cid)
    elif cmd == "note":
        args = sys.argv[2:]
        if not args or args[0] == "ls":
            for n in db.get_all_notes():
                print(f" {n[0]} {'🔒' if n[2] else '📄'} {n[1]}")
        elif args[0] == "add":
            is_enc = "-e" in args
            title = " ".join([a for a in args[1:] if a != "-e"])
            pwd = getpass.getpass(" Password: ") if is_enc else None
            with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tf:
                subprocess.call([os.environ.get('EDITOR', 'nano'), tf.name])
                with open(tf.name, 'r') as f: content = f.read()
            if content.strip(): db.add_note(title, content, pwd); print("✅ Saved.")
            os.remove(tf.name)
        elif args[0] == "view" and len(args) > 1:
            # دالة view_note السابقة
            pass
    elif cmd == "export":
        with open("numrun_v010.json", "w") as f: json.dump(db.get_backup_data(), f)
        print("✅ Exported.")

if __name__ == "__main__": main()
