from setuptools import setup, find_packages

setup(
    name="code-analyzer",
    version="1.0.0",
    description="A multi-language code analysis tool for detecting vulnerabilities and code quality issues",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        # Core dependencies
        "pyyaml>=6.0",           # Configuration handling
        
        # Python analysis
        "ast>=0.8.1",            # Python AST parsing
        "astor>=0.8.1",          # Python code generation
        "pylint>=2.17.0",        # Python linting
        "black>=23.3.0",         # Python code formatting
        
        # JavaScript analysis
        "esprima>=4.0.1",        # JavaScript parsing
        "escodegen>=2.1.0",      # JavaScript code generation
        "eslint-plugin>=0.1.0",  # JavaScript linting
        
        # Java analysis
        "javalang>=0.13.0",      # Java parsing
        
        # General utilities
        "typing>=3.7.4",         # Type hints
        "pathlib>=1.0.1",        # Path manipulation
        "regex>=2023.5.5",       # Advanced regular expressions
        
        # Optional AI features
        "transformers>=4.30.0",  # AI-powered analysis
        "torch>=2.0.0",          # Deep learning support
    ],
    extras_require={
        'dev': [
            'pytest>=7.3.1',
            'pytest-cov>=4.1.0',
            'black>=23.3.0',
            'isort>=5.12.0',
            'mypy>=1.4.1',
        ]
    },
    entry_points={
        'console_scripts': [
            'code-analyzer=core.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Quality Assurance',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
)
