"""
Quality rules for JavaScript code analysis.
"""
import re
from typing import List, Dict
import esprima
from detectors.rule_engine import BaseRule

class ComplexityRule(BaseRule):
    """Check JavaScript code complexity."""
    
    def __init__(self, config):
        super().__init__(config)
        self.max_complexity = 10

    def analyze(self, content: str) -> List[Dict]:
        issues = []
        try:
            tree = esprima.parseScript(content, {'loc': True})
            self._check_complexity(tree, issues)
        except Exception as e:
            print(f"Error in JavaScript complexity analysis: {str(e)}")
        return issues

    def _check_complexity(self, node: dict, issues: List[Dict]) -> int:
        """Recursively check code complexity."""
        if not isinstance(node, dict):
            return 0

        complexity = 0
        
        # Check function declarations and expressions
        if node.get('type') in ['FunctionDeclaration', 'FunctionExpression', 'ArrowFunctionExpression']:
            name = node.get('id', {}).get('name', 'anonymous')
            func_complexity = self._calculate_complexity(node)
            
            if func_complexity > self.max_complexity:
                issues.append({
                    'message': f'Function {name} has high cyclomatic complexity ({func_complexity})',
                    'line': node['loc']['start']['line'],
                    'severity': 'high',
                    'type': 'quality',
                    'fix': 'Consider breaking down the function into smaller functions'
                })

        # Recursively check all properties
        for key, value in node.items():
            if isinstance(value, (dict, list)):
                if isinstance(value, dict):
                    complexity += self._check_complexity(value, issues)
                else:
                    for item in value:
                        if isinstance(item, dict):
                            complexity += self._check_complexity(item, issues)

        return complexity

    def _calculate_complexity(self, node: dict) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity
        
        def traverse(node):
            nonlocal complexity
            if not isinstance(node, dict):
                return
                
            # Increment complexity for control flow statements
            if node.get('type') in [
                'IfStatement', 'WhileStatement', 'DoWhileStatement', 
                'ForStatement', 'ForInStatement', 'ForOfStatement',
                'ConditionalExpression', 'SwitchCase', 'CatchClause'
            ]:
                complexity += 1
            
            # Handle logical operators
            elif node.get('type') == 'LogicalExpression':
                complexity += 1
                
            # Recursively traverse all properties
            for key, value in node.items():
                if isinstance(value, (dict, list)):
                    if isinstance(value, dict):
                        traverse(value)
                    else:
                        for item in value:
                            if isinstance(item, dict):
                                traverse(item)
        
        traverse(node)
        return complexity

class StyleRule(BaseRule):
    """Check JavaScript code style."""
    
    def __init__(self, config):
        super().__init__(config)
        self.max_line_length = 80

    def analyze(self, content: str) -> List[Dict]:
        issues = []
        
        # Check line length
        for i, line in enumerate(content.splitlines(), 1):
            if len(line) > self.max_line_length:
                issues.append({
                    'message': f'Line exceeds {self.max_line_length} characters',
                    'line': i,
                    'severity': 'low',
                    'type': 'quality',
                    'fix': 'Break the line into multiple lines'
                })

        try:
            tree = esprima.parseScript(content, {'loc': True})
            self._check_naming_conventions(tree, issues)
        except Exception as e:
            print(f"Error in JavaScript style analysis: {str(e)}")

        return issues

    def _check_naming_conventions(self, node: dict, issues: List[Dict]) -> None:
        """Check naming conventions in the code."""
        if not isinstance(node, dict):
            return

        # Check variable declarations
        if node.get('type') == 'VariableDeclarator':
            name = node.get('id', {}).get('name')
            if name:
                if not self._is_valid_variable_name(name):
                    issues.append({
                        'message': f'Variable name "{name}" does not follow camelCase convention',
                        'line': node['loc']['start']['line'],
                        'severity': 'low',
                        'type': 'quality',
                        'fix': f'Rename to {self._to_camel_case(name)}'
                    })

        # Check function declarations
        elif node.get('type') == 'FunctionDeclaration':
            name = node.get('id', {}).get('name')
            if name and not self._is_valid_function_name(name):
                issues.append({
                    'message': f'Function name "{name}" does not follow camelCase convention',
                    'line': node['loc']['start']['line'],
                    'severity': 'low',
                    'type': 'quality',
                    'fix': f'Rename to {self._to_camel_case(name)}'
                })

        # Recursively check all properties
        for key, value in node.items():
            if isinstance(value, (dict, list)):
                if isinstance(value, dict):
                    self._check_naming_conventions(value, issues)
                else:
                    for item in value:
                        if isinstance(item, dict):
                            self._check_naming_conventions(item, issues)

    def _is_valid_variable_name(self, name: str) -> bool:
        """Check if variable name follows camelCase convention."""
        return re.match(r'^[a-z][a-zA-Z0-9]*$', name) is not None

    def _is_valid_function_name(self, name: str) -> bool:
        """Check if function name follows camelCase convention."""
        return re.match(r'^[a-z][a-zA-Z0-9]*$', name) is not None

    def _to_camel_case(self, name: str) -> str:
        """Convert a name to camelCase."""
        components = name.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

class BestPracticesRule(BaseRule):
    """Check JavaScript best practices."""
    
    def analyze(self, content: str) -> List[Dict]:
        issues = []
        try:
            tree = esprima.parseScript(content, {'loc': True})
            self._check_best_practices(tree, issues)
        except Exception as e:
            print(f"Error in JavaScript best practices analysis: {str(e)}")
        return issues

    def _check_best_practices(self, node: dict, issues: List[Dict]) -> None:
        """Check for JavaScript best practices violations."""
        if not isinstance(node, dict):
            return

        # Check for use of == instead of ===
        if node.get('type') == 'BinaryExpression':
            if node.get('operator') == '==':
                issues.append({
                    'message': 'Use === instead of == for comparison',
                    'line': node['loc']['start']['line'],
                    'severity': 'medium',
                    'type': 'quality',
                    'fix': 'Replace == with ==='
                })

        # Check for console.log statements
        if (node.get('type') == 'CallExpression' and
            node.get('callee', {}).get('type') == 'MemberExpression' and
            node.get('callee', {}).get('object', {}).get('name') == 'console'):
            issues.append({
                'message': 'Avoid using console.log in production code',
                'line': node['loc']['start']['line'],
                'severity': 'low',
                'type': 'quality',
                'fix': 'Remove console.log or replace with proper logging'
            })

        # Check for var usage
        if node.get('type') == 'VariableDeclaration':
            if node.get('kind') == 'var':
                issues.append({
                    'message': 'Use let or const instead of var',
                    'line': node['loc']['start']['line'],
                    'severity': 'medium',
                    'type': 'quality',
                    'fix': 'Replace var with let or const'
                })

        # Recursively check all properties
        for key, value in node.items():
            if isinstance(value, (dict, list)):
                if isinstance(value, dict):
                    self._check_best_practices(value, issues)
                else:
                    for item in value:
                        if isinstance(item, dict):
                            self._check_best_practices(item, issues)
