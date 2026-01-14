import os
from pathlib import Path

def install():
    home = Path.home()
    completion_path = Path(__file__).parent.parent / "completions" / "numrun.bash"
    abs_path = completion_path.absolute()
    
    shell = os.environ.get("SHELL", "")
    rc = home / (".zshrc" if "zsh" in shell else ".bashrc")

    if rc.exists():
        line = f"\nsource {abs_path} # numrun completion\n"
        with open(rc, "r") as f:
            if str(abs_path) in f.read():
                print("✅ Already installed.")
                return
        with open(rc, "a") as f:
            f.write(line)
        print(f"✅ Installed to {rc}. Please run 'source {rc}'")
