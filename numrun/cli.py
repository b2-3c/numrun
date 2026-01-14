import sys, subprocess, os, tempfile, json, re

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

DANGEROUS_KEYS = ["rm ", "mkfs", "dd ", "> /dev/sd", "shutdown", "reboot"]

def smart_guard(command):
    if any(key in command for key in DANGEROUS_KEYS):
        print(f"\n{C['Y']}⚠️  DANGER DETECTED: {C['W']}{command}{C['RST']}")
        confirm = input(f" {C['R']}Confirm execution? (y/N): {C['RST']}")
        return confirm.lower() == 'y'
    return True

def get_pro_help():
    logo = fr"""{C['C']}    _   __              {C['B']}  ____ 
{C['C']}   / | / /_  ______ ___ {C['B']} / __  \__  ______ 
{C['C']}  /  |/ / / / / __ `__ \{C['B']}/ /_/  / / /  / __ \\
{C['C']} / /|  / /_/ / / / / / / {C['B']}_  __/ /_/  / / / /
{C['C']}/_/ |_/\__,_/_/ /_/ /_/{C['B']}_/ |_|\__,_/_/ /_/ {C['Y']}v0.1.5{C['RST']}"""
    print(logo)
    w = 60
    print(f"\n {C['W']}╭─ {C['G']}COMMANDS{C['W']} {'─'*(w-10)}╮")
    print(f" │ {C['G']}nr{C['W']:<15} {C['GR']}•{C['W']} Interactive search (FZF)               │")
    print(f" │ {C['G']}nr <ID> [args]{C['W']:<4} {C['GR']}•{C['W']} Run command with dynamic args          │")
    print(f" │ {C['G']}nr save \"cmd\"{C['W']:<5} {C['GR']}•{C['W']} Save (use -g for group, -a for alias)  │")
    print(f" │ {C['G']}nr run-group <G>{C['W']:<3} {C['GR']}•{C['W']} Execute all commands in group           │")
    print(f" ╰{'─'*w}╯")
    print(f" {C['W']}╭─ {C['M']}NOTES & SYSTEM{C['W']} {'─'*(w-16)}╮")
    print(f" │ {C['M']}nr note add{C['W']:<8} {C['GR']}•{C['W']} Create note (opens $EDITOR)            │")
    print(f" │ {C['M']}nr export{C['W']:<10} {C['GR']}•{C['W']} Backup to ~/numrun_backup.json         │")
    print(f" │ {C['M']}nr del <ID>{C['W']:<8} {C['GR']}•{C['W']} Delete command                         │")
    print(f" ╰{'─'*w}╯{C['RST']}")

def execute_final(command, args=[]):
    # دعم المعاملات الديناميكية مثل $1, $2
    final_cmd = command
    for i, arg in enumerate(args, 1):
        final_cmd = final_cmd.replace(f"${i}", arg)
    
    if smart_guard(final_cmd):
        print(f"{C['B']}🚀 Executing:{C['RST']} {final_cmd}")
        subprocess.run(final_cmd, shell=True)
        return True
    return False

def interactive_fzf():
    rows = db.get_all_commands()
    if not rows: return
    lines = [f"{r['cmd_number']} | {(r['alias'] or '---'):<10} | {r['command']}" for r in rows]
    try:
        process = subprocess.Popen(['fzf', '--ansi', '--reverse'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        stdout, _ = process.communicate(input="\n".join(lines))
        if stdout:
            selected_id = stdout.split('|')[0].strip()
            run_by_identifier(selected_id)
    except FileNotFoundError: print(f"{C['R']}❌ fzf not found.{C['RST']}")

def run_by_identifier(identifier, extra_args=[]):
    all_cmds = db.get_all_commands()
    for r in all_cmds:
        if str(r['cmd_number']) == identifier or (r['alias'] and r['alias'] == identifier):
            if execute_final(r['command'], extra_args):
                db.increment_usage(r['cmd_number'])
            return True
    return False

def show_list():
    rows = db.get_all_commands()
    print(f"\n {C['C']}ID  │ ALIAS      │ COMMAND{' '*15} │ GROUP")
    print(f" {'─'*60}")
    for r in rows:
        alias = (r['alias'] or "---")[:10]
        cmd = (r['command'][:25] + "..") if len(r['command']) > 25 else r['command']
        print(f" {C['Y']}{str(r['cmd_number']):<3} {C['C']}│ {C['G']}{alias:<10} {C['C']}│ {C['W']}{cmd:<26} {C['C']}│ {C['M']}{r['group_name']}")

def main():
    if len(sys.argv) < 2:
        interactive_fzf(); return

    cmd = sys.argv[1]
    
    if cmd in ["-h", "--help"]: get_pro_help()
    elif cmd == "list": show_list()
    elif cmd == "export":
        path = os.path.expanduser("~/numrun_backup.json")
        with open(path, "w") as f: json.dump(db.get_backup_data(), f, indent=4)
        print(f" {C['G']}✅ Exported to {path}{C['RST']}")
    
    elif cmd == "save":
        parts = sys.argv[2:]
        group, alias = 'general', None
        if "-g" in parts:
            idx = parts.index("-g"); group = parts[idx+1]; parts = parts[:idx] + parts[idx+2:]
        if "-a" in parts:
            idx = parts.index("-a"); alias = parts[idx+1]; parts = parts[:idx] + parts[idx+2:]
        
        full_cmd = " ".join(parts)
        if full_cmd:
            if not alias:
                first_w = parts[0]
                suggested = (first_w[0] + first_w[-1]).lower() if len(first_w) > 1 else first_w[0].lower()
                user_alias = input(f" {C['Y']}Alias (Enter for '{suggested}'): {C['RST']}").strip()
                alias = user_alias if user_alias else suggested
            
            db.add_command(full_cmd, alias=alias, group=group)
            print(f" {C['G']}✅ Saved as #{alias if alias else 'ID'}{C['RST']}")

    elif cmd == "run-group" and len(sys.argv) > 2:
        for r in db.get_by_group(sys.argv[2]):
            execute_final(r['command']); db.increment_usage(r['cmd_number'])

    elif cmd == "note":
        args = sys.argv[2:]
        if not args or args[0] == "ls":
            for n in db.get_all_notes(): print(f" {n['note_id']} 📄 {n['title']}")
        elif args[0] == "add":
            title = " ".join(args[1:]) or "Untitled"
            with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tf:
                subprocess.call([os.environ.get('EDITOR', 'nano'), tf.name])
                with open(tf.name, 'r') as f: content = f.read()
            if content.strip(): db.add_note(title, content); print("✅ Note Saved.")
        elif args[0] == "view" and len(args) > 1:
            res = db.get_note(args[1])
            if res: print(f"\n{C['M']}{res['title']}{C['RST']}\n{res['content']}")

    elif cmd == "del" and len(sys.argv) > 2:
        if db.delete_cmd(sys.argv[2]): print("🗑️ Deleted.")

    else:
        if not run_by_identifier(cmd, sys.argv[2:]):
            print(f"{C['R']}❌ Unknown command: {cmd}{C['RST']}")

if __name__ == "__main__":
    main()
