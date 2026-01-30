import sys, subprocess, os, tempfile, time, platform, json, re
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.live import Live
from rich.layout import Layout
from rich import box

# استيراد psutil للمراقبة
try:
    import psutil
except ImportError:
    psutil = None

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import Database

db = Database()
VERSION = "2.3.0"
console = Console()

# ============================================================================
# Helpers
# ============================================================================

def get_uptime():
    try:
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.readline().split()[0])
            h = int(uptime_seconds // 3600)
            m = int((uptime_seconds % 3600) // 60)
            return f"{h}h {m}m"
    except: return "N/A"

def get_distro():
    distro = "Linux"
    if os.path.exists("/etc/os-release"):
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="): distro = line.split("=")[1].strip('" \n')
    return distro

def process_interactive_command(cmd_str):
    placeholders = re.findall(r'\{(.*?)\}', cmd_str)
    if not placeholders:
        return cmd_str
    
    console.print(Panel(f"[yellow]🔔 Interactive Command Detected[/yellow]", border_style="yellow"))
    final_cmd = cmd_str
    for p in placeholders:
        val = console.input(f" [green]Enter value for[/green] [bold white]{p}[/bold white]: ").strip()
        final_cmd = final_cmd.replace(f"{{{p}}}", val)
    return final_cmd

# ============================================================================
# System Dashboard (BTOP Style)
# ============================================================================

def make_dashboard_layout():
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3)
    )
    layout["main"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=2)
    )
    layout["left"].split_column(
        Layout(name="cpu"),
        Layout(name="mem"),
        Layout(name="disk")
    )
    layout["right"].split_column(
        Layout(name="proc"),
        Layout(name="net")
    )
    return layout

def get_cpu_info():
    if not psutil: return Panel("psutil not installed")
    cpu_pct = psutil.cpu_percent(interval=None, percpu=True)
    table = Table(show_header=False, box=None, expand=True)
    for i, pct in enumerate(cpu_pct):
        bar = "█" * int(pct/5) + "░" * (20 - int(pct/5))
        color = "green" if pct < 50 else "yellow" if pct < 80 else "red"
        table.add_row(f"CPU{i}", f"[{color}]{bar}[/{color}] {pct}%")
    return Panel(table, title="[bold cyan]CPU Usage[/bold cyan]", border_style="cyan")

def get_mem_info():
    if not psutil: return Panel("psutil not installed")
    mem = psutil.virtual_memory()
    table = Table(show_header=False, box=None, expand=True)
    bar = "█" * int(mem.percent/5) + "░" * (20 - int(mem.percent/5))
    table.add_row("RAM", f"[magenta]{bar}[/magenta] {mem.percent}%")
    table.add_row("Used", f"{mem.used // (1024**2)} MB")
    table.add_row("Free", f"{mem.available // (1024**2)} MB")
    return Panel(table, title="[bold magenta]Memory[/bold magenta]", border_style="magenta")

def get_disk_info():
    if not psutil: return Panel("psutil not installed")
    disk = psutil.disk_usage('/')
    table = Table(show_header=False, box=None, expand=True)
    bar = "█" * int(disk.percent/5) + "░" * (20 - int(disk.percent/5))
    table.add_row("Disk /", f"[yellow]{bar}[/yellow] {disk.percent}%")
    table.add_row("Total", f"{disk.total // (1024**3)} GB")
    return Panel(table, title="[bold yellow]Storage[/bold yellow]", border_style="yellow")

def get_proc_info():
    if not psutil: return Panel("psutil not installed")
    table = Table(title="Top Processes", box=box.SIMPLE, expand=True, header_style="bold blue")
    table.add_column("PID", style="dim")
    table.add_column("Name")
    table.add_column("CPU%", justify="right")
    table.add_column("MEM%", justify="right")
    
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try: procs.append(p.info)
        except: pass
    
    # Sort by CPU
    procs = sorted(procs, key=lambda x: x['cpu_percent'], reverse=True)[:8]
    for p in procs:
        table.add_row(str(p['pid']), p['name'][:15], f"{p['cpu_percent']}%", f"{p['memory_percent']:.1f}%")
    
    return Panel(table, border_style="blue")

def get_net_info():
    if not psutil: return Panel("psutil not installed")
    net = psutil.net_io_counters()
    table = Table(show_header=False, box=None, expand=True)
    table.add_row("Sent", f"[green]{net.bytes_sent // (1024**2)} MB[/green]")
    table.add_row("Recv", f"[blue]{net.bytes_recv // (1024**2)} MB[/blue]")
    return Panel(table, title="[bold green]Network[/bold green]", border_style="green")

def run_dashboard():
    if not psutil:
        console.print("[red]Error: psutil is required for Dashboard. Install with 'pip install psutil'[/red]")
        return

    layout = make_dashboard_layout()
    layout["header"].update(Panel(Align.center(f"[bold cyan]NUMRUN SYSTEM DASHBOARD[/bold cyan] | [white]{datetime.now().strftime('%H:%M:%S')}[/white]"), border_style="cyan"))
    layout["footer"].update(Panel(Align.center("[dim]Press Ctrl+C to Exit | Refreshing every 2s[/dim]"), border_style="dim"))

    with Live(layout, refresh_per_second=0.5, screen=True):
        try:
            while True:
                layout["header"].update(Panel(Align.center(f"[bold cyan]NUMRUN SYSTEM DASHBOARD[/bold cyan] | [white]{datetime.now().strftime('%H:%M:%S')}[/white]"), border_style="cyan"))
                layout["cpu"].update(get_cpu_info())
                layout["mem"].update(get_mem_info())
                layout["disk"].update(get_disk_info())
                layout["proc"].update(get_proc_info())
                layout["net"].update(get_net_info())
                time.sleep(2)
        except KeyboardInterrupt:
            pass

# ============================================================================
# Main Screens
# ============================================================================

def show_info():
    user = os.getenv("USER") or "User"
    host = platform.node()
    distro = get_distro()
    
    cmd_c, note_c, total_usage = db.get_stats()
    p_count, p_mins = db.get_pomodoro_stats()
    
    # System Info Table
    info_table = Table(box=box.ROUNDED, show_header=False, border_style="cyan")
    info_table.add_row("[cyan]User[/cyan]", f"[bold white]{user}[/bold white]")
    info_table.add_row("[cyan]Host[/cyan]", f"[bold white]{host}[/bold white]")
    info_table.add_row("[cyan]OS[/cyan]", f"[bold white]{distro}[/bold white]")
    info_table.add_row("[cyan]Uptime[/cyan]", f"[bold white]{get_uptime()}[/bold white]")
    info_table.add_row("[cyan]Version[/cyan]", f"[bold green]{VERSION} PRO[/bold green]")
    
    # Stats Table
    stats_table = Table(box=box.ROUNDED, show_header=False, border_style="magenta")
    stats_table.add_row("[magenta]Commands[/magenta]", f"[bold yellow]{cmd_c}[/bold yellow]")
    stats_table.add_row("[magenta]Notes[/magenta]", f"[bold yellow]{note_c}[/bold yellow]")
    stats_table.add_row("[magenta]Total Runs[/magenta]", f"[bold yellow]{total_usage}[/bold yellow]")
    stats_table.add_row("[magenta]Focus Sessions[/magenta]", f"[bold blue]{p_count}[/bold blue]")
    stats_table.add_row("[magenta]Focus Time[/magenta]", f"[bold blue]{p_mins}m[/bold blue]")

    logo = Text("""
     ▄▀ ▄▀
      ▀  ▀
     █▀▀▀▀▀█▄
     █░░░░░█ █
     ▀▄▄▄▄▄▀▀
    """, style="cyan")

    console.print()
    console.print(Align.center(logo))
    console.print(Align.center(Columns([info_table, stats_table], equal=True, expand=False)))
    console.print()

def show_commands():
    commands = db.get_all_commands(sort_by="usage")
    if not commands:
        console.print("[yellow]⚠️ No commands saved yet.[/yellow]")
        return
    
    table = Table(title="[bold cyan]Saved Commands (Sorted by Usage)[/bold cyan]", box=box.ROUNDED, header_style="bold magenta")
    table.add_column("ID", style="dim")
    table.add_column("Alias", style="green")
    table.add_column("Command", style="white")
    table.add_column("Tags", style="blue")
    table.add_column("Runs", style="yellow", justify="right")
    table.add_column("Last Used", style="dim")
    
    for r in commands:
        data = dict(r)
        tags = f"#{data.get('tags')}" if data.get('tags') else ""
        last_used = data.get('last_used') or "Never"
        usage = str(data.get('usage_count', 0))
        table.add_row(str(data.get('cmd_number')), data.get('alias') or "---", data.get('command'), tags, usage, last_used)
    
    console.print(table)

def show_notes():
    notes = db.get_all_notes()
    if not notes:
        console.print("[yellow]⚠️ No notes saved yet.[/yellow]")
        return
    
    table = Table(title="[bold magenta]Saved Notes[/bold magenta]", box=box.ROUNDED, header_style="bold cyan")
    table.add_column("ID", style="dim")
    table.add_column("Title", style="white")
    table.add_column("Tags", style="blue")
    table.add_column("Created", style="dim")
    table.add_column("Updated", style="yellow")
    
    for n in notes:
        data = dict(n)
        tags = f"#{data.get('tags')}" if data.get('tags') else ""
        table.add_row(str(data.get('note_id')), data.get('title'), tags, data.get('created_at') or "N/A", data.get('updated_at') or "N/A")
    
    console.print(table)

def smart_fzf(mode="all"):
    items = []
    if mode in ["all", "c"]:
        for r in db.get_all_commands(sort_by="usage"):
            data = dict(r)
            tag_str = f" #{data.get('tags')}" if data.get('tags') else ""
            items.append(f"[CMD] {data.get('cmd_number')} | {data.get('alias') or '---'} | {data.get('command')}{tag_str}")
    if mode in ["all", "n"]:
        for n in db.get_all_notes():
            data = dict(n)
            tag_str = f" #{data.get('tags')}" if data.get('tags') else ""
            items.append(f"[NOTE] {data.get('note_id')} | {data.get('title')}{tag_str}")
    
    if not items: console.print("[yellow]No items found.[/yellow]"); return
    try:
        hdr = "ALL" if mode=="all" else ("COMMANDS" if mode=="c" else "NOTES")
        p = subprocess.Popen(['fzf', '--ansi', '--reverse', '--header', f'| SEARCH: {hdr} |'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        out, _ = p.communicate(input="\n".join(items))
        if out:
            if "[CMD]" in out:
                cid = out.split('|')[0].replace("[CMD]", "").strip()
                cmd_raw = out.split('|')[2].split(' #')[0].strip()
                cmd_exec = process_interactive_command(cmd_raw)
                console.print(f"[yellow]▶ Running:[/yellow] [bold white]{cmd_exec}[/bold white]")
                db.increment_usage(cid)
                subprocess.run(cmd_exec, shell=True)
            elif "[NOTE]" in out:
                nid = out.split('|')[0].replace("[NOTE]", "").strip()
                res = db.get_note(nid)
                if res:
                    data = dict(res)
                    console.print()
                    console.print(Panel(data.get('content', ''), title=f"[bold magenta]{data.get('title')}[/bold magenta]", subtitle=f"[blue]#{data.get('tags', '')}[/blue]", border_style="magenta"))
                    console.print()
    except Exception as e: console.print(f"[red]Search error: {e}[/red]")

# ============================================================================
# Advanced Pomodoro
# ============================================================================

def advanced_pomodoro(minutes=25, task="Focus Session"):
    # استخدام Align لتوسيط المحتوى بدلاً من خاصية align في Panel لضمان التوافق
    content = Align.center(f"[bold blue]POMODORO PRO[/bold blue]\n[white]Task: {task}[/white]")
    console.print(Panel(content, border_style="blue"))
    
    total_seconds = minutes * 60
    with Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40, complete_style="green", finished_style="bold green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        p_task = progress.add_task(f"[white]Remaining", total=total_seconds)
        
        try:
            start_time = time.time()
            while not progress.finished:
                elapsed = time.time() - start_time
                progress.update(p_task, completed=elapsed)
                time.sleep(0.5)
            
            console.print(f"\n[bold green]🎉 Session Completed![/bold green]")
            db.log_pomodoro(task, minutes, "Completed")
            print("\a") 
        except KeyboardInterrupt:
            console.print(f"\n\n[bold red]⚠️ Session Interrupted.[/bold red]")
            db.log_pomodoro(task, int((time.time() - start_time)/60), "Interrupted")

# ============================================================================
# Help & CLI
# ============================================================================

def show_help():
    help_text = f"""
    [bold cyan]NUMRUN v{VERSION} PRO[/bold cyan] - Command & Note Manager

    [yellow]USAGE:[/yellow]
      [green]nr[/green] [white][id/alias][/white]     Run command
      [green]nr s[/green]              Search everything (fzf)
      [green]nr dash[/green]           [bold cyan]System Dashboard (btop style)[/bold cyan]
    
    [yellow]COMMANDS:[/yellow]
      [green]c-a [cmd][/green]        Add cmd (Use {{var}} for interactive)
      [green]-c[/green]               List commands
      [green]e-c [id][/green]         Edit command/tags
      [green]d-c [id][/green]         Delete command
    
    [yellow]NOTES:[/yellow]
      [green]n-a [title][/green]      Add note
      [green]-n[/green]               List notes
      [green]e-n [id][/green]         Edit note title/tags
      [green]d-n [id][/green]         Delete note
    
    [yellow]POMODORO PRO:[/yellow]
      [green]-p [min] [task][/green]  Start focus session
    
    [yellow]SYSTEM:[/yellow]
      [green]-i[/green]               Info & Stats
      [green]export[/green]           Export to JSON
      [green]import [file][/green]    Import from JSON
    """
    console.print(Panel(help_text, border_style="cyan", title="Help Menu"))

def main():
    if len(sys.argv) < 2: smart_fzf("all"); return
    cmd = sys.argv[1]

    if cmd == "-h": show_help()
    elif cmd == "-i": show_info()
    elif cmd == "dash": run_dashboard()
    elif cmd == "s": smart_fzf("all")
    elif cmd == "s-c": smart_fzf("c")
    elif cmd == "s-n": smart_fzf("n")
    elif cmd == "export":
        data = db.export_data()
        filename = f"numrun_backup_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w') as f: json.dump(data, f, indent=4)
        console.print(f"[green]✅ Data exported to {filename}[/green]")
    elif cmd == "import" and len(sys.argv) > 2:
        try:
            with open(sys.argv[2], 'r') as f:
                data = json.load(f)
                for c in data.get('commands', []): db.add_command(c['command'], c.get('alias'), c.get('tags', ''))
                for n in data.get('notes', []): db.add_note(n['title'], n['content'], n.get('tags', ''))
                console.print("[green]✅ Data imported successfully.[/green]")
        except Exception as e: console.print(f"[red]❌ Import error: {e}[/red]")
    elif cmd == "-p": 
        m = int(sys.argv[2]) if len(sys.argv) > 2 else 25
        t = sys.argv[3] if len(sys.argv) > 3 else "Focus Session"
        advanced_pomodoro(m, t)
    elif cmd == "-c": show_commands()
    elif cmd == "c-a":
        f_cmd = " ".join(sys.argv[2:])
        if not f_cmd: return
        al = console.input(f" [yellow]Alias (Optional):[/yellow] ").strip() or None
        tg = console.input(f" [yellow]Tags (comma separated):[/yellow] ").strip()
        db.add_command(f_cmd, alias=al, tags=tg); console.print("[green]✅ Saved.[/green]")
    elif cmd == "-n": show_notes()
    elif cmd == "n-a":
        t = " ".join(sys.argv[2:]) or "Untitled"
        tg = console.input(f" [yellow]Tags:[/yellow] ").strip()
        with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tf:
            subprocess.call([os.environ.get('EDITOR', 'nano'), tf.name])
            with open(tf.name, 'r') as f: content = f.read()
        if content.strip(): db.add_note(t, content, tags=tg); console.print("[green]✅ Saved.")
    elif cmd == "e-c" and len(sys.argv) > 2:
        db.update_command(sys.argv[2], console.input("New Cmd: "), console.input("New Alias: "), console.input("New Tags: ")); console.print("[green]✅[/green]")
    elif cmd == "e-n" and len(sys.argv) > 2:
        db.update_note(sys.argv[2], new_title=console.input("New Title: "), new_tags=console.input("New Tags: ")); console.print("[green]✅[/green]")
    elif cmd == "d-c" and len(sys.argv) > 2:
        if db.delete_cmd(sys.argv[2]): console.print("[green]🗑️ Deleted.[/green]")
    elif cmd == "d-n" and len(sys.argv) > 2:
        if db.delete_note(sys.argv[2]): console.print("[green]🗑️ Deleted.[/green]")
    else:
        r = db.get_command_by_id_or_alias(cmd)
        if r:
            data = dict(r)
            cmd_exec = process_interactive_command(data.get('command'))
            db.increment_usage(data.get('cmd_number'))
            subprocess.run(cmd_exec, shell=True)
        else:
            console.print(f"[red]❌ Error. Command '{cmd}' not found. Use 'nr -h' for help.[/red]")

if __name__ == "__main__":
    main()
