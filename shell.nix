{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = [ pkgs.python3 pkgs.python3Packages.pip ];
  shellHook = ''
    if [ ! -d ".venv" ]; then python3 -m venv .venv; fi
    source .venv/bin/activate
    pip install -e . --quiet
    echo "🚀 Advanced NumRun Environment Loaded!"
  '';
}
