# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project overview

This repository implements two main pieces of functionality:

1. A minimal demo that serves the current server time over HTTP and launches a desktop GUI (using wxPython) to display both the server time and the local time.
2. A simple static "code analyzer" CLI that scans a project directory for common security issues in several languages (Python, JavaScript/TypeScript, Java) using lightweight pattern-based rules.

The rest of the tree mainly consists of a Python virtual environment and a `detectors/` package that contains the static analysis logic.

## Key commands

All commands below assume the working directory is the project root.

- Run the HTTP server (spawns GUI on each request):
  - `python server.py`
  - Then open `http://localhost:8000/` in a browser. Each page load returns an HTML page showing the current server time and, in addition, launches the wxPython GUI.
- Run the GUI directly (without the HTTP server):
  - `python src/user-gui/gui.py`
  - Optionally pass a timestamp string as the first argument (e.g. `python src/user-gui/gui.py "2025-01-01 12:00:00"`); this will be displayed as the "Server Time" in the GUI.
- Run the static code analyzer CLI:
  - `python code_analyzer.py .`
  - By default this scans the current directory (excluding common dependency folders like `venv/`, `.git/`, `node_modules/`) and prints potential security issues it finds.
  - For JSON output: `python code_analyzer.py . --format json`

There is no configured test suite, linter, or build system in this repository as of now. If you add one (e.g. pytest or a formatter), also update this file with the exact commands.

## Code structure and architecture

Only a small portion of this tree is application code; `venv/` is a Python virtual environment and should generally be treated as third-party dependencies rather than project source.

### Entry point and HTTP layer

- `server.py`
  - Defines `SimpleHandler`, a subclass of `http.server.BaseHTTPRequestHandler`.
  - On each `GET` request, it:
    - Responds with a simple HTML page containing the current server time.
    - Builds the path to `src/user-gui/gui.py` and launches it as a separate process via `subprocess.Popen([sys.executable, gui_path, now])`, passing the current time as a string.
  - `run_server()` sets up an `HTTPServer` bound to port 8000 and calls `serve_forever()`. The `__main__` block invokes `run_server()`.

### GUI layer

- `src/user-gui/gui.py`
  - Uses `wxPython` to create a small desktop window (`TimeFrame`).
  - Accepts an optional command-line argument representing the server time (`sys.argv[1]`).
  - Displays two labels, updated once per second via a `wx.Timer`:
    - `Local Time: <current local time>` (updated continuously)
    - `Server Time: <value passed from server.py>` (if provided)
  - The module’s `__main__` block initializes the `wx.App`, constructs `TimeFrame`, and starts the event loop.

### Other directories

- `detectors/`
  - Contains the static analysis implementation for the code analyzer.
  - `detectors/vulnerability_scanner.py` exposes a simple multi-language scanner that looks for common insecure patterns in Python, JavaScript/TypeScript, and Java.
- `venv/`
  - Python virtual environment. Do not modify code under `venv/` as part of application changes; treat it as installed dependencies.

If you introduce new subsystems (e.g., additional detectors, reporting, or configuration management), prefer grouping them into dedicated top-level packages (such as `detectors/` or `core/`) and update this file with their responsibilities and entry points.
