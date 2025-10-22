"""
Security rules for Python code analysis.
"""
import ast
from typing import List, Dict
import re
from detectors.rule_engine import BaseRule

class InjectionRule(BaseRule):
    """Detect potential SQL injection and command injection vulnerabilities."""
    
    def __init__(self, config):
        super().__init__(config)
        self.severity = 'critical'
        self.rule_type = 'security'

    def analyze(self, content: str) -> List[Dict]:
        issues = []
        tree = ast.parse(content)

        # Check for SQL injection vulnerabilities
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for direct string formatting in SQL queries
                if self._is_sql_query(node):
                    if self._has_string_formatting(node):
                        issues.append({
                            'message': 'Potential SQL injection vulnerability detected',
                            'line': node.lineno,
                            'severity': 'critical',
                            'type': 'security',
                            'fix': 'Use parameterized queries or an ORM instead of string formatting'
                        })

            # Check for command injection vulnerabilities
            if self._is_shell_command(node):
                if self._has_dynamic_input(node):
                    issues.append({
                        'message': 'Potential command injection vulnerability detected',
                        'line': node.lineno,
                        'severity': 'critical',
                        'type': 'security',
                        'fix': 'Use subprocess module with shell=False and proper argument passing'
                    })

        return issues

    def _is_sql_query(self, node: ast.Call) -> bool:
        """Check if the call is likely a SQL query."""
        if isinstance(node.func, ast.Attribute):
            return node.func.attr in ['execute', 'executemany', 'raw']
        return False

    def _has_string_formatting(self, node: ast.Call) -> bool:
        """Check if string formatting is used in the call."""
        for arg in node.args:
            if isinstance(arg, (ast.BinOp, ast.Call)):
                if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Mod):
                    return True
                if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Attribute):
                    if arg.func.attr in ['format', 'replace']:
                        return True
        return False

    def _is_shell_command(self, node: ast.Call) -> bool:
        """Check if the call is executing shell commands."""
        if isinstance(node.func, ast.Name):
            return node.func.id in ['system', 'popen', 'call', 'run']
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr in ['system', 'popen', 'call', 'run']
        return False

    def _has_dynamic_input(self, node: ast.Call) -> bool:
        """Check if the command includes dynamic input."""
        for arg in node.args:
            if not isinstance(arg, ast.Str):
                return True
        return False

class AuthenticationRule(BaseRule):
    """Check for common authentication and authorization issues."""
    
    def __init__(self, config):
        super().__init__(config)
        self.severity = 'high'
        self.rule_type = 'security'

    def analyze(self, content: str) -> List[Dict]:
        issues = []
        tree = ast.parse(content)

        # Check for hardcoded credentials
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id.lower()
                        if any(cred in var_name for cred in ['password', 'secret', 'key', 'token']):
                            if isinstance(node.value, ast.Str):
                                issues.append({
                                    'message': f'Hardcoded credential found in variable {target.id}',
                                    'line': node.lineno,
                                    'severity': 'critical',
                                    'type': 'security',
                                    'fix': 'Use environment variables or a secure configuration system'
                                })

        # Check for weak password handling
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if self._is_password_hash(node):
                    if not self._is_secure_hash(node):
                        issues.append({
                            'message': 'Weak password hashing detected',
                            'line': node.lineno,
                            'severity': 'high',
                            'type': 'security',
                            'fix': 'Use strong password hashing algorithms like bcrypt or Argon2'
                        })

        return issues

    def _is_password_hash(self, node: ast.Call) -> bool:
        """Check if the call is related to password hashing."""
        if isinstance(node.func, ast.Name):
            return node.func.id in ['md5', 'sha1']
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr in ['md5', 'sha1']
        return False

    def _is_secure_hash(self, node: ast.Call) -> bool:
        """Check if a secure hashing algorithm is used."""
        if isinstance(node.func, ast.Name):
            return node.func.id in ['pbkdf2_hmac', 'argon2', 'bcrypt']
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr in ['pbkdf2_hmac', 'argon2', 'bcrypt']
        return False

class DataValidationRule(BaseRule):
    """Check for proper data validation and sanitization."""
    
    def __init__(self, config):
        super().__init__(config)
        self.severity = 'high'
        self.rule_type = 'security'

    def analyze(self, content: str) -> List[Dict]:
        issues = []
        tree = ast.parse(content)

        # Check for proper input validation
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check file operations
                if self._is_file_operation(node):
                    if not self._has_path_validation(node):
                        issues.append({
                            'message': 'File operation without path validation',
                            'line': node.lineno,
                            'severity': 'high',
                            'type': 'security',
                            'fix': 'Validate and sanitize file paths before operations'
                        })

                # Check deserialization
                if self._is_deserialization(node):
                    if not self._has_input_validation(node):
                        issues.append({
                            'message': 'Unsafe deserialization of data',
                            'line': node.lineno,
                            'severity': 'high',
                            'type': 'security',
                            'fix': 'Validate and sanitize input before deserialization'
                        })

        return issues

    def _is_file_operation(self, node: ast.Call) -> bool:
        """Check if the call is a file operation."""
        if isinstance(node.func, ast.Name):
            return node.func.id in ['open', 'read', 'write']
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr in ['open', 'read', 'write']
        return False

    def _has_path_validation(self, node: ast.Call) -> bool:
        """Check if there's path validation before the operation."""
        # This is a simplified check - in real implementation,
        # you'd want to do more sophisticated analysis
        return False

    def _is_deserialization(self, node: ast.Call) -> bool:
        """Check if the call is deserializing data."""
        if isinstance(node.func, ast.Name):
            return node.func.id in ['loads', 'load', 'pickle']
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr in ['loads', 'load', 'pickle']
        return False

    def _has_input_validation(self, node: ast.Call) -> bool:
        """Check if there's input validation before deserialization."""
        # This is a simplified check - in real implementation,
        # you'd want to do more sophisticated analysis
        return False
