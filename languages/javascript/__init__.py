"""
JavaScript language support initialization.
"""
from languages.javascript.parser import JavaScriptParser
from languages.javascript.fixer import JavaScriptFixer
from languages.javascript.rules_quality import ComplexityRule, StyleRule, BestPracticesRule
from languages.javascript.rules_security import XSSRule, InjectionRule, AuthenticationRule

__all__ = [
    'JavaScriptParser',
    'JavaScriptFixer',
    'ComplexityRule',
    'StyleRule',
    'BestPracticesRule',
    'InjectionRule',
    'AuthenticationRule',
    'SecurityHeadersRule'
]
