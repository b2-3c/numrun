# 🚀 NumRun (v2.0.4)

**The Ultimate Smart Notebook for Terminal Users.**

NumRun is a powerful and highly optimized Command Line Interface (CLI) tool designed for developers and power users. It allows you to save complex commands, organize them with aliases, and manage quick text notes—all within a modern, visually appealing terminal interface.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![NixOS Compatible](https://img.shields.io/badge/NixOS-Compatible-brightgreen.svg)](https://nixos.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-orange.svg)](http://makeapullrequest.com)

---

## ✨ Key Features (v2.0.4 Enhancements)

The latest version introduces significant improvements in both functionality and user experience:

*   **⚡ Instant Execution:** Run saved commands using their ID or Alias (e.g., `nr 1` or `nr ll`).
*   **🎨 Modern UI/UX (Powered by Rich):** Replaced basic ANSI colors with the `rich` library for professional, table-based, and highly readable output.
*   **📊 Usage Tracking:** Commands now track their usage count and last used date, allowing you to identify your most frequent commands.
*   **📝 Enhanced Note Management:** Added a dedicated command (`nr e-n-c`) to edit note content directly using your default system editor.
*   **⏱️ Pomodoro Timer:** Built-in focus timer (`nr -p`) with an improved visual design.
*   **🔍 Smart Search (fzf):** Interactive fuzzy search across all commands and notes.
*   **🛠️ Robust Installation:** The `setup.sh` script is now highly resilient, automatically handling dependencies (`rich`) and complex path structures across different shells (Bash/Zsh).

---

## 🛠️ Installation

### 1️⃣ Quick Setup (Recommended)

Ensure you have Python 3 and `pip3` installed.

1.  Clone the repository and navigate to the project directory:
    ```bash
    git clone https://github.com/b2-3c/numrun
    cd numrun
    ```
2.  Run the setup script. This will install the necessary Python dependencies (`rich`) and set up the `nr` alias in your shell configuration files (`.bashrc`, `.zshrc`).
    ```bash
    bash setup.sh
    ```
3.  Reload your shell configuration to activate the `nr` command:
    ```bash
    source ~/.zshrc  # Use ~/.bashrc if you are on Bash
    ```

### 2️⃣ Dependencies

NumRun now requires the `rich` Python library for its advanced UI. The `setup.sh` script handles this automatically.

---

## 📖 NumRun Commands Reference

| الأمر | الوصف |
| :--- | :--- |
| `nr [id/alias]` | تشغيل أمر محفوظ باستخدام المعرف أو الاسم المستعار. |
| `nr s` | البحث التفاعلي الشامل (أوامر وملاحظات) باستخدام `fzf`. |
| `nr s-c` | البحث التفاعلي في الأوامر فقط. |
| `nr s-n` | البحث التفاعلي في الملاحظات فقط. |
| `nr -c` | عرض قائمة بجميع الأوامر المحفوظة في جدول منظم (يتضمن عداد الاستخدام). |
| `nr c-a [cmd]` | إضافة أمر جديد مع اقتراح اسم مستعار تلقائي. |
| `nr e-c [id]` | تعديل الأمر والاسم المستعار لأمر موجود. |
| `nr d-c [id]` | حذف أمر. |
| `nr -n` | عرض قائمة بجميع الملاحظات المحفوظة في جدول منظم. |
| `nr n-a [title]` | إضافة ملاحظة جديدة وفتح المحرر لكتابة محتواها. |
| `nr e-n [id]` | تعديل عنوان ملاحظة موجودة. |
| `nr e-n-c [id]` | **(جديد)** تحرير محتوى ملاحظة موجودة باستخدام المحرر الافتراضي. |
| `nr d-n [id]` | حذف ملاحظة. |
| `nr -i` | عرض معلومات النظام وإحصائيات الاستخدام بتصميم جديد. |
| `nr -p [min]` | تشغيل مؤقت بومودورو (افتراضي 25 دقيقة). |
| `nr -h` | عرض شاشة المساعدة. |

---

## 💡 Example Usage

### 1. Adding and Running a Command

```bash
# Add a command with an alias 'll'
$ nr c-a "ls -la"

# Run the command using its alias
$ nr ll
```

### 2. Viewing Stats and Commands

```bash
# View system info and usage statistics
$ nr -i

# View the list of commands (note the Usage count)
$ nr -c
```

### 3. Managing Notes

```bash
# Add a new note titled "Project Setup"
$ nr n-a "Project Setup"

# Edit the content of note ID 1
$ nr e-n-c 1
```

---

## 📂 Project Structure

```
numrun/
├── numrun/                
│   ├── cli.py             # The main application logic (v2.0.4)
│   ├── database.py        # SQLite database handler (v2.0.4)
│   └── ...
├── setup.sh               # Installation script (v2.0.4)
├── README.md              # This file
└── LICENSE                
```

---

## 🤝 Contributing

We welcome contributions! Feel free to open an issue or submit a pull request on GitHub.

---

## 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for more information.
