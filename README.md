# 🕒 Nightreign Auto-Timer

## 🔍 Description

Nightreign Auto-Timer is a lightweight overlay tool that detects specific keywords (e.g., "DAY", "JOUR", etc.) on screen using OCR and triggers a two-cycle timer sequence, useful for Elden Ring Nightreign.

The interface is discreet, draggable, always on top, and can be controlled through global keyboard shortcuts.

---

## 🧠 Main Features

- Automatic OCR detection of keywords like `DAY`, `JOUR`, `GIORNO`, `DIA`, `TAG`.
- Configurable and persistent overlay (position, background)
- Live update and always-on-top
- keyboard controls

---

## 🖥 Installation & Usage

1. **Download the `.exe` version** (or clone the repo and run via Python)
2. Launch `nightreign-auto-timer.exe`
3. When the overlay appears, wait for the trigger keyword to show on screen
4. The timer sequence will auto-start upon detection

---

## 🎹 Global Keyboard Shortcuts

| Shortcut | Action                              |
| -------- | ----------------------------------- |
| Ctrl + R | Reset timer (back to WAITING state) |
| Ctrl + Q | Quit the program                    |
| Ctrl + H | Toggle overlay visibility           |
| Ctrl + B | Toggle transparent background       |
| Ctrl + S | Manually start a timer sequence     |

---

## 💾 Configuration

A `config.txt` file is auto-generated with:

- The last window position
- Background mode (black or transparent)

---

## 📄 Third-party Licenses

### Tesseract OCR

This program includes Tesseract OCR, licensed under the Apache License 2.0.

- Project: https://github.com/tesseract-ocr/tesseract
- License: https://www.apache.org/licenses/LICENSE-2.0

Tesseract is © Google Inc. and contributors. Redistributed in binary form without modification.

---

## 📦 Optional Compilation

If you'd like to build the `.exe` yourself:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --icon=timer.ico --add-data "Tesseract-OCR;Tesseract-OCR" timer.py
```

---

## 💬 Support / Suggestions

For feedback, issues, or improvements — feel free to open a GitHub issue or comment on the Nexus Mods page!
