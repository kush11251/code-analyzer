"""
Java language support initialization.
"""
from languages.java.parser import JavaParser
from languages.java.fixer import JavaFixer
from languages.java.rules_quality import ComplexityRule, StyleRule, DesignRule
from languages.java.rules_security import InjectionRule, AuthenticationRule, ValidationRule

__all__ = [
    'JavaParser',
    'JavaFixer',
    'ComplexityRule',
    'StyleRule',
    'DesignRule',
    'InjectionRule',
    'AuthenticationRule',
    'ValidationRule'
]
