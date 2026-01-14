import sys, subprocess, os, platform, json, tempfile

try: 
    from numrun.database import Database
except ImportError: 
    from database import Database

db = Database()
C = {
    "BLUE": "\033[1;34m", "CYAN": "\033[1;36m", "GREEN": "\033[1;32m", 
    "RED": "\033[1;31m", "YELLOW": "\033[1;33m", "MAGENTA": "\033[1;35m", 
    "RESET": "\033[0m", "BOLD": "\033[1m", "GRAY": "\033[90m"
}

def get_help():
    total = len(db.get_all())
    logo = fr"""
{C['BLUE']}    _   __              {C['CYAN']}____ 
{C['BLUE']}   / | / /_  ______ ___ {C['CYAN']}/ __ \__  ______ 
{C['BLUE']}  /  |/ / / / / __ `__ \{C['CYAN']}/ /_/ / / / / __ \\
{C['BLUE']} / /|  / /_/ / / / / / / {C['CYAN']}_  __/ /_/ / / / /
{C['BLUE']}/_/ |_/\__,_/_/ /_/ /_/{C['CYAN']}_/ |_|\__,_/_/ /_/ """
    
    dashboard = f"""
{C['CYAN']}┏━━━━ {C['BOLD']}PRO DASHBOARD{C['RESET']}{C['CYAN']} ━━━━━━━━━━━━━━━━━━━━━━┓{C['RESET']}
{C['CYAN']}┃{C['RESET']} {C['BLUE']}Commands{C['RESET']}: {total:<5} | {C['BLUE']}FZF{C['RESET']}: Active | {C['BLUE']}Ver{C['RESET']}: 0.5.0   {C['CYAN']}┃{C['RESET']}
{C['CYAN']}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{C['RESET']}

{C['YELLOW']}MODES:{C['RESET']}
  {C['GREEN']}nr{C['RESET']}              {C['GRAY']}» Interactive Search (FZF){C['RESET']}
  {C['GREEN']}nr <id|alias>{C['RESET']}   {C['GRAY']}» Run. Add {C['BOLD']}--copy{C['RESET']}{C['GRAY']} to only copy.{C['RESET']}
  {C['GREEN']}nr save <cmd>{C['RESET']}    {C['GRAY']}» Save (use {C['BOLD']}-g{C['RESET']}{C['GRAY']} for group){C['RESET']}
  {C['GREEN']}nr edit <id>{C['RESET']}     {C['GRAY']}» Modify cmd/shortcut in editor{C['RESET']}
  {C['GREEN']}nr list [group]{C['RESET']}  {C['GRAY']}» Show Advanced Table{C['RESET']}
  {C['GREEN']}nr export/import{C['RESET']} {C['GRAY']}» JSON Backup{C['RESET']}
"""
    print(logo + dashboard)

def copy_to_clipboard(text):
    try:
        cmd = ['xclip', '-selection', 'clipboard'] if platform.system() == "Linux" else ['pbcopy']
        subprocess.run(cmd, input=text.encode(), check=True)
        print(f"📋 {C['GREEN']}Copied to clipboard!{C['RESET']}")
    except: 
        print(f"{C['RED']}❌ Error: Install 'xclip' or 'pbcopy'.{C['RESET']}")

def interactive_search():
    rows = db.get_all()
    if not rows: return print("Your database is empty.")
    # ID | Alias | Command
    input_str = "\n".join([f"{r[0]} | {r[5] or '-'} | {r[1]}" for r in rows])
    try:
        fzf = subprocess.Popen(['fzf', '--ansi', '--header', 'Search Commands'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, _ = fzf.communicate(input=input_str.encode())
        if stdout:
            selected_id = stdout.decode().split("|")[0].strip()
            execute_logic(selected_id, [])
    except FileNotFoundError: 
        print(f"{C['YELLOW']}💡 Hint: Install 'fzf' for interactive mode.{C['RESET']}")

def execute_logic(identifier, extra_args):
    copy_mode = "--copy" in extra_args
    if copy_mode: extra_args.remove("--copy")
    
    res = db.get_by_id_or_alias(identifier)
    if not res: return False
    
    cmd, cid, alias = res
    for i, arg in enumerate(extra_args, 1): 
        cmd = cmd.replace(f"${i}", arg)
    
    if copy_mode: 
        copy_to_clipboard(cmd)
        return True

    if any(d in cmd.lower() for d in ["rm ", "dd "]):
        if input(f"{C['RED']}⚠️ GUARD:{C['RESET']} {cmd}\nExecute? (y/N): ").lower() != 'y': return True

    print(f"{C['BLUE']}🚀 Running:{C['RESET']} {cmd}")
    db.increment_usage(cid)
    subprocess.run(cmd, shell=True)
    return True

def main():
    if len(sys.argv) < 2: 
        interactive_search()
        return
        
    arg1 = sys.argv[1]
    if arg1 in ["-h", "--help"]: 
        get_help()
        return

    if execute_logic(arg1, sys.argv[2:]): 
        return

    if arg1 == "save":
        group = 'general'
        if "-g" in sys.argv:
            idx = sys.argv.index("-g")
            group = sys.argv[idx+1]
            cmd_parts = sys.argv[2:idx] + sys.argv[idx+2:]
        else: 
            cmd_parts = sys.argv[2:]
        
        full_cmd = " ".join(cmd_parts)
        sug = (cmd_parts[0][0] + cmd_parts[0][-1]).lower() if cmd_parts else "nr"
        
        alias = None
        if not db.is_alias_exists(sug) and sug not in ["save", "list", "del", "edit"]:
            choice = input(f"💡 Suggestion: '{C['YELLOW']}{sug}{C['RESET']}' shortcut? (y/n/custom): ").lower()
            if choice == 'y': alias = sug
            elif choice != 'n' and choice.strip(): alias = choice
        
        num = db.add_command(full_cmd, alias, group)
        print(f"✅ {C['GREEN']}Saved as #{num} in [{group}]{C['RESET']}")

    elif arg1 == "list":
        group = sys.argv[2] if len(sys.argv) > 2 else None
        rows = db.get_all(group)
        header = f"{C['BLUE']}{'ID':<4} | {'ALIAS':<10} | {'COMMAND':<35} | {'GROUP':<10} | {'USES'}{C['RESET']}"
        sep = f"{C['GRAY']}{'-'*4}-+-{'-'*10}-+-{'-'*35}-+-{'-'*10}-+-{'-'*5}{C['RESET']}"
        print(f"\n📋 {C['CYAN']}Inventory:{C['RESET']}\n{header}\n{sep}")
        for r in rows:
            # r[0]:id, r[1]:cmd, r[2]:grp, r[3]:uses, r[4]:last, r[5]:alias
            print(f"{r[0]:<4} | {C['YELLOW']}{str(r[5] or '-'):<10}{C['RESET']} | {r[1][:32]:<35} | {C['MAGENTA']}{r[2]:<10}{C['RESET']} | {r[3]}")

    elif arg1 == "edit":
        if len(sys.argv) < 3: return
        res = db.get_by_id_or_alias(sys.argv[2])
        if not res: return
        with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tf:
            tf.write(f"{res[0]}\n# Alias: {res[2] or ''}".encode())
            tf_path = tf.name
        subprocess.call([os.environ.get('EDITOR', 'nano'), tf_path])
        with open(tf_path, 'r') as f:
            lines = f.readlines()
            new_cmd = lines[0].strip()
            new_alias = lines[1].replace("# Alias:", "").strip() if len(lines)>1 else res[2]
        db.update_command(res[1], new_cmd, new_alias)
        os.remove(tf_path); print("📝 Updated.")

    elif arg1 == "export":
        data = [dict(zip(['id','cmd','grp','uses','last','alias'], r)) for r in db.get_all()]
        with open("numrun_backup.json", "w") as f: json.dump(data, f, indent=4)
        print("📤 Exported to numrun_backup.json")

    elif arg1 == "del":
        if len(sys.argv) > 2:
            db.delete(sys.argv[2])
            print("🗑️ Deleted.")

if __name__ == "__main__": 
    main()
