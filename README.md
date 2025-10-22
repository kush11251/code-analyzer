# Code Analyzer

A powerful, multi-language code analysis tool for detecting vulnerabilities, assessing code quality, and suggesting improvements. The tool combines traditional static analysis with AI-powered insights to provide comprehensive code quality and security assessments.

## Features

- **Multi-Language Support**: Currently supports Python, JavaScript, and Java with language-specific analyzers
- **Code Quality Analysis**: Detects code smells, complexity issues, and style violations
- **Security Vulnerability Detection**: Identifies common security vulnerabilities and suggests fixes
- **Code Structure Analysis**: Analyzes code organization and suggests architectural improvements
- **Extensible Rule Engine**: Custom rules can be added through plugins
- **AI-Powered Analysis**: Uses AI to provide intelligent code improvement suggestions
- **Automated Fixes**: Provides automatic fix suggestions for common issues
- **Integration Support**: Connects with GitHub and other development platforms
- **User-Friendly GUI**: Easy-to-use graphical interface for file/folder selection and analysis
- **Multiple Report Formats**: Generates reports in HTML, Markdown, and JSON formats

## Project Structure

```
code-analyzer/
├── core/                     # Core functionality
│   ├── config.py            # Configuration management
│   ├── main.py             # Main entry point
│   └── utils/              # Utility functions
│       └── logger.py       # Logging setup
├── detectors/               # Analysis engines
│   ├── ai_engine.py        # AI-based analysis
│   ├── language_detector.py # Language detection
│   └── rule_engine.py      # Rule processing engine
├── languages/              # Language-specific modules
│   ├── java/              # Java analysis
│   ├── javascript/        # JavaScript analysis
│   └── python/           # Python analysis
├── plugins/               # Extensibility support
│   ├── custom_rules/     # Custom rule definitions
│   └── external_integrations/  # External service integrations
├── reports/              # Report generation
│   ├── report_builder.py # Report generation logic
│   └── templates/       # Report templates
└── ui/                  # User interface
    ├── analyzer_window.py  # Main application window
    └── selector.py       # File/folder selector
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/kush11251/code-analyzer.git
cd code-analyzer
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Configure the tool:
   - Copy `.env.example` to `.env`
   - Update OpenAI API key and other settings in `.env`
   - (Optional) Create a custom configuration at `~/.code_analyzer/config.yml`

## Usage

### Graphical User Interface

1. Launch the GUI:
```bash
python analyze_gui.py
```

2. Using the GUI:
   - Click "Add File" or "Add Folder" to select items to analyze
   - Selected files/folders appear in the list
   - Click "Analyze Selected" to start analysis
   - View results in the Results tab, sorted by severity and type

### Command Line Interface

```bash
# Basic usage
python -m core.main /path/to/project

# With custom config
python -m core.main --config /path/to/config.yml /path/to/project

# Specify output format
python -m core.main --format html /path/to/project
```

### Python API
```python
from core.main import CodeAnalyzer

# Initialize the analyzer with default config
analyzer = CodeAnalyzer()

# With custom config
analyzer = CodeAnalyzer("/path/to/config.yml")

# Analyze a project
results = analyzer.analyze_project("/path/to/project")

# Generate report (format based on config)
analyzer.generate_report(results, "report.html")

# Access specific results
print(f"Total files analyzed: {results['summary']['analyzed_files']}")
print(f"Total issues found: {results['summary']['total_issues']}")

# Get AI insights (if enabled)
if 'ai_insights' in results:
    print("AI Recommendations:", results['ai_insights'])
```

## Language Support

### Python
- Syntax validation
- PEP 8 compliance
- Security vulnerabilities
- Code complexity analysis
- Type checking

### JavaScript
- ESLint integration
- Security best practices
- Code quality metrics
- Performance analysis
- Modern JS features usage

### Java
- Code style checking
- Security vulnerabilities
- Performance optimization
- Design patterns analysis
- Best practices validation

## Configuration

### Environment Variables (.env)
```
OPENAI_API_KEY=your_api_key_here
LOG_LEVEL=INFO
LOG_FILE=code_analyzer.log
```

### User Configuration (config.yml)
```yaml
languages:
  python:
    enabled: true
    extensions: ['.py']
    ignore_patterns: ['*venv*', '*.pyc']
  javascript:
    enabled: true
    extensions: ['.js', '.jsx', '.ts', '.tsx']
    ignore_patterns: ['node_modules']
  java:
    enabled: true
    extensions: ['.java']
    ignore_patterns: ['target']

analysis:
  max_file_size: 1048576  # 1MB
  parallel_processing: true
  max_workers: 4

ai_assistance:
  enabled: true
  model: gpt-4
  confidence_threshold: 0.8
```

## Extending the Tool

### Adding Custom Rules
Create new rules in `plugins/custom_rules/`:

```python
from detectors.rule_engine import BaseRule

class MyCustomRule(BaseRule):
    def __init__(self, config):
        super().__init__(config)
        self.languages = ['python', 'javascript']  # Supported languages
        
    def analyze(self, content):
        issues = []
        # Implement your analysis logic here
        return issues
```

### External Integrations

The tool supports integration with external services through the plugins system. Current integrations:

- GitHub: Analyze repositories and create issues
- More integrations can be added in `plugins/external_integrations/`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Write/update tests
5. Run tests and ensure they pass
6. Submit a Pull Request

## License

MIT License - See LICENSE file for details
