# SnapCode

SnapCode is a simple desktop utility designed to bundle your source code into a single, LLM-friendly output. It exists primarily because I’m too lazy to manually copy and paste a dozen files just to get an AI to explain a new project to me when I have no clue what the flow is or how it even works.

## Why this exists

Because I was too lazy to copy and paste a shitload of files just to give an AI some context. It handles the boring stuff: respects your .gitignore, filters by extension, and formats everything into clean Markdown or XML so the AI doesn't get confused.

## Features

- Respects .gitignore patterns and custom folder exclusions.
- Filter files by extension (include or exclude).
- Output formats: Markdown (standard), XML (Claude-optimized), or raw string lists.
- Remembers your settings so you don't have to re-type your exclusions every time you open it.
- Built with Python and Tkinter, so it doesn't require a 2GB Electron installation to run.

## Installation

You need Python 3.8 or higher. No weird dependencies are required for the core app, as it uses the standard library.

1. Clone the repository:
   git clone https://github.com/yourusername/SnapCode.git

2. Enter the directory:
   cd SnapCode

3. Run it:
   python snapcode.py

## Usage

1. Open a folder.
2. Tell the app which folders to ignore (the ones you probably should have put in your gitignore anyway).
3. Select the files you actually care about.
4. Click "Generate Output" and it will be copied to your clipboard.
5. Paste it into your AI of choice and watch it try to make sense of your logic.

## License

MIT. Do whatever you want with it. I highly doubt anyone else will actually use this anyway. XD