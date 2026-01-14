# 🚀 NumRun

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![NixOS Compatible](https://img.shields.io/badge/NixOS-Compatible-brightgreen.svg)](https://nixos.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-orange.svg)](http://makeapullrequest.com)

(NumRun) is the "smart notebook" for black screen users. Instead of wasting time digging through your command history for a complex command you wrote a week ago, this tool lets you save your long commands and assign them a simple number (e.g., number 1). Once you type nr 1, the command runs instantly, with an awesome feature that warns you if the command you’re about to run is dangerous (like deletion commands) so you don’t make a mistake. You can even search through your commands quickly and visually.

---

## ✨ Pro Features

* **⚡ Instant Execution:** Run any command by its ID:

  ```bash
  nr 5
  ```
* **🎯 Interactive Mode:** Run `nr` without arguments to open a visual search (FZF integration).
* **🔧 Dynamic Arguments:** Save commands with `$1, $2` and pass values at runtime:

  ```bash
  nr 1 google.com
  ```
* **🛡️ Smart Guard:** Automatically detects dangerous commands (like `rm`) and asks for confirmation.
* **📊 Usage Analytics:** Tracks execution counts and last used timestamps.
* **🏷️ Tagging & Search:** Search by content or custom tags like `docker` or `git`.
* **⌨️ TAB Autocomplete:** Deep integration with Bash and Zsh.
* **❄️ NixOS Optimized:** Reproducible environment via `shell.nix`.

---

## 🛠️ Installation

### 1️⃣ Quick Setup (Recommended)

```bash
git clone https://github.com/b2-3c/numrun
cd numrun
bash setup.sh
source ~/.bashrc  # or ~/.zshrc
```

### 2️⃣ Manual Installation

```bash
pip install -e .
numrun setup-completion
```

---

## 🚀 Quick Start Guide

### Save a Command with Dynamic Arguments

```bash
nr save "ping -c 3 $1"
# Saved as #1
```

### Execute with Value

```bash
nr 1 google.com
# Executes: ping -c 3 google.com
```

### Visual Search (FZF)

Type `nr` and press Enter to browse your commands interactively.

### Smart Guard in Action

If you try to run a command containing `rm` or `dd`, NumRun will prompt:
⚠️ DANGER DETECTED. Confirm execution? (y/N)

---

## 📂 Project Structure

```
numrun/
├── numrun/                # Core Package Directory
│   ├── __init__.py        # Makes the directory a Python package
│   ├── cli.py             # Main CLI Logic, Fastfetch UI, and FZF integration
│   ├── database.py        # SQLite Database handler and migrations
│   └── setup_completion.py # Script to install shell TAB completion
├── completions/           # Shell completion definition files
│   ├── numrun.bash
│   └── numrun.zsh
├── pyproject.toml         # Build system requirements and CLI entry points
├── shell.nix              # NixOS reproducible environment file
├── setup.sh               # Automated installation & alias setup script
├── README.md              # Project documentation and usage guide
└── LICENSE                # Project license (e.g., MIT)
```

---

## 🤝 Contributing

1. Fork the project.
2. Create a feature branch:

   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. Implement your changes.
4. Push to the branch:

   ```bash
   git push origin feature/AmazingFeature
   ```
5. Open a Pull Request.

---

## 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for more information.
