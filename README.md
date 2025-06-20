# 🚀 Karbon - AI Web Builder

**Karbon** is a desktop app that uses AI to generate and iteratively refine HTML/CSS/JS websites from simple prompts. Built with Python and Tkinter, it provides a live preview and export functionality.

# Screenshots
![Karbon UI Screenshot](https://i.imgur.com/7eYNysu.png) 
<div style="overflow-x: auto; white-space: nowrap;">
  <img src="https://i.imgur.com/0IqmrUS.png" style="width: 300px; display: inline-block; margin-right: 10px;" />
  <img src="https://i.imgur.com/BkvTUY2.png" style="width: 300px; display: inline-block; margin-right: 10px;" />
  <img src="https://i.imgur.com/pnhpTPb.png" style="width: 300px; display: inline-block; margin-right: 10px;" />
  <img src="https://i.imgur.com/Y6wj97j.png" style="width: 300px; display: inline-block;" />
</div>

---

## 🧠 Features

- 🔤 Prompt-based website generation using AI
- 🛠️ Iterative prompt-based updates to the code
- 🖼️ Live preview in a browser window
- 📤 Export final code to HTML/CSS/JS files
- 🎛️ Simple and intuitive Tkinter GUI

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/prakhardoneria/karbon.git
cd karbon
````

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the App

```bash
python ui.py
```

> The app window will launch, allowing you to enter a prompt to generate your first website layout.

---

## 🛠️ Building Executable (Windows)

Use [PyInstaller](https://pyinstaller.org/) to create a standalone `.exe`:

```bash
pyinstaller ui.py --onefile --noconsole --name Karbon --icon=icon.ico
```

The built executable will appear in the `dist/` folder.

---

## 📦 Release via GitHub Actions

On push to the `main` branch, GitHub Actions will:

* Build `Karbon.exe` using PyInstaller
* Create a GitHub release with the `.exe` attached

See `.github/workflows/build-karbon.yml` for details.

---

## 📁 Project Structure

```
karbon/
├── ui.py                  # Main UI launcher
├── ai_engine.py           # Handles AI code generation
├── exporter.py            # Exports final code to files
├── preview.py             # Opens code in browser preview
├── ui_items/              # Modularized UI components
│   ├── __init__.py
│   ├── prompt_view.py
│   ├── editor_view.py
│   └── karbon_ui.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🧑‍💻 Contributing

Pull requests are welcome! To contribute:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a pull request

---

## 📝 License

GNU General Public License v3.0. See `LICENSE` file for details.

---


