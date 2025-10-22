"""
Security rules for Java code analysis.
"""
from typing import List, Dict
import javalang
from detectors.rule_engine import BaseRule

class InjectionRule(BaseRule):
    """Detect potential injection vulnerabilities in Java code."""
    
    def __init__(self, config):
        super().__init__(config)
        self.severity = 'critical'
        self.rule_type = 'security'

    def analyze(self, content: str) -> List[Dict]:
        issues = []
        try:
            tree = javalang.parse.parse(content)
            self._check_sql_injection(tree, issues)
            self._check_command_injection(tree, issues)
        except Exception as e:
            print(f"Error in Java injection analysis: {str(e)}")
        return issues

    def _check_sql_injection(self, tree, issues: List[Dict]) -> None:
        """Check for SQL injection vulnerabilities."""
        for _, node in tree.filter(javalang.tree.MethodInvocation):
            # Check for direct string concatenation in SQL queries
            if node.member in ['executeQuery', 'executeUpdate', 'execute']:
                if self._has_string_concatenation(node.arguments):
                    issues.append({
                        'message': 'Potential SQL injection vulnerability',
                        'line': node.position[0] if node.position else 0,
                        'severity': 'critical',
                        'type': 'security',
                        'fix': 'Use PreparedStatement instead of string concatenation'
                    })

    def _check_command_injection(self, tree, issues: List[Dict]) -> None:
        """Check for command injection vulnerabilities."""
        for _, node in tree.filter(javalang.tree.MethodInvocation):
            if (node.qualifier == 'Runtime' and node.member == 'exec') or \
               (node.member in ['exec', 'start'] and 'Process' in str(node.qualifier)):
                issues.append({
                    'message': 'Potential command injection vulnerability',
                    'line': node.position[0] if node.position else 0,
                    'severity': 'critical',
                    'type': 'security',
                    'fix': 'Use ProcessBuilder with proper argument validation'
                })

    def _has_string_concatenation(self, args) -> bool:
        """Check if arguments contain string concatenation."""
        for arg in args:
            if isinstance(arg, javalang.tree.BinaryOperation) and arg.operator == '+':
                return True
        return False

class AuthenticationRule(BaseRule):
    """Check for authentication and authorization related security issues."""
    
    def __init__(self, config):
        super().__init__(config)
        self.severity = 'high'
        self.rule_type = 'security'

    def analyze(self, content: str) -> List[Dict]:
        issues = []
        try:
            tree = javalang.parse.parse(content)
            self._check_auth_issues(tree, issues)
        except Exception as e:
            print(f"Error in Java authentication analysis: {str(e)}")
        return issues

    def _check_auth_issues(self, tree, issues: List[Dict]) -> None:
        """Check for authentication and authorization issues."""
        # Check for hardcoded credentials
        for _, node in tree.filter(javalang.tree.FieldDeclaration):
            for declarator in node.declarators:
                if any(cred in declarator.name.lower() for cred in ['password', 'secret', 'key']):
                    if hasattr(declarator, 'initializer') and declarator.initializer:
                        issues.append({
                            'message': f'Hardcoded credential found in field {declarator.name}',
                            'line': node.position[0] if node.position else 0,
                            'severity': 'critical',
                            'type': 'security',
                            'fix': 'Use secure configuration management'
                        })

        # Check for weak encryption
        for _, node in tree.filter(javalang.tree.ClassCreator):
            if 'MD5' in str(node.type) or 'SHA1' in str(node.type):
                issues.append({
                    'message': 'Weak cryptographic algorithm detected',
                    'line': node.position[0] if node.position else 0,
                    'severity': 'high',
                    'type': 'security',
                    'fix': 'Use strong cryptographic algorithms (e.g., SHA-256, SHA-3)'
                })

class ValidationRule(BaseRule):
    """Check for proper input validation and sanitization."""
    
    def __init__(self, config):
        super().__init__(config)
        self.severity = 'high'
        self.rule_type = 'security'

    def analyze(self, content: str) -> List[Dict]:
        issues = []
        try:
            tree = javalang.parse.parse(content)
            self._check_validation_issues(tree, issues)
        except Exception as e:
            print(f"Error in Java validation analysis: {str(e)}")
        return issues

    def _check_validation_issues(self, tree, issues: List[Dict]) -> None:
        """Check for input validation issues."""
        # Check for proper file path validation
        for _, node in tree.filter(javalang.tree.ClassCreator):
            if 'File' in str(node.type) or 'Path' in str(node.type):
                if not self._has_path_validation(node):
                    issues.append({
                        'message': 'File path used without proper validation',
                        'line': node.position[0] if node.position else 0,
                        'severity': 'high',
                        'type': 'security',
                        'fix': 'Validate and sanitize file paths before use'
                    })

        # Check for proper deserialization
        for _, node in tree.filter(javalang.tree.MethodInvocation):
            if node.member in ['readObject', 'fromXML', 'unmarshal']:
                issues.append({
                    'message': 'Potentially unsafe deserialization',
                    'line': node.position[0] if node.position else 0,
                    'severity': 'high',
                    'type': 'security',
                    'fix': 'Implement proper validation before deserialization'
                })

    def _has_path_validation(self, node) -> bool:
        """Check if there's path validation before file operations."""
        # This is a simplified check - in real implementation,
        # you'd want to do more sophisticated analysis
        return False
