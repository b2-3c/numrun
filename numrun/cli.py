import sys, subprocess, os, platform, tempfile

try: from numrun.database import Database
except ImportError: from database import Database

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
{C['C']}/_/ |_/\__,_/_/ /_/ /_/{C['B']}_/ |_|\__,_/_/ /_/ {C['GR']}v0.8.1{C['RST']}"""
    
    print(logo)
    w = 58 # عرض ثابت لجميع الصناديق
    
    # قسم الأوامر
    print(f"\n {C['W']}╭─ {C['G']}PRIMARY COMMANDS{C['W']} {'─'*(w-20)}╮")
    print(f" │ {C['G']}nr{C['W']:<14} {C['GR']}•{C['W']} Search & Run (FZF Mode)          │")
    print(f" │ {C['G']}nr save <cmd>{C['W']:<5} {C['GR']}•{C['W']} Save command to database          │")
    print(f" │ {C['G']}nr list{C['W']:<10} {C['GR']}•{C['W']} Advanced table view                │")
    print(f" ╰{'─'*w}╯")
    
    # قسم المفكرة
    print(f"\n {C['W']}╭─ {C['M']}NOTEBOOK SYSTEM{C['W']} {'─'*(w-19)}╮")
    print(f" │ {C['M']}nr note add{C['W']:<6} {C['GR']}•{C['W']} Write and save a text note         │")
    print(f" │ {C['M']}nr note ls{C['W']:<7} {C['GR']}•{C['W']} Show all saved notes               │")
    print(f" │ {C['M']}nr note view{C['W']:<5} {C['GR']}•{C['W']} Read note content (nr note view 1) │")
    print(f" ╰{'─'*w}╯")
    
    # قسم الإحصائيات
    print(f"\n {C['W']}╭─ {C['Y']}SYSTEM & STATS{C['W']} {'─'*(w-18)}╮")
    print(f" │ {C['Y']}nr stats{C['W']:<11} {C['GR']}•{C['W']} Performance & Usage Graph          │")
    print(f" │ {C['Y']}nr del <id>{C['W']:<9} {C['GR']}•{C['W']} Remove command from database       │")
    print(f" ╰{'─'*w}╯{C['RST']}")

def show_list():
    rows = db.get_all_commands()
    if not rows:
        print(f"\n {C['R']}⚠ Database empty. Use 'nr save <cmd>'{C['RST']}"); return

    print(f"\n {C['B']}{C['BOLD']}📋 COMMAND INVENTORY{C['RST']}")
    top = f" {C['C']}╭{'─'*5}┬{'─'*12}┬{'─'*32}┬{'─'*7}╮{C['RST']}"
    sep = f" {C['C']}├{'─'*5}┼{'─'*12}┼{'─'*32}┼{'─'*7}┤{C['RST']}"
    bot = f" {C['C']}╰{'─'*5}┴{'─'*12}┴{'─'*32}┴{'─'*7}╯{C['RST']}"
    
    print(top)
    print(f" {C['C']}│{C['W']} {'ID':<3} {C['C']}│{C['W']} {'ALIAS':<10} {C['C']}│{C['W']} {'COMMAND':<30} {C['C']}│{C['W']} {'RUNS':<5} {C['C']}│")
    print(sep)
    for r in rows:
        alias = (r[5][:10]) if r[5] else "---"
        cmd = (r[1][:27] + "..") if len(r[1]) > 27 else r[1]
        print(f" {C['C']}│{C['W']} {r[0]:<3} {C['C']}│{C['Y']} {alias:<10} {C['C']}│{C['W']} {cmd:<30} {C['C']}│{C['G']} {r[3]:<5} {C['C']}│")
    print(bot)

def view_note(nid):
    res = db.get_note_by_id(nid)
    if not res: return
    w = 56
    print(f"\n {C['M']}╭{'─'*w}╮")
    print(f" │ {C['BOLD']}{C['W']}{res[0].center(w)}{C['RST']}{C['M']} │")
    print(f" ├{'─'*w}┤")
    for line in res[1].splitlines():
        chunks = [line[i:i+(w-4)] for i in range(0, len(line), w-4)]
        for chunk in chunks: print(f" {C['M']}│{C['RST']}  {chunk:<{w-4}}  {C['M']}│")
    print(f" ├{'─'*w}┤")
    print(f" │ {C['GR']}{res[3].center(w)}{C['RST']}{C['M']} │")
    print(f" ╰{'─'*w}╯{C['RST']}")

def execute_logic(identifier, args):
    res = db.get_by_id_or_alias(identifier)
    if not res: return False
    cmd, cid, _ = res
    for i, arg in enumerate(args, 1): cmd = cmd.replace(f"${i}", arg)
    print(f" {C['B']}🚀 Executing: {C['W']}{cmd}{C['RST']}")
    db.increment_usage(cid)
    subprocess.run(cmd, shell=True)
    return True

def main():
    if len(sys.argv) < 2:
        # البحث التفاعلي الموحد
        try:
            cmds = [f"[CMD] {r[0]} | {r[5] or '-'} | {r[1]}" for r in db.get_all_commands()]
            notes = [f"[NOTE] {r[0]} | {r[1]}" for r in db.get_all_notes()]
            combined = "\n".join(cmds + notes)
            fzf = subprocess.Popen(['fzf', '--ansi', '--reverse', '--header', 'NumRun Global Search'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            stdout, _ = fzf.communicate(input=combined.encode())
            if stdout:
                line = stdout.decode()
                val = line.split("|")[0].strip()
                if "[CMD]" in line: execute_logic(val.replace("[CMD]", "").strip(), [])
                else: view_note(val.replace("[NOTE]", "").strip())
        except: print(f" {C['Y']}💡 Hint: 'nr -h' for help.{C['RST']}")
        return

    cmd = sys.argv[1]
    if cmd in ["-h", "--help"]: get_pro_help()
    elif cmd == "list": show_list()
    elif cmd == "stats":
        rows = db.conn.execute("SELECT command, usage_count FROM commands WHERE usage_count > 0 ORDER BY usage_count DESC LIMIT 5").fetchall()
        print(f"\n {C['Y']}📊 TOP COMMANDS{C['RST']}")
        for r in rows: print(f" {C['W']}{r[0][:20]:<20} {C['G']}{'█'*r[1]} ({r[1]})")
    elif cmd == "note":
        args = sys.argv[2:]
        if not args or args[0] == "ls":
            for n in db.get_all_notes(): print(f" {C['Y']}{n[0]:<3} {C['W']}➜ {n[1]}")
        elif args[0] == "add":
            title = " ".join(args[1:]) or "New Note"
            with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tf: tf_path = tf.name
            subprocess.call([os.environ.get('EDITOR', 'nano'), tf_path])
            with open(tf_path, 'r') as f: content = f.read()
            if content.strip(): db.add_note(title, content)
            os.remove(tf_path); print("✅ Saved.")
        elif args[0] == "view": view_note(args[1])
        elif args[0] == "del": db.delete_note(args[1]); print("🗑️ Deleted.")
    elif cmd == "save":
        txt = " ".join(sys.argv[2:])
        if txt: db.add_command(txt); print("✅ Saved.")
    elif cmd == "del":
        if len(sys.argv) > 2: db.delete_cmd(sys.argv[2]); print("🗑️ Deleted.")
    else: execute_logic(cmd, sys.argv[2:])

if __name__ == "__main__": main()
