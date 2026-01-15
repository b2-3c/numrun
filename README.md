# 🚀 NumRun (v1.0.1)

**The Ultimate Smart Notebook for Terminal Users.**

NumRun is a productivity tool designed for developers who use the command line. It allows you to save complex commands, organize them into groups, and keep quick text notes—all without leaving your terminal.
![Screenshot](screenshots/1.png)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![NixOS Compatible](https://img.shields.io/badge/NixOS-Compatible-brightgreen.svg)](https://nixos.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-orange.svg)](http://makeapullrequest.com)

---

## ✨ Key Features

* **⚡ Instant Execution:** Run saved commands using their ID (e.g., `nr 1`).
* **📂 Batch Groups:** Organize commands into groups (e.g., `setup`, `deploy`) and run them sequentially with `nr run-group`.
* **📝 Quick Notes:** Built-in notebook to store snippets and reminders.
* **🛡️ Smart Guard:** Automatically detects dangerous keywords (`rm`, `dd`) and asks for confirmation.
* **🐍 No Dependencies:** Written in pure Python 3 using SQLite; works on NixOS without pip install.
* **💾 Data Portability:** Export your entire database to a JSON file for backup or sync.

---

## 🛠️ Installation

### 1️⃣ Quick Setup (Recommended)

```bash
git clone https://github.com/b2-3c/numrun
cd numrun
bash setup.sh
source ~/.bashrc  # or ~/.zshrc
```
Install the search utility: nix-env -iA nixos.fzf (or via your system's package manager).
### 2️⃣ Manual Installation

```bash
pip install -e .
numrun setup-completion
```

```bash
source ~/.bashrc
```

---

## 🚀 Quick Start Guide

| Command                                | Description                                         |
| -------------------------------------- | --------------------------------------------------- |
| `nr save "ls -la"`                     | Save a command to the 'general' group.              |
| `nr save "nix-collect-garbage" -g sys` | Save a command to a specific group.                 |
| `nr list`                              | View all saved commands and their groups.           |
| `nr run-group sys`                     | Execute all commands in the 'sys' group.            |
| `nr note add "Server IP"`              | Create a new text note (opens your default editor). |
| `nr note ls`                           | List all saved notes.                               |
| `nr note view 1`                       | View the content of a specific note.                |
| `nr export`                            | Backup everything to `~/numrun_backup.json`.        |
| `nr del 5`                             | Delete a command by its ID.                         |

---

### Example Usage

Save a command with dynamic arguments:

```bash
nr save "ping -c 3 $1"
# Saved as #1
```

Execute the command with a value:

```bash
nr 1 google.com
# Executes: ping -c 3 google.com
```

Open visual search (FZF):

```bash
nr
```

Smart Guard in action (prevents dangerous commands like `rm`):

```bash
⚠️ DANGER DETECTED. Confirm execution? (y/N)
```

---

## 📂 Project Structure

```
numrun/
├── numrun/                
│   ├── __init__.py        
│   ├── cli.py             
│   ├── database.py        
│   └── setup_completion.py
├── completions/           
│   ├── numrun.bash
│   └── numrun.zsh
├── pyproject.toml         
├── shell.nix              
├── setup.sh               
├── README.md              
└── LICENSE                
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
