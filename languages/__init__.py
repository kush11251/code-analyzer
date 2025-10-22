"""
Languages package initialization.
"""
from languages.python.parser import PythonParser
from languages.python.fixer import PythonFixer
from languages.python.rules_quality import ComplexityRule as PythonComplexityRule
from languages.python.rules_security import InjectionRule as PythonInjectionRule

from languages.javascript.parser import JavaScriptParser
from languages.javascript.fixer import JavaScriptFixer
from languages.javascript.rules_quality import ComplexityRule as JSComplexityRule
from languages.javascript.rules_security import XSSRule as JSXSSRule

from languages.java.parser import JavaParser
from languages.java.fixer import JavaFixer
from languages.java.rules_quality import ComplexityRule as JavaComplexityRule
from languages.java.rules_security import InjectionRule as JavaInjectionRule

__all__ = [
    # Python
    'PythonParser', 'PythonFixer', 'PythonComplexityRule', 'PythonInjectionRule',
    # JavaScript
    'JavaScriptParser', 'JavaScriptFixer', 'JSComplexityRule', 'JSXSSRule',
    # Java
    'JavaParser', 'JavaFixer', 'JavaComplexityRule', 'JavaInjectionRule'
]

__all__ = [
    'PythonParser', 'PythonFixer',
    'JavaScriptParser', 'JavaScriptFixer',
    'JavaParser', 'JavaFixer'
]
