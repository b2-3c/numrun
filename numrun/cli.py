import sys, subprocess, os, tempfile, time, platform

# لضمان عمل الاستيراد بشكل سليم في أي بيئة
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import Database

db = Database()
VERSION = "0.9.2"

C = {
    "B": "\033[1;34m", "C": "\033[1;36m", "G": "\033[1;32m", "R": "\033[1;31m",
    "Y": "\033[1;33m", "M": "\033[1;35m", "W": "\033[1;37m", "GR": "\033[90m",
    "RST": "\033[0m"
}

def get_uptime():
    try:
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.readline().split()[0])
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    except: return "N/A"

def show_info():
    user = os.getenv("USER") or "User"
    hostname = platform.node()
    distro = "Linux"
    if os.path.exists("/etc/os-release"):
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="): distro = line.split("=")[1].strip('" \n')

    cmd_count, note_count = db.get_stats()
    
    # 1. قائمة المعلومات (الجهة اليمنى)
    info_layout = [
        f"{C['C']}{user}{C['W']}@{C['C']}{hostname}",
        f"{C['GR']}{'-' * (len(user) + len(hostname) + 1)}",
        f"{C['Y']}nr      {C['W']}: {C['G']}{VERSION}",
        f"{C['Y']}OS      {C['W']}: {C['G']}{distro}",
        f"{C['Y']}Kernel  {C['W']}: {C['G']}{platform.release()}",
        f"{C['Y']}Uptime  {C['W']}: {C['G']}{get_uptime()}",
        f"{C['Y']}Storage {C['W']}: {C['M']}{cmd_count} Cmds / {note_count} Notes"
    ]

    # 2. الشعار (الجهة اليسرى) مع الإزاحة المطلوبة
    logo = [
        "", # سطر فارغ لإنزال الشعار لأسفل قليلاً
        f"     {C['Y']}▄▀ ▄▀",
        f"     {C['Y']} ▀  ▀",
        f"    {C['Y']} █▀▀▀▀▀█▄",
        f"    {C['Y']} █░░░░░█ █",
        f"    {C['Y']} ▀▄▄▄▄▄▀▀"
    ]

    print("")
    # عرض الشعار والمعلومات جنباً إلى جنب بذكاء
    max_lines = max(len(info_layout), len(logo))
    for i in range(max_lines):
        # جزء الشعار
        l_part = logo[i] if i < len(logo) else ""
        # جزء المعلومات
        r_part = info_layout[i] if i < len(info_layout) else ""
        
        # تنظيف الألوان لحساب طول المسافات الحقيقي
        clean_l = l_part.replace(C['Y'], "").replace(C['RST'], "")
        padding = " " * (18 - len(clean_l)) # 18 هو عرض منطقة الشعار الثابتة
        
        print(f"{l_part}{padding}{r_part}")
    print("")

def start_pomodoro(minutes=25):
    print(f"\n{C['M']}⏳ Focus Mode: {minutes}m{C['RST']}")
    try:
        for i in range(minutes * 60, 0, -1):
            m, s = divmod(i, 60)
            print(f"\r {C['Y']}Time Remaining: {C['RST']}{m:02d}:{s:02d}", end="")
            time.sleep(1)
        print(f"\n\n{C['G']}🎉 Pomodoro Finished!{C['RST']}\a")
    except KeyboardInterrupt:
        print(f"\n{C['R']}Stopped.{C['RST']}")

def get_pro_help():
    print(f"\n{C['C']}--- NUMRUN v{VERSION} ---{C['RST']}")
    print(f" {C['Y']}Actions:{C['RST']}")
    print(f"  {C['G']}nr -c / c-a{C['W']:<10} {C['GR']}•{C['W']} List / Add Commands")
    print(f"  {C['G']}nr -n / n-a{C['W']:<10} {C['GR']}•{C['W']} List / Add Notes")
    print(f" {C['Y']}Edit/Delete:{C['RST']}")
    print(f"  {C['G']}e-c / d-c{C['W']:<10} {C['GR']}•{C['W']} Edit / Delete Cmd")
    print(f"  {C['G']}e-n / d-n{C['W']:<10} {C['GR']}•{C['W']} Edit / Delete Note")
    print(f" {C['Y']}Tools:{C['RST']}")
    print(f"  {C['M']}-i{C['W']:<14} {C['GR']}•{C['W']} Pro System Info")
    print(f"  {C['M']}-p [min]{C['W']:<10} {C['GR']}•{C['W']} Pomodoro Timer")
    print(f"  {C['B']}s / s-c / s-n{C['W']:<10} {C['GR']}•{C['W']} FZF Search")

def smart_fzf(mode="all"):
    items = []
    if mode in ["all", "commands"]:
        for r in db.get_all_commands(): items.append(f"[CMD] {r['cmd_number']} | {r['alias'] or '---'} | {r['command']}")
    if mode in ["all", "notes"]:
        for n in db.get_all_notes(): items.append(f"[NOTE] {n['note_id']} | {n['title']}")
    
    if not items: return
    try:
        p = subprocess.Popen(['fzf', '--ansi', '--reverse'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        out, _ = p.communicate(input="\n".join(items))
        if out:
            if "[CMD]" in out: subprocess.run(out.split('|')[2].strip(), shell=True)
            elif "[NOTE]" in out:
                res = db.get_note(out.split('|')[0].replace("[NOTE]", "").strip())
                if res: print(f"\n{C['M']}{res['title']}{C['RST']}\n{res['content']}")
    except: print("fzf required.")

def main():
    if len(sys.argv) < 2: smart_fzf("commands"); return
    cmd = sys.argv[1]

    if cmd == "-i": show_info()
    elif cmd == "-p": start_pomodoro(int(sys.argv[2]) if len(sys.argv) > 2 else 25)
    elif cmd == "-c":
        for r in db.get_all_commands(): print(f" {C['Y']}{r['cmd_number']:<3} {C['G']}{str(r['alias']):<10} {C['W']}{r['command']}")
    elif cmd == "c-a":
        full_cmd = " ".join(sys.argv[2:])
        if not full_cmd: return
        sugg = (sys.argv[2][0] + sys.argv[2][-1]).lower() if len(sys.argv[2]) > 1 else sys.argv[2][0]
        alias = input(f" {C['Y']}Alias (Enter for '{sugg}'): {C['RST']}").strip() or sugg
        db.add_command(full_cmd, alias=alias); print("✅ Command Saved.")
    elif cmd == "-n":
        for n in db.get_all_notes(): print(f" {C['Y']}{n['note_id']:<3} {C['M']}📄 {n['title']}")
    elif cmd == "n-a":
        title = " ".join(sys.argv[2:]) or "Untitled"
        with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tf:
            subprocess.call([os.environ.get('EDITOR', 'nano'), tf.name])
            with open(tf.name, 'r') as f: content = f.read()
        if content.strip(): db.add_note(title, content); print("✅ Note Saved.")
    elif cmd == "e-c" and len(sys.argv) > 2:
        cid = sys.argv[2]
        new_c = input(f" {C['C']}New Cmd: {C['RST']}")
        new_a = input(f" {C['C']}New Alias: {C['RST']}")
        db.update_command(cid, new_cmd=new_c or None, new_alias=new_a or None); print("✅ Updated.")
    elif cmd == "e-n" and len(sys.argv) > 2:
        nid = sys.argv[2]
        res = db.get_note(nid)
        if not res: return
        new_t = input(f" {C['C']}New Title: {C['RST']}")
        if input(f" {C['Y']}Edit Body? (y/N): {C['RST']}").lower() == 'y':
            with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False, mode='w+') as tf:
                tf.write(res['content']); tf.flush()
                subprocess.call([os.environ.get('EDITOR', 'nano'), tf.name])
                with open(tf.name, 'r') as f: new_content = f.read()
        else: new_content = None
        db.update_note(nid, new_title=new_t or None, new_content=new_content); print("✅ Updated.")
    elif cmd == "d-c" and len(sys.argv) > 2:
        if db.delete_cmd(sys.argv[2]): print("🗑️ Deleted.")
    elif cmd == "d-n" and len(sys.argv) > 2:
        if db.delete_note(sys.argv[2]): print("🗑️ Deleted.")
    elif cmd == "d-all":
        if input(f" {C['R']}CONFIRM WIPE ALL? (y/N): {C['RST']}").lower() == 'y': db.wipe_everything(); print("💥 Database Cleared.")
    elif cmd in ["s", "s-c", "s-n"]: smart_fzf(cmd.replace("s-", "") if "-" in cmd else "all")
    elif cmd == "-h": get_pro_help()
    else:
        for r in db.get_all_commands():
            if str(r['cmd_number']) == cmd or r['alias'] == cmd:
                subprocess.run(r['command'], shell=True); return
        print(f"❌ Unknown command: {cmd}")

if __name__ == "__main__":
    main()
