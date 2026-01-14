import sys, subprocess, os, tempfile, json

# إعداد المسارات لضمان استيراد قاعدة البيانات
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

def show_list():
    rows = db.get_all_commands()
    if not rows:
        print(f"\n {C['R']}⚠ No commands found.{C['RST']}\n")
        return
    sep = f" {C['C']}├{'─'*5}┼{'─'*12}┼{'─'*24}┼{'─'*12}┤"
    print(f"\n {C['C']}╭{'─'*5}┬{'─'*12}┬{'─'*24}┬{'─'*12}╮")
    print(f" │ {C['W']}ID  {C['C']}│ {C['W']}ALIAS      {C['C']}│ {C['W']}COMMAND                 {C['C']}│ {C['W']}GROUP      {C['C']}│")
    print(sep)
    for r in rows:
        alias = (r['alias'] or "---")[:10]
        cmd_disp = (r['command'][:21] + "..") if len(r['command']) > 21 else r['command']
        print(f" │ {C['Y']}{str(r['cmd_number']):<3} {C['C']}│ {C['G']}{alias:<10} {C['C']}│ {C['W']}{cmd_disp:<22} {C['C']}│ {C['M']}{r['group_name']:<10} {C['C']}│")
    print(f" {C['C']}╰{'─'*5}┴{'─'*12}┴{'─'*24}┴{'─'*12}╯{C['RST']}")

def run_by_id(identifier):
    all_cmds = db.get_all_commands()
    for r in all_cmds:
        if str(r['cmd_number']) == identifier or (r['alias'] and r['alias'] == identifier):
            print(f"{C['B']}🚀 Running:{C['RST']} {r['command']}")
            subprocess.run(r['command'], shell=True)
            db.increment_usage(r['cmd_number'])
            return True
    return False

def main():
    if len(sys.argv) < 2:
        return

    cmd = sys.argv[1]
    
    if cmd == "list":
        show_list()
    elif cmd == "save":
        args = sys.argv[2:]
        if not args: return
        
        group, alias = 'general', None
        if "-g" in args:
            idx = args.index("-g"); group = args[idx+1]; args = args[:idx] + args[idx+2:]
        
        command = " ".join(args)
        
        if command:
            # --- المنطق الجديد للاقتراح الذكي ---
            first_word = command.split()[0]
            # اقتراح أول حرف وآخر حرف من أول كلمة في الأمر
            suggested = (first_word[0] + first_word[-1]).lower() if len(first_word) > 1 else first_word[0].lower()
            
            print(f"\n {C['Y']}❓ Set an alias for this command?{C['RST']}")
            print(f" {C['GR']}Default suggestion: {C['BOLD']}{suggested}{C['RST']}")
            
            user_input = input(f" {C['C']}Enter alias (or press Enter for '{suggested}'): {C['RST']}").strip()
            
            # إذا ضغط Enter يستخدم المقترح، إذا كتب يستخدم المكتوب
            alias = user_input if user_input else suggested
            
            success = db.add_command(command, alias=alias, group=group)
            if success:
                print(f" {C['G']}✅ Saved as '{alias}' in group [{group}].{C['RST']}")
            else:
                # محاولة الحفظ بدون Alias إذا فشل بسبب التكرار
                db.add_command(command, alias=None, group=group)
                print(f" {C['R']}⚠ Alias '{alias}' already exists. Saved without alias.{C['RST']}")

    elif cmd == "del" and len(sys.argv) > 2:
        db.delete_cmd(sys.argv[2]); print("🗑️ Deleted.")
    
    else:
        if not run_by_id(cmd):
            print(f"{C['R']}❌ Unknown command or ID: {cmd}{C['RST']}")

if __name__ == "__main__":
    main()
