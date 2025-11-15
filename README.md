# Code Analyzer

A Python-based multi-language static code analysis and vulnerability detection tool with:
- a command-line interface,
- a desktop GUI (wxPython), and
- a simple web UI served over HTTP.

## Overview

Code Analyzer is designed to help developers identify potential security issues in source code. It currently supports Python, JavaScript/TypeScript (including Angular projects), and Java using lightweight pattern-based rules. The same analysis engine is exposed via a CLI, a wxPython desktop GUI, and a minimal web interface.

## Features

- **Vulnerability Detection**: Automated scanning for common security vulnerabilities
- **Multi-language Support**: Python, JavaScript/TypeScript (including Angular TS projects), and Java
- **CLI Interface**: Simple `python3 code_analyzer.py` command-line tool
- **GUI Interface**: User-friendly wxPython desktop GUI
- **Web UI**: Lightweight HTML interface served via `server.py`
- **Cross-platform Support**: Works on macOS, Linux, and Windows

## Project Structure

```
code-analyzer/
├── server.py              # Simple HTTP server with web UI for analysis
├── code_analyzer.py       # Main CLI entrypoint for the analyzer
├── WARP.md                # Project documentation for Warp
├── README.md              # This file
├── .gitignore             # Git ignore rules
├── requirements.txt       # Python dependencies (wxPython for GUI)
├── detectors/
│   ├── __init__.py
│   └── vulnerability_scanner.py  # Multi-language vulnerability scanner
└── src/
    └── user-gui/
        └── gui.py        # wxPython desktop GUI application
```

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/kush11251/code-analyzer.git
cd code-analyzer
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

## Usage

### Command-line analyzer
```bash
python3 code_analyzer.py .
```

By default this scans the current directory (excluding common dependency/build folders such as `venv/`, `.git/`, `node_modules/`, `dist/`, `.angular/`, `out-tsc/`) and prints potential security issues it finds. For JSON output:

```bash
python3 code_analyzer.py . --format json
```

### Desktop GUI
```bash
python3 src/user-gui/gui.py
```

The GUI lets you pick a folder to analyze and shows results in a table inside the window.

### Web UI (local web deployment)
```bash
python3 server.py
```

This starts the web UI on `http://localhost:8000/`. Open that URL in your browser, enter the path to the project you want to scan (for example, the root of an Angular TypeScript project or a Python repo), and click **Scan** to see a table of vulnerabilities.

## Dependencies

This project keeps runtime dependencies minimal:

- `wxPython` - GUI framework for the desktop UI

Install them with:

```bash
pip3 install -r requirements.txt
```

## Features in Development

- [ ] Advanced vulnerability patterns
- [x] Multi-language support (Python, JS/TS, Java)
- [ ] Detailed vulnerability reports (export formats, filters)
- [ ] Integration with CI/CD pipelines
- [ ] Custom rule creation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

---

**Author**: Kussagra Pathak

**Last Updated**: November 2025
