# 🚀 NumRun

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![NixOS Compatible](https://img.shields.io/badge/NixOS-Compatible-brightgreen.svg)](https://nixos.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-orange.svg)](http://makeapullrequest.com)

**NumRun** is a professional-grade CLI tool for power users to manage and execute complex shell commands using simple index numbers. It features a **Fastfetch-style interface**, interactive search, and dynamic arguments.

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
├─ cli.py         # Core logic with Fastfetch-style UI and Argument Parser
├─ database.py    # SQLite handler with auto-migration support
├─ completions/   # Shell completion scripts for Bash/Zsh
├─ setup.sh       # One-click installer and alias creator
└─ shell.nix      # Reproducible environment for Nix users
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
