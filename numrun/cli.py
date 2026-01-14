import sys, subprocess, os, platform, tempfile, time

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
{C['C']}/_/ |_/\__,_/_/ /_/ /_/{C['B']}_/ |_|\__,_/_/ /_/ {C['GR']}v0.9.0{C['RST']}"""
    print(logo)
    w = 58
    print(f"\n {C['W']}╭─ {C['G']}PRIMARY COMMANDS{C['W']} {'─'*(w-20)}╮")
    print(f" │ {C['G']}nr{C['W']:<14} {C['GR']}•{C['W']} Search & Run (FZF Mode)          │")
    print(f" │ {C['G']}nr save <cmd>{C['W']:<5} {C['GR']}•{C['W']} Add (use -g <name> for group)     │")
    print(f" │ {C['G']}nr list{C['W']:<10} {C['GR']}•{C['W']} View all saved commands            │")
    print(f" ╰{'─'*w}╯")
    
    print(f"\n {C['W']}╭─ {C['B']}BATCH & GROUPS{C['W']} {'─'*(w-18)}╮")
    print(f" │ {C['B']}nr run-group <N>{C['W']:<4} {C['GR']}•{C['W']} Execute all commands in group <N>  │")
    print(f" │ {C['B']}nr del <id>{C['W']:<9} {C['GR']}•{C['W']} Remove command by ID               │")
    print(f" ╰{'─'*w}╯")

    print(f"\n {C['W']}╭─ {C['M']}NOTEBOOK SYSTEM{C['W']} {'─'*(w-19)}╮")
    print(f" │ {C['M']}nr note add{C['W']:<8} {C['GR']}•{C['W']} Write and save a text note         │")
    print(f" │ {C['M']}nr note ls{C['W']:<9} {C['GR']}•{C['W']} Browse your notes                  │")
    print(f" ╰{'─'*w}╯{C['RST']}")

def show_list():
    rows = db.get_all_commands()
    if not rows:
        print(f"\n {C['R']}⚠ Database empty.{C['RST']}"); return

    print(f"\n {C['B']}{C['BOLD']}📋 COMMAND INVENTORY{C['RST']}")
    top = f" {C['C']}╭{'─'*5}┬{'─'*12}┬{'─'*22}┬{'─'*12}┬{'─'*7}╮{C['RST']}"
    sep = f" {C['C']}├{'─'*5}┼{'─'*12}┼{'─'*22}┼{'─'*12}┼{'─'*7}┤{C['RST']}"
    bot = f" {C['C']}╰{'─'*5}┴{'─'*12}┴{'─'*22}┴{'─'*12}┴{'─'*7}╯{C['RST']}"
    
    print(top)
    print(f" {C['C']}│{C['W']} {'ID':<3} {C['C']}│{C['W']} {'ALIAS':<10} {C['C']}│{C['W']} {'COMMAND':<20} {C['C']}│{C['W']} {'GROUP':<10} {C['C']}│{C['W']} {'RUNS':<5} {C['C']}│")
    print(sep)
    for r in rows:
        # r[0]:id, r[1]:cmd, r[2]:grp, r[3]:runs, r[5]:alias
        alias = (r[5][:10]) if r[5] else "---"
        cmd = (r[1][:17] + "..") if len(r[1]) > 17 else r[1]
        grp = (r[2][:10])
        print(f" {C['C']}│{C['W']} {r[0]:<3} {C['C']}│{C['Y']} {alias:<10} {C['C']}│{C['W']} {cmd:<20} {C['C']}│{C['M']} {grp:<10} {C['C']}│{C['G']} {r[3]:<5} {C['C']}│")
    print(bot)

def run_batch(group_name):
    commands = db.get_by_group(group_name)
    if not commands:
        print(f" {C['R']}❌ No commands in group: {group_name}{C['RST']}"); return

    print(f"\n {C['B']}⚡ Executing Group: {C['W']}{group_name}{C['RST']}")
    draw_line = f" {C['GR']}{'─'*45}{C['RST']}"
    print(draw_line)
    
    for i, (cmd, cid) in enumerate(commands, 1):
        print(f" {C['C']}[{i}/{len(commands)}]{C['RST']} {C['W']}Running:{C['RST']} {cmd[:35]}...")
        res = subprocess.run(cmd, shell=True)
        if res.returncode == 0:
            db.increment_usage(cid)
            print(f" {C['G']}╰─ Success{C['RST']}")
        else:
            print(f" {C['R']}╰─ Failed{C['RST']}")
            if input(f" {C['Y']}Continue? (y/N): ").lower() != 'y': break
    print(draw_line)

def main():
    if len(sys.argv) < 2:
        try:
            cmds = [f"[CMD] {r[0]} | {r[5] or '-'} | {r[1]}" for r in db.get_all_commands()]
            notes = [f"[NOTE] {r[0]} | {r[1]}" for r in db.get_all_notes()]
            combined = "\n".join(cmds + notes)
            fzf = subprocess.Popen(['fzf', '--ansi', '--reverse', '--header', 'Search'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            stdout, _ = fzf.communicate(input=combined.encode())
            if stdout:
                line = stdout.decode()
                val = line.split("|")[0].strip()
                if "[CMD]" in line:
                    res = db.get_by_id_or_alias(val.replace("[CMD]", "").strip())
                    subprocess.run(res[0], shell=True)
                    db.increment_usage(res[1])
                else:
                    # View Note Logic
                    pass
        except: pass
        return

    cmd = sys.argv[1]
    if cmd in ["-h", "--help"]: get_pro_help()
    elif cmd == "list": show_list()
    elif cmd == "run-group":
        if len(sys.argv) > 2: run_batch(sys.argv[2])
    elif cmd == "save":
        group = 'general'
        parts = sys.argv[2:]
        if "-g" in parts:
            idx = parts.index("-g")
            group = parts[idx+1]
            parts = parts[:idx] + parts[idx+2:]
        full_cmd = " ".join(parts)
        if full_cmd:
            db.add_command(full_cmd, group=group)
            print(f" {C['G']}✅ Saved to [{group}]{C['RST']}")
    elif cmd == "note":
        # Note logic (Add/Ls/View كما في السابق)
        pass
    elif cmd == "del":
        if len(sys.argv) > 2: db.delete_cmd(sys.argv[2]); print("🗑️ Deleted.")

if __name__ == "__main__": main()
