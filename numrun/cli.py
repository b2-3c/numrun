import sys, subprocess, os, tempfile, time, platform

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import Database

db = Database()
VERSION = "1.0.1"

C = {
    "B": "\033[1;34m", "C": "\033[1;36m", "G": "\033[1;32m", "R": "\033[1;31m",
    "Y": "\033[1;33m", "M": "\033[1;35m", "W": "\033[1;37m", "GR": "\033[90m",
    "RST": "\033[0m", "UL": "\033[4m"
}

def get_uptime():
    try:
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.readline().split()[0])
            h = int(uptime_seconds // 3600)
            m = int((uptime_seconds % 3600) // 60)
            return f"{h}h {m}m"
    except: return "N/A"

def show_info():
    user = os.getenv("USER") or "User"
    host = platform.node()
    distro = "Linux"
    if os.path.exists("/etc/os-release"):
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="): distro = line.split("=")[1].strip('" \n')

    cmd_c, note_c = db.get_stats()
    
    info = [
        f"{C['C']}{user}{C['W']}@{C['C']}{host}",
        f"{C['GR']}{'-' * (len(user) + len(host) + 1)}",
        f"{C['Y']}Tool    {C['W']}: {C['G']}numrun",
        f"{C['Y']}Version {C['W']}: {C['G']}{VERSION}",
        f"{C['Y']}OS      {C['W']}: {C['G']}{distro}",
        f"{C['Y']}Uptime  {C['W']}: {C['G']}{get_uptime()}",
        f"{C['Y']}Data    {C['W']}: {C['M']}{cmd_c} Cmds / {note_c} Notes"
    ]

    logo = ["", f"     {C['Y']}▄▀ ▄▀", f"     {C['Y']} ▀  ▀", f"    {C['Y']} █▀▀▀▀▀█▄", f"    {C['Y']} █░░░░░█ █", f"    {C['Y']} ▀▄▄▄▄▄▀▀"]

    print("")
    for i in range(max(len(info), len(logo))):
        l = logo[i] if i < len(logo) else ""
        r = info[i] if i < len(info) else ""
        cl = l.replace(C['Y'], "").replace(C['RST'], "")
        print(f"{l}{' ' * (18 - len(cl))}{r}")
    print("")

def smart_fzf(mode="all"):
    items = []
    if mode in ["all", "c"]:
        for r in db.get_all_commands(): items.append(f"{C['G']}[CMD]{C['RST']} {r['cmd_number']} | {r['alias'] or '---'} | {r['command']}")
    if mode in ["all", "n"]:
        for n in db.get_all_notes(): items.append(f"{C['M']}[NOTE]{C['RST']} {n['note_id']} | {n['title']}")
    
    if not items: return
    try:
        hdr = "ALL" if mode=="all" else ("COMMANDS" if mode=="c" else "NOTES")
        p = subprocess.Popen(['fzf', '--ansi', '--reverse', '--header', f'| SEARCH: {hdr} |'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        out, _ = p.communicate(input="\n".join(items))
        if out:
            if "[CMD]" in out:
                cmd_exec = out.split('|')[2].strip()
                print(f"{C['Y']}Running: {C['W']}{cmd_exec}{C['RST']}")
                subprocess.run(cmd_exec, shell=True)
            elif "[NOTE]" in out:
                nid = out.split('|')[0].replace("[NOTE]", "").strip()
                res = db.get_note(nid)
                if res: print(f"\n{C['M']}--- {res['title']} ---{C['RST']}\n{res['content']}\n")
    except: print("fzf error.")

def show_help():
    h = f"""
    {C['C']}NUMRUN {C['G']}v{VERSION}{C['RST']} - Command & Note Manager

    {C['Y']}{C['UL']}USAGE:{C['RST']}
      {C['W']}nr {C['G']}[id/alias]   {C['GR']}# Run stored command by ID or Alias
      {C['W']}nr {C['G']}s            {C['GR']}# Global search (Cmds + Notes) using fzf
    
    {C['Y']}{C['UL']}SEARCH:{C['RST']}
      {C['G']}s-c            {C['W']}Search Commands only
      {C['G']}s-n            {C['W']}Search Notes only

    {C['Y']}{C['UL']}COMMANDS:{C['RST']}
      {C['G']}c-a [cmd]      {C['W']}Add new command
      {C['G']}-c             {C['W']}List all commands
      {C['G']}e-c [id]       {C['W']}Edit command
      {C['G']}d-c [id]       {C['W']}Delete command

    {C['Y']}{C['UL']}NOTES:{C['RST']}
      {C['G']}n-a [title]    {C['W']}Add new note (opens editor)
      {C['G']}-n             {C['W']}List all notes
      {C['G']}e-n [id]       {C['W']}Edit note title
      {C['G']}d-n [id]       {C['W']}Delete note

    {C['Y']}{C['UL']}SYSTEM:{C['RST']}
      {C['G']}-i             {C['W']}Show System Info & Stats
      {C['G']}-p [min]       {C['W']}Pomodoro Timer (Default 25m)
      {C['G']}-h             {C['W']}Show this help page
    """
    print(h)

def main():
    if len(sys.argv) < 2: smart_fzf("all"); return
    cmd = sys.argv[1]

    if cmd == "-h": show_help()
    elif cmd == "-i": show_info()
    elif cmd == "s": smart_fzf("all")
    elif cmd == "s-c": smart_fzf("c")
    elif cmd == "s-n": smart_fzf("n")
    elif cmd == "-p": 
        try:
            m_in = int(sys.argv[2]) if len(sys.argv) > 2 else 25
            print(f"\n{C['M']}⏳ Focus: {m_in}m{C['RST']}")
            for i in range(m_in * 60, 0, -1):
                m, s = divmod(i, 60)
                print(f"\r {C['Y']}Remaining: {C['RST']}{m:02d}:{s:02d}", end="")
                time.sleep(1)
            print(f"\n\n{C['G']}🎉 Done!{C['RST']}\a")
        except: pass
    elif cmd == "-c":
        for r in db.get_all_commands(): print(f" {C['Y']}{r['cmd_number']:<3} {C['G']}{str(r['alias']):<10} {C['W']}{r['command']}")
    elif cmd == "c-a":
        f_cmd = " ".join(sys.argv[2:])
        if not f_cmd: return
        sug = (sys.argv[2][0] + sys.argv[2][-1]).lower() if len(sys.argv[2]) > 1 else sys.argv[2][0]
        al = input(f" {C['Y']}Alias (Default '{sug}'): {C['RST']}").strip() or sug
        db.add_command(f_cmd, alias=al); print("✅ Saved.")
    elif cmd == "-n":
        for n in db.get_all_notes(): print(f" {C['Y']}{n['note_id']:<3} {C['M']}📄 {n['title']} {C['GR']}({n['created_at']})")
    elif cmd == "n-a":
        t = " ".join(sys.argv[2:]) or "Untitled"
        with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tf:
            subprocess.call([os.environ.get('EDITOR', 'nano'), tf.name])
            with open(tf.name, 'r') as f: content = f.read()
        if content.strip(): db.add_note(t, content); print("✅ Saved.")
    elif cmd == "e-c" and len(sys.argv) > 2:
        db.update_command(sys.argv[2], input("New Cmd: "), input("New Alias: ")); print("✅")
    elif cmd == "e-n" and len(sys.argv) > 2:
        res = db.get_note(sys.argv[2])
        if res: db.update_note(sys.argv[2], new_title=input(f"New Title: ") or res['title']); print("✅")
    elif cmd == "d-c" and len(sys.argv) > 2:
        if db.delete_cmd(sys.argv[2]): print("🗑️ Deleted.")
    elif cmd == "d-n" and len(sys.argv) > 2:
        if db.delete_note(sys.argv[2]): print("🗑️ Deleted.")
    else:
        for r in db.get_all_commands():
            if str(r['cmd_number']) == cmd or r['alias'] == cmd:
                subprocess.run(r['command'], shell=True); return
        print(f"❌ Error. Use 'nr -h' for help.")

if __name__ == "__main__":
    main()
