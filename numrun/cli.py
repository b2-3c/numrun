import sys, subprocess, os, tempfile, time, platform
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich import box
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import Database

db = Database()
VERSION = "2.0.0"
console = Console()

# ============================================================================
# وظائف مساعدة
# ============================================================================

def get_uptime():
    """الحصول على مدة تشغيل النظام"""
    try:
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.readline().split()[0])
            h = int(uptime_seconds // 3600)
            m = int((uptime_seconds % 3600) // 60)
            return f"{h}h {m}m"
    except: 
        return "N/A"

def get_distro():
    """الحصول على اسم توزيعة لينكس"""
    distro = "Linux"
    if os.path.exists("/etc/os-release"):
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="): 
                    distro = line.split("=")[1].strip('" \n')
    return distro

# ============================================================================
# شاشات العرض الرئيسية
# ============================================================================

def show_info():
    """عرض معلومات النظام والإحصائيات"""
    user = os.getenv("USER") or "User"
    host = platform.node()
    distro = get_distro()
    
    cmd_c, note_c, total_usage = db.get_stats()
    uptime = get_uptime()
    
    # إنشاء جدول معلومات النظام
    info_table = Table(title="System Information", box=box.ROUNDED, show_header=False, padding=(0, 2))
    
    info_table.add_row("[cyan]User[/cyan]", f"[bold green]{user}[/bold green]")
    info_table.add_row("[cyan]Host[/cyan]", f"[bold green]{host}[/bold green]")
    info_table.add_row("[cyan]OS[/cyan]", f"[bold green]{distro}[/bold green]")
    info_table.add_row("[cyan]Uptime[/cyan]", f"[bold green]{uptime}[/bold green]")
    info_table.add_row("[cyan]Tool[/cyan]", f"[bold green]numrun v{VERSION}[/bold green]")
    
    # إنشاء جدول الإحصائيات
    stats_table = Table(title="Statistics", box=box.ROUNDED, show_header=False, padding=(0, 2))
    stats_table.add_row("[magenta]Commands[/magenta]", f"[bold yellow]{cmd_c}[/bold yellow]")
    stats_table.add_row("[magenta]Notes[/magenta]", f"[bold yellow]{note_c}[/bold yellow]")
    stats_table.add_row("[magenta]Total Usage[/magenta]", f"[bold yellow]{total_usage}[/bold yellow]")
    
    # عرض الجداول جنباً إلى جنب
    console.print()
    columns = Columns([info_table, stats_table], equal=True, expand=True)
    console.print(columns)
    console.print()

def show_commands():
    """عرض جميع الأوامر المحفوظة في جدول منظم"""
    commands = db.get_all_commands()
    
    if not commands:
        console.print("[yellow]⚠️  No commands saved yet.[/yellow]")
        return
    
    table = Table(title="Saved Commands", box=box.ROUNDED, padding=(0, 1))
    table.add_column("ID", style="cyan", width=5)
    table.add_column("Alias", style="green", width=12)
    table.add_column("Command", style="white", width=50)
    table.add_column("Usage", style="magenta", width=8)
    table.add_column("Last Used", style="yellow", width=16)
    
    for cmd in commands:
        last_used = cmd['last_used'] or "Never"
        table.add_row(
            str(cmd['cmd_number']),
            cmd['alias'] or "---",
            cmd['command'][:47] + "..." if len(cmd['command']) > 50 else cmd['command'],
            str(cmd['usage_count']),
            last_used
        )
    
    console.print()
    console.print(table)
    console.print()

def show_notes():
    """عرض جميع الملاحظات المحفوظة في جدول منظم"""
    notes = db.get_all_notes()
    
    if not notes:
        console.print("[yellow]⚠️  No notes saved yet.[/yellow]")
        return
    
    table = Table(title="Saved Notes", box=box.ROUNDED, padding=(0, 1))
    table.add_column("ID", style="cyan", width=5)
    table.add_column("Title", style="magenta", width=30)
    table.add_column("Created", style="yellow", width=16)
    table.add_column("Updated", style="yellow", width=16)
    
    for note in notes:
        updated = note['updated_at'] or note['created_at']
        table.add_row(
            str(note['note_id']),
            note['title'][:27] + "..." if len(note['title']) > 30 else note['title'],
            note['created_at'],
            updated
        )
    
    console.print()
    console.print(table)
    console.print()

def smart_fzf(mode="all"):
    """البحث التفاعلي باستخدام fzf"""
    items = []
    
    if mode in ["all", "c"]:
        for r in db.get_all_commands(): 
            items.append(f"[CMD] {r['cmd_number']} | {r['alias'] or '---'} | {r['command']}")
    
    if mode in ["all", "n"]:
        for n in db.get_all_notes(): 
            items.append(f"[NOTE] {n['note_id']} | {n['title']}")
    
    if not items:
        console.print("[yellow]⚠️  No items to search.[/yellow]")
        return
    
    try:
        hdr = "ALL" if mode == "all" else ("COMMANDS" if mode == "c" else "NOTES")
        p = subprocess.Popen(
            ['fzf', '--ansi', '--reverse', '--header', f'| SEARCH: {hdr} |'], 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            text=True
        )
        out, _ = p.communicate(input="\n".join(items))
        
        if out:
            if "[CMD]" in out:
                cmd_exec = out.split('|')[2].strip()
                console.print(f"[yellow]▶ Running:[/yellow] [bold]{cmd_exec}[/bold]")
                db.increment_usage(out.split('|')[0].replace("[CMD]", "").strip())
                subprocess.run(cmd_exec, shell=True)
            elif "[NOTE]" in out:
                nid = out.split('|')[0].replace("[NOTE]", "").strip()
                res = db.get_note(nid)
                if res:
                    console.print()
                    console.print(Panel(
                        res['content'],
                        title=f"[magenta]{res['title']}[/magenta]",
                        border_style="magenta"
                    ))
                    console.print()
    except FileNotFoundError:
        console.print("[red]❌ Error: fzf is not installed. Please install fzf to use search.[/red]")
    except Exception as e:
        console.print(f"[red]❌ Search error: {e}[/red]")

def show_help():
    """عرض شاشة المساعدة"""
    help_text = f"""
[cyan bold]NUMRUN v{VERSION}[/cyan bold] - Command & Note Manager
[dim]A powerful CLI tool for managing commands and notes efficiently[/dim]

[yellow bold underline]USAGE:[/yellow bold underline]
  [green]nr[/green] [cyan][id/alias][/cyan]        Run stored command by ID or Alias
  [green]nr[/green] [cyan]s[/cyan]                 Global search (Cmds + Notes) using fzf

[yellow bold underline]SEARCH:[/yellow bold underline]
  [green]s-c[/green]                  Search Commands only
  [green]s-n[/green]                  Search Notes only

[yellow bold underline]COMMANDS:[/yellow bold underline]
  [green]c-a[/green] [cyan][cmd][/cyan]            Add new command
  [green]-c[/green]                   List all commands
  [green]e-c[/green] [cyan][id][/cyan]            Edit command
  [green]d-c[/green] [cyan][id][/cyan]            Delete command

[yellow bold underline]NOTES:[/yellow bold underline]
  [green]n-a[/green] [cyan][title][/cyan]         Add new note (opens editor)
  [green]-n[/green]                   List all notes
  [green]e-n[/green] [cyan][id][/cyan]            Edit note title
  [green]e-n-c[/green] [cyan][id][/cyan]          Edit note content
  [green]d-n[/green] [cyan][id][/cyan]            Delete note

[yellow bold underline]SYSTEM:[/yellow bold underline]
  [green]-i[/green]                   Show System Info & Stats
  [green]-p[/green] [cyan][min][/cyan]            Pomodoro Timer (Default 25m)
  [green]-h[/green]                   Show this help page
"""
    console.print(help_text)

# ============================================================================
# وظائف إدارة الأوامر
# ============================================================================

def add_command():
    """إضافة أمر جديد"""
    if len(sys.argv) < 3:
        console.print("[red]❌ Error: Please provide a command.[/red]")
        console.print("[dim]Usage: nr c-a [command][/dim]")
        return
    
    f_cmd = " ".join(sys.argv[2:])
    sug = (sys.argv[2][0] + sys.argv[2][-1]).lower() if len(sys.argv[2]) > 1 else sys.argv[2][0]
    
    console.print(f"[cyan]Command:[/cyan] {f_cmd}")
    al = console.input(f"[yellow]Alias (Default '{sug}'):[/yellow] ").strip() or sug
    
    if db.add_command(f_cmd, alias=al):
        console.print("[green]✅ Command saved successfully![/green]")
    else:
        console.print("[red]❌ Error: Alias already exists.[/red]")

def edit_command():
    """تعديل أمر موجود"""
    if len(sys.argv) < 3:
        console.print("[red]❌ Error: Please provide a command ID.[/red]")
        return
    
    cmd_id = sys.argv[2]
    cmd = db.get_command_by_id_or_alias(cmd_id)
    
    if not cmd:
        console.print("[red]❌ Error: Command not found.[/red]")
        return
    
    console.print(f"[cyan]Current Command:[/cyan] {cmd['command']}")
    console.print(f"[cyan]Current Alias:[/cyan] {cmd['alias'] or '---'}")
    
    new_cmd = console.input("[yellow]New Command (leave blank to keep):[/yellow] ").strip() or cmd['command']
    new_alias = console.input("[yellow]New Alias (leave blank to keep):[/yellow] ").strip() or cmd['alias']
    
    if db.update_command(cmd_id, new_cmd, new_alias):
        console.print("[green]✅ Command updated successfully![/green]")
    else:
        console.print("[red]❌ Error: Failed to update command.[/red]")

def delete_command():
    """حذف أمر"""
    if len(sys.argv) < 3:
        console.print("[red]❌ Error: Please provide a command ID.[/red]")
        return
    
    if db.delete_cmd(sys.argv[2]):
        console.print("[green]🗑️  Command deleted successfully![/green]")
    else:
        console.print("[red]❌ Error: Command not found.[/red]")

# ============================================================================
# وظائف إدارة الملاحظات
# ============================================================================

def add_note():
    """إضافة ملاحظة جديدة"""
    title = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Untitled"
    
    console.print(f"[cyan]Title:[/cyan] {title}")
    console.print("[yellow]Opening editor... (save and exit to continue)[/yellow]")
    
    with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tf:
        subprocess.call([os.environ.get('EDITOR', 'nano'), tf.name])
        with open(tf.name, 'r') as f: 
            content = f.read()
        os.unlink(tf.name)
    
    if content.strip():
        db.add_note(title, content)
        console.print("[green]✅ Note saved successfully![/green]")
    else:
        console.print("[yellow]⚠️  Note is empty. Not saved.[/yellow]")

def edit_note_title():
    """تعديل عنوان الملاحظة"""
    if len(sys.argv) < 3:
        console.print("[red]❌ Error: Please provide a note ID.[/red]")
        return
    
    res = db.get_note(sys.argv[2])
    if not res:
        console.print("[red]❌ Error: Note not found.[/red]")
        return
    
    console.print(f"[cyan]Current Title:[/cyan] {res['title']}")
    new_title = console.input("[yellow]New Title:[/yellow] ").strip() or res['title']
    
    if db.update_note(sys.argv[2], new_title=new_title):
        console.print("[green]✅ Note title updated successfully![/green]")
    else:
        console.print("[red]❌ Error: Failed to update note.[/red]")

def edit_note_content():
    """تعديل محتوى الملاحظة"""
    if len(sys.argv) < 3:
        console.print("[red]❌ Error: Please provide a note ID.[/red]")
        return
    
    res = db.get_note(sys.argv[2])
    if not res:
        console.print("[red]❌ Error: Note not found.[/red]")
        return
    
    console.print(f"[cyan]Title:[/cyan] {res['title']}")
    console.print("[yellow]Opening editor... (save and exit to continue)[/yellow]")
    
    with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False, mode='w') as tf:
        tf.write(res['content'] or "")
        tf.flush()
        subprocess.call([os.environ.get('EDITOR', 'nano'), tf.name])
        with open(tf.name, 'r') as f: 
            content = f.read()
        os.unlink(tf.name)
    
    if db.update_note(sys.argv[2], new_content=content):
        console.print("[green]✅ Note content updated successfully![/green]")
    else:
        console.print("[red]❌ Error: Failed to update note.[/red]")

def delete_note():
    """حذف ملاحظة"""
    if len(sys.argv) < 3:
        console.print("[red]❌ Error: Please provide a note ID.[/red]")
        return
    
    if db.delete_note(sys.argv[2]):
        console.print("[green]🗑️  Note deleted successfully![/green]")
    else:
        console.print("[red]❌ Error: Note not found.[/red]")

# ============================================================================
# وظائف إضافية
# ============================================================================

def pomodoro_timer():
    """مؤقت بومودورو"""
    try:
        m_in = int(sys.argv[2]) if len(sys.argv) > 2 else 25
        
        console.print()
        console.print(Panel(
            f"[bold magenta]⏳ Focus Mode: {m_in} minutes[/bold magenta]",
            border_style="magenta"
        ))
        console.print()
        
        for i in range(m_in * 60, 0, -1):
            m, s = divmod(i, 60)
            console.print(f"\r[yellow]Remaining:[/yellow] [bold]{m:02d}:{s:02d}[/bold]", end="", highlight=False)
            time.sleep(1)
        
        console.print()
        console.print(Panel(
            "[bold green]🎉 Time's up! Great work![/bold green]",
            border_style="green"
        ))
        console.print()
        
        # تشغيل صوت تنبيه
        try:
            subprocess.run(['beep'], timeout=1)
        except:
            pass
    except ValueError:
        console.print("[red]❌ Error: Invalid time format.[/red]")

def run_command_by_id_or_alias(identifier):
    """تشغيل أمر باستخدام المعرف أو الاسم المستعار"""
    cmd = db.get_command_by_id_or_alias(identifier)
    
    if cmd:
        console.print(f"[yellow]▶ Running:[/yellow] [bold]{cmd['command']}[/bold]")
        db.increment_usage(cmd['cmd_number'])
        subprocess.run(cmd['command'], shell=True)
    else:
        console.print(f"[red]❌ Error: Command '{identifier}' not found.[/red]")
        console.print("[dim]Use 'nr -h' for help.[/dim]")

# ============================================================================
# الدالة الرئيسية
# ============================================================================

def main():
    if len(sys.argv) < 2:
        smart_fzf("all")
        return
    
    cmd = sys.argv[1]
    
    # أوامر المساعدة والمعلومات
    if cmd == "-h":
        show_help()
    elif cmd == "-i":
        show_info()
    
    # أوامر البحث
    elif cmd == "s":
        smart_fzf("all")
    elif cmd == "s-c":
        smart_fzf("c")
    elif cmd == "s-n":
        smart_fzf("n")
    
    # أوامر الأوامر
    elif cmd == "-c":
        show_commands()
    elif cmd == "c-a":
        add_command()
    elif cmd == "e-c":
        edit_command()
    elif cmd == "d-c":
        delete_command()
    
    # أوامر الملاحظات
    elif cmd == "-n":
        show_notes()
    elif cmd == "n-a":
        add_note()
    elif cmd == "e-n":
        edit_note_title()
    elif cmd == "e-n-c":
        edit_note_content()
    elif cmd == "d-n":
        delete_note()
    
    # أوامر إضافية
    elif cmd == "-p":
        pomodoro_timer()
    
    # تشغيل أمر بناءً على المعرف أو الاسم المستعار
    else:
        run_command_by_id_or_alias(cmd)

if __name__ == "__main__":
    main()
