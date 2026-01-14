# 🚀 NumRun

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![NixOS Compatible](https://img.shields.io/badge/NixOS-Compatible-brightgreen.svg)](https://nixos.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-orange.svg)](http://makeapullrequest.com)

**NumRun** is a professional-grade CLI tool built for power users who want to manage and execute complex shell commands using simple index numbers. Stop searching through your bash history—save your best one-liners and run them instantly.

---

## ✨ Features

- **⚡ Instant Execution:** Run any saved command by its ID: `numrun 5`.
- **🏷️ Tagging System:** Categorize commands (e.g., `docker`, `web`, `git`) for better organization.
- **🔍 Advanced Search:** Find commands by their content or associated tags.
- **📝 Integrated Editor:** Edit saved commands directly in your favorite system editor (`Vim`, `Nano`, etc.).
- **📊 Usage Tracking:** Automatically keeps track of how many times you've used each command.
- **⌨️ Smart Autocomplete:** Full TAB-completion support for subcommands and command IDs (Bash & Zsh).
- **❄️ NixOS Ready:** Includes a `shell.nix` for a reproducible, isolated development environment.
- **📦 Import/Export:** Easily backup or sync your commands via JSON files.

---

## 🛠️ Installation

### 1. Standard Installation
```bash
git clone https://github.com/b2-3c/numrun
cd numrun
pip install .

2. NixOS Users (Recommended)

If you are on NixOS, simply run:
Bash

nix-shell

3. Enable Tab Completion

After installation, activate the smart completion for your shell:
Bash

numrun setup-completion
source ~/.bashrc  # or ~/.zshrc for Zsh users

🚀 Quick Start Guide
Save a command
Bash

numrun save "docker exec -it my_container bash"
# Saved as #1

Run by number
Bash

numrun 1

List all commands
Bash

numrun list

Add tags and search
Bash

numrun tag 1 dev
numrun search dev

Edit an existing command
Bash

numrun edit 1

📂 Project Structure

    numrun/cli.py: The heart of the tool, handling arguments and execution.

    numrun/database.py: SQLite wrapper for persistent storage.

    completions/: Shell scripts for TAB completion.

    pyproject.toml: Modern Python packaging configuration.

    shell.nix: Declarative environment for Nix users.

🤝 Contributing

Contributions make the open-source community an amazing place to learn and create.

    Fork the Project.

    Create your Feature Branch (git checkout -b feature/AmazingFeature).

    Commit your Changes (git commit -m 'Add some AmazingFeature').

    Push to the Branch (git push origin feature/AmazingFeature).

    Open a Pull Request.

📜 License

Distributed under the MIT License. See LICENSE for more information.
