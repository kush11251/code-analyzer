"""
Security rules for JavaScript code analysis.
"""
import esprima
from typing import List, Dict
import re
from detectors.rule_engine import BaseRule

class InjectionRule(BaseRule):
    """Detect potential injection vulnerabilities in JavaScript code."""
    
    def __init__(self, config):
        super().__init__(config)
        self.severity = 'critical'
        self.rule_type = 'security'

    def analyze(self, content: str) -> List[Dict]:
        issues = []
        try:
            tree = esprima.parseScript(content, {'loc': True})
            self._check_injections(tree, issues)
        except Exception as e:
            print(f"Error in JavaScript injection analysis: {str(e)}")
        return issues

    def _check_injections(self, node: dict, issues: List[Dict]) -> None:
        """Check for potential injection vulnerabilities."""
        if not isinstance(node, dict):
            return

        # Check for eval usage
        if (node.get('type') == 'CallExpression' and
            node.get('callee', {}).get('name') == 'eval'):
            issues.append({
                'message': 'Dangerous use of eval detected',
                'line': node['loc']['start']['line'],
                'severity': 'critical',
                'type': 'security',
                'fix': 'Avoid using eval, use safer alternatives'
            })

        # Check for innerHTML assignments
        if (node.get('type') == 'AssignmentExpression' and
            node.get('left', {}).get('property', {}).get('name') == 'innerHTML'):
            issues.append({
                'message': 'Potential XSS vulnerability: innerHTML assignment',
                'line': node['loc']['start']['line'],
                'severity': 'high',
                'type': 'security',
                'fix': 'Use textContent or sanitize HTML content'
            })

        # Check for dangerous DOM methods
        if node.get('type') == 'CallExpression':
            callee = node.get('callee', {})
            if (callee.get('type') == 'MemberExpression' and
                callee.get('property', {}).get('name') in ['insertAdjacentHTML', 'write', 'writeln']):
                issues.append({
                    'message': f'Potential XSS vulnerability: Using {callee["property"]["name"]}',
                    'line': node['loc']['start']['line'],
                    'severity': 'high',
                    'type': 'security',
                    'fix': 'Use safer DOM manipulation methods'
                })

        # Recursively check all properties
        for key, value in node.items():
            if isinstance(value, (dict, list)):
                if isinstance(value, dict):
                    self._check_injections(value, issues)
                else:
                    for item in value:
                        if isinstance(item, dict):
                            self._check_injections(item, issues)

class AuthenticationRule(BaseRule):
    """Check for authentication and authorization related security issues."""
    
    def __init__(self, config):
        super().__init__(config)
        self.severity = 'high'
        self.rule_type = 'security'

    def analyze(self, content: str) -> List[Dict]:
        issues = []
        try:
            tree = esprima.parseScript(content, {'loc': True})
            self._check_auth_issues(tree, issues)
        except Exception as e:
            print(f"Error in JavaScript authentication analysis: {str(e)}")
        return issues

    def _check_auth_issues(self, node: dict, issues: List[Dict]) -> None:
        """Check for authentication and authorization issues."""
        if not isinstance(node, dict):
            return

        # Check for hardcoded credentials
        if node.get('type') == 'VariableDeclarator':
            name = node.get('id', {}).get('name', '').lower()
            if any(cred in name for cred in ['password', 'secret', 'key', 'token']):
                if node.get('init', {}).get('type') == 'Literal':
                    issues.append({
                        'message': f'Hardcoded credential found in variable {name}',
                        'line': node['loc']['start']['line'],
                        'severity': 'critical',
                        'type': 'security',
                        'fix': 'Use environment variables or secure configuration management'
                    })

        # Check for insecure authentication methods
        if (node.get('type') == 'CallExpression' and
            node.get('callee', {}).get('property', {}).get('name') == 'setItem'):
            args = node.get('arguments', [])
            if len(args) >= 2 and isinstance(args[0], dict):
                key = args[0].get('value', '')
                if any(auth in key.lower() for auth in ['token', 'auth', 'session']):
                    issues.append({
                        'message': 'Sensitive authentication data stored in localStorage',
                        'line': node['loc']['start']['line'],
                        'severity': 'high',
                        'type': 'security',
                        'fix': 'Use secure storage methods for authentication data'
                    })

        # Recursively check all properties
        for key, value in node.items():
            if isinstance(value, (dict, list)):
                if isinstance(value, dict):
                    self._check_auth_issues(value, issues)
                else:
                    for item in value:
                        if isinstance(item, dict):
                            self._check_auth_issues(item, issues)

class SecurityHeadersRule(BaseRule):
    """Check for security headers and configurations."""
    
    def __init__(self, config):
        super().__init__(config)
        self.severity = 'high'
        self.rule_type = 'security'

    def analyze(self, content: str) -> List[Dict]:
        issues = []
        try:
            tree = esprima.parseScript(content, {'loc': True})
            self._check_security_headers(tree, issues)
        except Exception as e:
            print(f"Error in JavaScript security headers analysis: {str(e)}")
        return issues

    def _check_security_headers(self, node: dict, issues: List[Dict]) -> None:
        """Check for security header related issues."""
        if not isinstance(node, dict):
            return

        # Check for CORS configuration
        if (node.get('type') == 'CallExpression' and
            node.get('callee', {}).get('property', {}).get('name') == 'setRequestHeader'):
            args = node.get('arguments', [])
            if len(args) >= 2 and isinstance(args[0], dict):
                header_name = args[0].get('value', '').lower()
                if header_name == 'origin' or 'cors' in header_name:
                    issues.append({
                        'message': 'Review CORS configuration for security',
                        'line': node['loc']['start']['line'],
                        'severity': 'medium',
                        'type': 'security',
                        'fix': 'Ensure CORS is properly configured with specific origins'
                    })

        # Check for Content Security Policy
        if (node.get('type') == 'CallExpression' and
            node.get('callee', {}).get('property', {}).get('name') == 'setRequestHeader'):
            args = node.get('arguments', [])
            if len(args) >= 2 and isinstance(args[0], dict):
                header_name = args[0].get('value', '').lower()
                if 'content-security-policy' in header_name:
                    value = args[1].get('value', '')
                    if 'unsafe-inline' in value or 'unsafe-eval' in value:
                        issues.append({
                            'message': 'Unsafe CSP directives detected',
                            'line': node['loc']['start']['line'],
                            'severity': 'high',
                            'type': 'security',
                            'fix': 'Remove unsafe-inline and unsafe-eval from CSP'
                        })

        # Recursively check all properties
        for key, value in node.items():
            if isinstance(value, (dict, list)):
                if isinstance(value, dict):
                    self._check_security_headers(value, issues)
                else:
                    for item in value:
                        if isinstance(item, dict):
                            self._check_security_headers(item, issues)
