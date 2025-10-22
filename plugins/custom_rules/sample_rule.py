"""
Sample custom rule implementation.
"""
from typing import Dict, List, Optional

from detectors.rule_engine import BaseRule

class CustomRule(BaseRule):
    """
    Example custom rule that checks for potentially dangerous function calls.
    """
    def __init__(self, config):
        super().__init__(config)
        self.languages = ['python', 'javascript']  # This rule supports Python and JavaScript
        self.dangerous_functions = {
            'python': ['eval', 'exec', 'pickle.loads', 'subprocess.call'],
            'javascript': ['eval', 'Function', 'document.write', 'innerHTML']
        }
    
    def analyze(self, content: str) -> List[Dict]:
        """
        Analyze code for dangerous function calls.
        
        Args:
            content: Source code to analyze
            
        Returns:
            List of issues found
        """
        issues = []
        
        # Get dangerous functions for the current language
        dangerous_funcs = self.dangerous_functions.get(self.current_language, [])
        
        # Simple line-by-line analysis
        for line_num, line in enumerate(content.split('\n'), 1):
            for func in dangerous_funcs:
                if func in line:
                    issues.append({
                        'line': line_num,
                        'message': f'Potentially dangerous function call: {func}',
                        'severity': 'high',
                        'type': 'security',
                        'rule': 'custom_dangerous_calls',
                        'fix_suggestion': f'Consider using a safer alternative to {func}'
                    })
        
        return issues

class SecurityHeaderRule(BaseRule):
    """
    Custom rule to check for security headers in web applications.
    """
    def __init__(self, config):
        super().__init__(config)
        self.languages = ['python', 'javascript']
        self.required_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'Content-Security-Policy': None,
            'Strict-Transport-Security': None
        }
    
    def analyze(self, content: str) -> List[Dict]:
        issues = []
        found_headers = set()
        
        # Look for header definitions
        for line_num, line in enumerate(content.split('\n'), 1):
            for header in self.required_headers:
                if header in line:
                    found_headers.add(header)
        
        # Report missing headers
        missing_headers = set(self.required_headers.keys()) - found_headers
        if missing_headers:
            issues.append({
                'line': 1,
                'message': f'Missing security headers: {", ".join(missing_headers)}',
                'severity': 'medium',
                'type': 'security',
                'rule': 'custom_security_headers',
                'fix_suggestion': 'Add the missing security headers to protect against common web vulnerabilities'
            })
        
        return issues

class LoggingRule(BaseRule):
    """
    Custom rule to enforce proper logging practices.
    """
    def __init__(self, config):
        super().__init__(config)
        self.languages = ['python']
        self.required_log_levels = {'error', 'warning', 'info', 'debug'}
    
    def analyze(self, content: str) -> List[Dict]:
        issues = []
        found_levels = set()
        
        # Look for logging calls
        for line_num, line in enumerate(content.split('\n'), 1):
            if 'logger.' in line:
                for level in self.required_log_levels:
                    if f'logger.{level}' in line:
                        found_levels.add(level)
        
        # Check for missing log levels
        if found_levels:  # Only check if the file uses logging
            missing_levels = self.required_log_levels - found_levels
            if missing_levels:
                issues.append({
                    'line': 1,
                    'message': f'Missing log levels: {", ".join(missing_levels)}',
                    'severity': 'low',
                    'type': 'maintainability',
                    'rule': 'custom_logging_levels',
                    'fix_suggestion': 'Consider adding different log levels for better debugging and monitoring'
                })
        
        return issues
