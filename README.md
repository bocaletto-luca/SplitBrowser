# SplitBrowser

A Python-based desktop web browser featuring dynamic split-screen layouts, multi-tab support, and per-pane fullscreen capabilities.

Repository: https://github.com/bocaletto-luca/SplitBrowser

---

## Table of Contents

- [Features](#features)  
- [Requirements](#requirements)  
- [Installation](#installation)  
- [Usage](#usage)  
- [Keyboard Shortcuts](#keyboard-shortcuts)  
- [Project Structure](#project-structure)  
- [Contributing](#contributing)  
- [License](#license)  

---

## Features

- Multi-tab browsing with easy “New Tab” and “Close Tab” commands  
- Split each tab into 1–4 panes, horizontally or vertically, with equal resizing:  
  - 1 panel → single view  
  - 2 panels → 50% / 50%  
  - 3 panels → ~33% each  
  - 4 panels → 25% each  
- Each pane includes:  
  - URL bar with “Go” button  
  - Back, Forward, Reload, Clear Cache controls  
- Full-screen modes:  
  - Entire window (F11 / Esc)  
  - Active pane only (Shift+F11 / Esc)  
- Pane-only fullscreen supports cycling through panes using Ctrl+Tab / Ctrl+Shift+Tab  
- Tab-only fullscreen supports cycling through tabs using Ctrl+PgUp / Ctrl+PgDown  
- Menu bar remains visible at all times for quick access  

---

## Requirements

- Python 3.7 or newer  
- PyQt5  
- PyQtWebEngine  

---

## Installation

```bash
# Clone the repository
git clone https://github.com/bocaletto-luca/SplitBrowser.git
cd SplitBrowser

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate    # macOS / Linux
# .\venv\Scripts\activate   # Windows PowerShell

# Install dependencies
pip install --upgrade pip
pip install PyQt5 PyQtWebEngine
```

---

## Usage

```bash
python main.py
```

1. Open the **File** menu or use shortcuts to manage tabs.  
2. Use the **Split** menu to choose 1–4 panels, arranged horizontally or vertically.  
3. Navigate in each pane with Back, Forward, Reload, Clear Cache, and URL bar.  
4. Toggle fullscreen:  
   - Entire window: **F11** or **Esc**  
   - Active pane: **Shift+F11** or **Esc**  
5. Switch among tabs and panes in fullscreen modes with the keyboard shortcuts below.  

---

## Keyboard Shortcuts

- Ctrl+T: New Tab  
- Ctrl+W: Close Tab  
- F11: Toggle fullscreen for the entire window  
- Shift+F11: Toggle fullscreen for the active pane only  
- Esc: Exit fullscreen (pane first, then window)  
- Ctrl+PgUp / Ctrl+PgDown: Switch tabs (in window-fullscreen mode)  
- Ctrl+Tab / Ctrl+Shift+Tab: Cycle panes (in pane-fullscreen mode)  

---

## Project Structure

```plaintext
SplitBrowser/
├── main.py            # Main application script
├── requirements.txt   # (optional) pip freeze output
└── README.md          # This file
```

---

## Contributing

1. Fork the repository  
2. Create a feature branch (`git checkout -b feature/YourFeature`)  
3. Implement your changes and commit (`git commit -am 'Add feature'`)  
4. Push to your fork (`git push origin feature/YourFeature`)  
5. Open a Pull Request  

---

## License

This project is released under the MIT License.  
© 2025 Luca Bocaletto
