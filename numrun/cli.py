import sys, subprocess, os, tempfile, json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from database import Database
except ImportError:
    from numrun.database import Database

db = Database()

C = {
    "B": "\033[1;34m", "C": "\033[1;36m", "G": "\033[1;32m", "R": "\033[1;31m",
    "Y": "\033[1;33m", "M": "\033[1;35m", "W": "\033[1;37m", "GR": "\033[90m",
    "RST": "\033[0m"
}

def get_pro_help():
    print(f"\n{C['C']}--- NUMRUN v0.6.0 ---{C['RST']}")
    print(f" {C['Y']}Operations:{C['RST']}")
    print(f"  {C['G']}nr -c{C['W']:<12} {C['GR']}•{C['W']} List Commands")
    print(f"  {C['G']}nr c-a <cmd>{C['W']:<8} {C['GR']}•{C['W']} Add New Command")
    print(f"  {C['G']}nr -n{C['W']:<12} {C['GR']}•{C['W']} List Notes")
    print(f"  {C['G']}nr n-a <title>{C['W']:<6} {C['GR']}•{C['W']} Add New Note")
    print(f" {C['Y']}Management:{C['RST']}")
    print(f"  {C['G']}e-c / e-n{C['W']:<10} {C['GR']}•{C['W']} Edit (Cmd / Note)")
    print(f"  {C['G']}d-c / d-n{C['W']:<10} {C['GR']}•{C['W']} Delete (Cmd / Note)")
    print(f"  {C['B']}s / s-c / s-n{C['W']:<10} {C['GR']}•{C['W']} FZF Search")

def smart_fzf(mode="all"):
    items = []
    if mode in ["all", "commands"]:
        for r in db.get_all_commands():
            items.append(f"[CMD] {r['cmd_number']} | {r['alias'] or '---'} | {r['command']}")
    if mode in ["all", "notes"]:
        for n in db.get_all_notes():
            items.append(f"[NOTE] {n['note_id']} | {n['title']}")
    
    if not items: return

    try:
        p = subprocess.Popen(['fzf', '--ansi', '--reverse'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        out, _ = p.communicate(input="\n".join(items))
        if out:
            if "[CMD]" in out:
                subprocess.run(out.split('|')[2].strip(), shell=True)
            elif "[NOTE]" in out:
                note_id = out.split('|')[0].replace("[NOTE]", "").strip()
                res = db.get_note(note_id)
                if res: print(f"\n{C['M']}{res['title']}{C['RST']}\n{res['content']}")
    except: print("fzf required.")

def main():
    if len(sys.argv) < 2: smart_fzf("commands"); return
    cmd = sys.argv[1]

    # --- Commands Section ---
    if cmd == "-c":
        for r in db.get_all_commands():
            print(f" {C['Y']}{r['cmd_number']:<3} {C['C']}│ {C['G']}{str(r['alias']):<10} {C['C']}│ {C['W']}{r['command']}")

    elif cmd == "c-a":
        full_cmd = " ".join(sys.argv[2:])
        if not full_cmd: return
        sugg = (sys.argv[2][0] + sys.argv[2][-1]).lower() if len(sys.argv[2]) > 1 else sys.argv[2][0]
        while True:
            alias = input(f" {C['Y']}Alias (Enter for '{sugg}'): {C['RST']}").strip() or sugg
            if alias.startswith("-"): print(f" {C['R']}⚠ Cannot start with '-'{C['RST']}")
            else: break
        db.add_command(full_cmd, alias=alias); print("✅ Command Saved.")

    # --- Notes Section ---
    elif cmd == "-n":
        for n in db.get_all_notes(): print(f" {n['note_id']} 📄 {n['title']}")

    elif cmd == "n-a":
        title = " ".join(sys.argv[2:]) or "Untitled"
        with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tf:
            subprocess.call([os.environ.get('EDITOR', 'nano'), tf.name])
            with open(tf.name, 'r') as f: content = f.read()
        if content.strip(): db.add_note(title, content); print("✅ Note Saved.")

    # --- Edit & Delete ---
    elif cmd == "e-c" and len(sys.argv) > 2:
        cid = sys.argv[2]
        new_c = input(f" {C['C']}New Command: {C['RST']}")
        new_a = input(f" {C['C']}New Alias: {C['RST']}")
        db.update_command(cid, new_cmd=new_c if new_c else None, new_alias=new_a if new_a else None)
        print("✅ Updated.")

    elif cmd == "e-n" and len(sys.argv) > 2:
        nid = sys.argv[2]
        res = db.get_note(nid)
        if not res: return
        new_t = input(f" {C['C']}New Title: {C['RST']}")
        if input(f" {C['Y']}Edit Content? (y/N): {C['RST']}").lower() == 'y':
            with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False, mode='w+') as tf:
                tf.write(res['content']); tf.flush()
                subprocess.call([os.environ.get('EDITOR', 'nano'), tf.name])
                with open(tf.name, 'r') as f: new_content = f.read()
        else: new_content = None
        db.update_note(nid, new_title=new_t if new_t else None, new_content=new_content)
        print("✅ Updated.")

    elif cmd == "d-c" and len(sys.argv) > 2:
        if db.delete_cmd(sys.argv[2]): print("🗑️ Deleted.")

    elif cmd == "d-n" and len(sys.argv) > 2:
        if db.delete_note(sys.argv[2]): print("🗑️ Deleted.")

    elif cmd == "d-all":
        if input(f" {C['R']}WIPE EVERYTHING? (CONFIRM): {C['RST']}") == "CONFIRM":
            db.wipe_everything(); print("💥 Done.")

    elif cmd in ["s", "s-c", "s-n"]: smart_fzf(cmd.replace("s-", "") if "-" in cmd else "all")
    elif cmd == "-h": get_pro_help()
    
    else:
        for r in db.get_all_commands():
            if str(r['cmd_number']) == cmd or r['alias'] == cmd:
                subprocess.run(r['command'], shell=True); return
        print(f"❌ Unknown: {cmd}")

if __name__ == "__main__":
    main()
