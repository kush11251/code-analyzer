# Code Analyzer

A comprehensive Python-based code analysis and vulnerability detection tool with a modern GUI interface and HTTP server capabilities.

## Overview

Code Analyzer is designed to help developers identify potential vulnerabilities, code quality issues, and security concerns in Python codebases. The project combines a robust backend server with an intuitive graphical user interface to provide real-time analysis and reporting.

## Features

- **Vulnerability Detection**: Automated scanning for common security vulnerabilities
- **Code Quality Analysis**: Real-time code quality checks and suggestions
- **GUI Interface**: User-friendly wxPython-based graphical interface
- **HTTP Server**: RESTful API server for remote analysis requests
- **Real-time Updates**: Live datetime tracking and system monitoring
- **Cross-platform Support**: Works on macOS, Linux, and Windows

## Project Structure

```
code-analyzer/
├── server.py              # HTTP server for remote analysis
├── code_analyzer.py       # Main analysis engine
├── WARP.md               # Project documentation
├── README.md             # This file
├── .gitignore            # Git ignore rules
├── detectors/
│   ├── __init__.py
│   └── vulnerability_scanner.py  # Vulnerability detection modules
└── src/
    └── user-gui/
        └── gui.py        # wxPython GUI application
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

### Running the GUI
```bash
python3 src/user-gui/gui.py
```

### Starting the Server
```bash
python3 server.py
```

The server will start on `http://localhost:8000` and provide analysis capabilities through HTTP endpoints.

### Running the Code Analyzer
```bash
python3 code_analyzer.py
```

## Dependencies

- `wxPython` - GUI framework
- `numpy` - Numerical computations
- Additional dependencies listed in `requirements.txt`

## Features in Development

- [ ] Advanced vulnerability patterns
- [ ] Multi-language support
- [ ] Detailed vulnerability reports
- [ ] Integration with CI/CD pipelines
- [ ] Custom rule creation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

---

**Author**: Kussagra Pathak

**Last Updated**: November 2025
