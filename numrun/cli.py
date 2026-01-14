import sys, subprocess, os, tempfile, json

# ضمان استيراد قاعدة البيانات من نفس المسار
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from database import Database
except ImportError:
    from numrun.database import Database

db = Database()

# الألوان
C = {
    "B": "\033[1;34m", "C": "\033[1;36m", "G": "\033[1;32m", "R": "\033[1;31m",
    "Y": "\033[1;33m", "M": "\033[1;35m", "W": "\033[1;37m", "GR": "\033[90m",
    "RST": "\033[0m", "BOLD": "\033[1m"
}

DANGEROUS = ["rm ", "mkfs", "dd ", "> /dev/", "shutdown", "reboot"]

def smart_guard(cmd_text):
    if any(k in cmd_text for k in DANGEROUS):
        print(f"\n{C['Y']}⚠️  DANGER DETECTED: {C['W']}{cmd_text}{C['RST']}")
        return input(f" {C['R']}Confirm execution? (y/N): {C['RST']}").lower() == 'y'
    return True

def execute_final(command, args=[]):
    # معالجة المعاملات الديناميكية $1, $2 الخ
    for i, arg in enumerate(args, 1):
        command = command.replace(f"${i}", arg)
    
    if smart_guard(command):
        print(f"{C['B']}🚀 Executing:{C['RST']} {command}")
        subprocess.run(command, shell=True)
        return True
    return False

def show_list():
    rows = db.get_all_commands()
    if not rows:
        print(f"\n {C['R']}⚠ No commands found.{C['RST']}")
        return
    print(f"\n {C['C']}ID  │ ALIAS      │ COMMAND (Short Preview)")
    print(f" {'─'*55}")
    for r in rows:
        alias = (r['alias'] or "---")[:10]
        cmd = (r['command'][:30] + "..") if len(r['command']) > 30 else r['command']
        print(f" {C['Y']}{str(r['cmd_number']):<3} {C['C']}│ {C['G']}{alias:<10} {C['C']}│ {C['W']}{cmd}")

def get_pro_help():
    logo = fr"""{C['C']}    _   __              {C['B']}  ____ 
{C['C']}   / | / /_  ______ ___ {C['B']} / __  \__  ______ 
{C['C']}  /  |/ / / / / __ `__ \{C['B']}/ /_/  / / /  / __ \\
{C['C']} / /|  / /_/ / / / / / / {C['B']}_  __/ /_/  / / / /
{C['C']}/_/ |_/\__,_/_/ /_/ /_/{C['B']}_/ |_|\__,_/_/ /_/ {C['Y']}v0.2.0{C['RST']}"""
    print(logo)
    print(f"\n {C['G']}nr{C['W']:<15} {C['GR']}•{C['W']} Visual Search (FZF)")
    print(f" {C['G']}nr save \"cmd\"{C['W']:<8} {C['GR']}•{C['W']} Save command (Auto-alias suggestion)")
    print(f" {C['G']}nr <ID/Alias> [args]{C['GR']} •{C['W']} Run command with dynamic arguments")
    print(f" {C['G']}nr edit <ID>{C['W']:<10} {C['GR']}•{C['W']} Update command text")
    print(f" {C['G']}nr alias set <ID> <A>{C['GR']}•{C['W']} Set custom alias")
    print(f" {C['G']}nr note add <T>{C['W']:<6} {C['GR']}•{C['W']} New note ($EDITOR)")
    print(f" {C['G']}nr export{C['W']:<11} {C['GR']}•{C['W']} Backup to JSON")

def main():
    if len(sys.argv) < 2:
        # وضع البحث التفاعلي FZF
        rows = db.get_all_commands()
        if not rows: print("List is empty."); return
        lines = [f"{r['cmd_number']} | {(r['alias'] or '---'):<10} | {r['command']}" for r in rows]
        try:
            p = subprocess.Popen(['fzf', '--ansi', '--reverse', '--header=Select to Run'], 
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            out, _ = p.communicate(input="\n".join(lines))
            if out: execute_final(out.split('|')[2].strip())
        except FileNotFoundError:
            show_list()
        return

    cmd = sys.argv[1]

    if cmd in ["-h", "--help"]: get_pro_help()
    
    elif cmd == "list": show_list()

    elif cmd == "save":
        parts = sys.argv[2:]
        if not parts: return
        full_cmd = " ".join(parts)
        first_w = parts[0]
        # اقتراح البداية والنهاية
        sugg = (first_w[0] + first_w[-1]).lower() if len(first_w) > 1 else first_w[0]
        alias = input(f" {C['Y']}Alias (Enter for '{sugg}'): {C['RST']}").strip() or sugg
        if db.add_command(full_cmd, alias=alias):
            print(f" {C['G']}✅ Saved as '{alias}'{C['RST']}")
        else:
            db.add_command(full_cmd, alias=None)
            print(f" {C['R']}⚠ Alias taken. Saved by ID.{C['RST']}")

    elif cmd == "edit" and len(sys.argv) > 2:
        cid = sys.argv[2]
        new_cmd = input(f" {C['C']}New command: {C['RST']}")
        if new_cmd: db.update_command(cid, new_cmd); print("✅ Updated.")

    elif cmd == "alias":
        args = sys.argv[2:]
        if args[0] == "set" and len(args) >= 3:
            if db.update_alias(args[1], args[2]): print("✅ Alias Set.")
            else: print("❌ Alias already exists.")
        elif args[0] == "del" and len(args) >= 2:
            db.update_alias(args[1], None); print("🗑️ Alias Removed.")

    elif cmd == "del" and len(sys.argv) > 2:
        if db.delete_cmd(sys.argv[2]): print("🗑️ Command Deleted.")

    elif cmd == "note":
        args = sys.argv[2:]
        if args[0] == "add":
            title = " ".join(args[1:]) or "Untitled"
            with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tf:
                subprocess.call([os.environ.get('EDITOR', 'nano'), tf.name])
                with open(tf.name, 'r') as f: content = f.read()
            if content.strip(): db.add_note(title, content); print("✅ Note Saved.")
        elif args[0] == "ls":
            for n in db.get_all_notes(): print(f" {n['note_id']} 📄 {n['title']}")
        elif args[0] == "view" and len(args) > 1:
            res = db.get_note(args[1])
            if res: print(f"\n{C['M']}{res['title']}{C['RST']}\n{res['content']}")

    elif cmd == "export":
        path = os.path.expanduser("~/numrun_backup.json")
        with open(path, "w") as f: json.dump(db.get_backup_data(), f, indent=4)
        print(f"✅ Backup created at {path}")

    else:
        # البحث عن ID أو Alias للتشغيل الفوري
        found = False
        for r in db.get_all_commands():
            if str(r['cmd_number']) == cmd or r['alias'] == cmd:
                if execute_final(r['command'], sys.argv[2:]):
                    db.increment_usage(r['cmd_number'])
                found = True; break
        if not found: print(f"{C['R']}❌ Unknown command or ID: {cmd}{C['RST']}")

if __name__ == "__main__":
    main()
