import sys, subprocess, os, tempfile, time, platform, re
from database import Database

db = Database()
VERSION = "1.0.2"

C = {"B": "\033[1;34m", "C": "\033[1;36m", "G": "\033[1;32m", "R": "\033[1;31m",
     "Y": "\033[1;33m", "M": "\033[1;35m", "W": "\033[1;37m", "GR": "\033[90m", "RST": "\033[0m"}

def get_uptime():
    try:
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.readline().split()[0])
            return f"{int(uptime_seconds // 3600)}h {int((uptime_seconds % 3600) // 60)}m"
    except: return "N/A"

def show_info():
    user, host = os.getenv("USER") or "User", platform.node()
    cmds, notes = len(db.get_all_commands()), len(db.get_all_notes())
    print(f"\n{C['C']}{user}{C['W']}@{C['C']}{host}{C['RST']}")
    print(f"{C['GR']}------------------------------------------{C['RST']}")
    print(f"{C['Y']}Version  {C['W']}: {C['G']}{VERSION}")
    print(f"{C['Y']}Uptime   {C['W']}: {C['G']}{get_uptime()}")
    print(f"{C['Y']}Storage  {C['W']}: {C['M']}{cmds} Commands / {notes} Notes\n")

def show_help():
    print(f"\n{C['C']}NumRun Help Center - v{VERSION}{C['RST']}")
    print(f"{C['GR']}------------------------------------------{C['RST']}")
    print(f"{C['Y']}1. Basic   {C['W']}: -i (Info), -c (List), -n (Notes)")
    print(f"{C['Y']}2. Manage  {C['W']}: c-a (Add), n-a (Note), e-c, d-c")
    print(f"{C['Y']}3. Advanced{C['W']}: f-c (Fav), fav (List), #tag (Search)")
    print(f"{C['Y']}4. Tools   {C['W']}: var (Vars), tpl (Tpls), -p (Timer)\n")

def list_styled(mode="c"):
    if mode == "c" or mode == "fav":
        cmds = db.get_all_commands(fav_only=(mode=="fav"))
        print(f"\n{C['GR']}ID   FAV  ALIAS     COMMAND{C['RST']}")
        print(f"{C['GR']}------------------------------------------{C['RST']}")
        for r in cmds:
            fav = f"{C['Y']}⭐{C['RST']}" if r['is_fav'] else "  "
            alias = f"{C['G']}{(str(r['alias']) if r['alias'] else 'None'):<8}"
            note = f" {C['B']}# {r['note_inline']}" if r['note_inline'] else ""
            print(f"{C['Y']}{r['cmd_number']:<3}  {fav}  {alias}  {C['W']}{r['command']}{note}")
    else:
        print(f"\n{C['GR']}ID   NOTE TITLE           CREATED AT{C['RST']}")
        print(f"{C['GR']}------------------------------------------{C['RST']}")
        for n in db.get_all_notes():
            print(f"{C['Y']}{n['note_id']:<3}  {C['M']}📄 {n['title']:<15}  {C['GR']}{n['created_at']}")
    print("")

def execute_logic(cmd_text):
    for k, v in db.get_vars().items(): cmd_text = cmd_text.replace(f"${k}", v)
    if any(x in cmd_text for x in ["rm -rf", "shutdown", "dd ", "mkfs"]):
        print(f"\n{C['R']}🛑 WARNING: Dangerous command!{C['RST']}")
        if input("Confirm execution? (y/N): ").lower() != 'y': return
    print(f"\n{C['Y']}▶ {C['W']}{cmd_text}{C['RST']}")
    if input(f"{C['GR']}[Y/n] {C['RST']}").lower() in ['y', '']:
        subprocess.run(cmd_text, shell=True)

def main():
    if len(sys.argv) < 2: list_styled(); return
    arg = sys.argv[1]

    if arg == "-i": show_info()
    elif arg == "-h": show_help()
    elif arg == "-c": list_styled("c")
    elif arg == "-n": list_styled("n")
    elif arg == "c-a":
        f_cmd = " ".join(sys.argv[2:])
        if not f_cmd: return
        al, nt, tg = input(f"{C['C']}➜ Alias: ").strip() or None, input(f"{C['C']}➜ Note: ").strip(), input(f"{C['C']}➜ Tags: ").strip()
        db.add_command(f_cmd, al, tg, nt); print("✅ Saved.")
    elif arg == "n-a":
        t = " ".join(sys.argv[2:]) or "Untitled"
        with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tf:
            subprocess.call([os.environ.get('EDITOR', 'nano'), tf.name])
            with open(tf.name, 'r') as f: content = f.read()
        if content.strip(): db.add_note(t, content); print("✅ Saved.")
    elif arg == "fav": list_styled("fav")
    elif arg == "f-c" and len(sys.argv) > 2:
        db.toggle_fav(sys.argv[2]); print("⭐ Toggled.")
    elif arg.startswith("#"):
        tag = arg[1:]
        for r in db.get_all_commands():
            if tag in str(r['tags']): print(f"{C['Y']}{r['cmd_number']} {C['W']}| {r['command']}")
    elif arg == "var" and len(sys.argv) > 3 and sys.argv[2] == "set":
        db.set_var(sys.argv[3], sys.argv[4]); print("✅ Var Saved.")
    elif arg == "tpl" and sys.argv[2] == "add":
        db.add_tpl(sys.argv[3], " ".join(sys.argv[4:])); print("✅ Template saved.")
    elif arg == "run":
        tpl = db.get_tpl(sys.argv[2])
        if tpl:
            for p in sys.argv[3:]:
                if '=' in p: k, v = p.split('='); tpl = tpl.replace(f"{{{k}}}", v)
            execute_logic(tpl)
    elif arg == "-p":
        raw_val = sys.argv[2] if len(sys.argv) > 2 else "25"
        mins = int(re.sub("[^0-9]", "", raw_val)) # يستخرج الأرقام فقط من 3m
        print(f"{C['M']}⏳ Pomodoro: {mins}m focus session.{C['RST']}")
        for i in range(mins*60, 0, -1):
            m, s = divmod(i, 60)
            print(f"\r{C['Y']}Time left: {m:02d}:{s:02d}", end=""); time.sleep(1)
        db.log_pomodoro(datetime.now().strftime("%Y-%m-%d"), "Work", mins); print("\n✅ Done!")
    elif arg == "e-c" and len(sys.argv) > 2:
        db.update_command(sys.argv[2], input("New Cmd: "), input("New Alias: ")); print("✅")
    elif arg == "d-c" and len(sys.argv) > 2:
        db.delete_cmd(sys.argv[2]); print("🗑️ Deleted.")
    else:
        for r in db.get_all_commands():
            if str(r['cmd_number']) == arg or r['alias'] == arg:
                execute_logic(r['command']); return
        print(f"❌ Unknown command: {arg}")

if __name__ == "__main__":
    main()
