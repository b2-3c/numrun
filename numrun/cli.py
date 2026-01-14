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
    print(f" │ {C['G']}nr{C['W']:<15} {C['GR']}•{C['W']} Interactive search with fzf            │")
    print(f" │ {C['G']}nr <ID/Alias>{C['W']:<5} {C['GR']}•{C['W']} Run command directly                   │")
    print(f" │ {C['G']}nr save <cmd>{C['W']:<5} {C['GR']}•{C['W']} Save with smart alias suggestion       │")
    print(f" │ {C['G']}nr list{C['W']:<10} {C['GR']}•{C['W']} Show all saved commands                      │")
    print(f" ╰{'─'*w}╯{C['RST']}")

def interactive_fzf():
    """البحث باستخدام fzf"""
    rows = db.get_all_commands()
    if not rows:
        print(f" {C['R']}⚠ No commands found.{C['RST']}")
        return
    
    # تنسيق الأسطر لـ fzf
    lines = [f"{r['cmd_number']} | { (r['alias'] or '---'):<10} | {r['command']}" for r in rows]
    input_str = "\n".join(lines)
    
    try:
        process = subprocess.Popen(
            ['fzf', '--ansi', '--header', 'Select Command (ESC to exit)', '--reverse'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
        )
        stdout, _ = process.communicate(input=input_str)
        if stdout:
            selected_id = stdout.split('|')[0].strip()
            run_by_id(selected_id)
    except FileNotFoundError:
        print(f" {C['R']}❌ 'fzf' is not installed. Run 'nr list' instead.{C['RST']}")

def run_by_id(identifier):
    all_cmds = db.get_all_commands()
    for r in all_cmds:
        if str(r['cmd_number']) == identifier or (r['alias'] and r['alias'] == identifier):
            print(f"{C['B']}🚀 Running:{C['RST']} {r['command']}")
            subprocess.run(r['command'], shell=True)
            db.increment_usage(r['cmd_number'])
            return True
    return False

def show_list():
    rows = db.get_all_commands()
    if not rows:
        print(f"\n {C['R']}⚠ Empty list.{C['RST']}")
        return
    print(f"\n {C['C']}╭{'─'*5}┬{'─'*12}┬{'─'*24}┬{'─'*12}╮")
    for r in rows:
        alias = (r['alias'] or "---")[:10]
        cmd_disp = (r['command'][:21] + "..") if len(r['command']) > 21 else r['command']
        print(f" │ {C['Y']}{str(r['cmd_number']):<3} {C['C']}│ {C['G']}{alias:<10} {C['C']}│ {C['W']}{cmd_disp:<22} {C['C']}│ {C['M']}{r['group_name']:<10} {C['C']}│")
    print(f" {C['C']}╰{'─'*5}┴{'─'*12}┴{'─'*24}┴{'─'*12}╯{C['RST']}")

def main():
    # 1. حالة كتابة nr فقط
    if len(sys.argv) < 2:
        interactive_fzf()
        return

    cmd = sys.argv[1]
    
    # 2. المساعدة أولاً
    if cmd in ["-h", "--help"]:
        get_pro_help()
    
    elif cmd == "list":
        show_list()
        
    elif cmd == "save":
        args = sys.argv[2:]
        if not args: return
        group = 'general'
        if "-g" in args:
            idx = args.index("-g"); group = args[idx+1]; args = args[:idx] + args[idx+2:]
        
        command = " ".join(args)
        if command:
            # اقتراح البداية والنهاية
            first_w = args[0]
            suggested = (first_w[0] + first_w[-1]).lower() if len(first_w) > 1 else first_w[0].lower()
            
            print(f" {C['Y']}❓ Alias for: {C['W']}{command}{C['RST']}")
            user_input = input(f" {C['C']}Alias (Enter for '{suggested}'): {C['RST']}").strip()
            alias = user_input if user_input else suggested
            
            if db.add_command(command, alias=alias, group=group):
                print(f" {C['G']}✅ Saved as '{alias}'{C['RST']}")
            else:
                db.add_command(command, alias=None, group=group)
                print(f" {C['R']}⚠ Alias exists. Saved by ID.{C['RST']}")

    elif cmd == "note":
        args = sys.argv[2:]
        if not args or args[0] == "ls":
            for n in db.get_all_notes(): print(f" {n['note_id']} 📄 {C['W']}{n['title']}{C['RST']}")
        elif args[0] == "add":
            title = " ".join(args[1:]) or "Untitled"
            with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tf:
                subprocess.call([os.environ.get('EDITOR', 'nano'), tf.name])
                with open(tf.name, 'r') as f: content = f.read()
            if content.strip(): db.add_note(title, content); print("✅ Saved.")
            os.remove(tf.name)
        elif args[0] == "view" and len(args) > 1:
            res = db.get_note(args[1])
            if res: print(f"\n{C['M']}{res['title']}{C['RST']}\n{res['content']}")

    elif cmd == "del" and len(sys.argv) > 2:
        if db.delete_cmd(sys.argv[2]): print("🗑️ Deleted.")

    else:
        # 3. التشغيل السريع (ID/Alias)
        if not run_by_id(cmd):
            print(f"{C['R']}❌ Unknown: {cmd}{C['RST']}")

if __name__ == "__main__":
    main()
