"""
Quality rules for Python code analysis.
"""
import ast
from typing import List, Dict
import re
from detectors.rule_engine import BaseRule

class ComplexityRule(BaseRule):
    """Check code complexity using cyclomatic complexity."""
    
    def __init__(self, config):
        super().__init__(config)
        self.max_complexity = 10

    def analyze(self, content: str) -> List[Dict]:
        issues = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    complexity = self._calculate_complexity(node)
                    if complexity > self.max_complexity:
                        issues.append({
                            'message': f'Function {node.name} has high cyclomatic complexity ({complexity})',
                            'line': node.lineno,
                            'severity': 'high',
                            'type': 'quality',
                            'fix': 'Consider breaking down the function into smaller functions'
                        })
        except Exception as e:
            print(f"Error in complexity analysis: {str(e)}")
        return issues

    def _calculate_complexity(self, node) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor,
                               ast.ExceptHandler, ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

class StyleRule(BaseRule):
    """Check Python code style against PEP 8 guidelines."""
    
    def analyze(self, content: str) -> List[Dict]:
        issues = []
        
        # Check line length
        for i, line in enumerate(content.splitlines(), 1):
            if len(line) > 79:
                issues.append({
                    'message': 'Line too long (exceeds 79 characters)',
                    'line': i,
                    'severity': 'low',
                    'type': 'quality',
                    'fix': 'Break the line into multiple lines'
                })

        # Check function/variable naming
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                    issues.append({
                        'message': f'Function name "{node.name}" does not follow snake_case convention',
                        'line': node.lineno,
                        'severity': 'low',
                        'type': 'quality',
                        'fix': f'Rename to {self._to_snake_case(node.name)}'
                    })
                    
        return issues

    def _to_snake_case(self, name: str) -> str:
        """Convert a name to snake_case."""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

class MaintainabilityRule(BaseRule):
    """Check code maintainability issues."""
    
    def analyze(self, content: str) -> List[Dict]:
        issues = []
        tree = ast.parse(content)
        
        # Check for large functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                body_lines = len(node.body)
                if body_lines > 50:
                    issues.append({
                        'message': f'Function {node.name} is too large ({body_lines} lines)',
                        'line': node.lineno,
                        'severity': 'medium',
                        'type': 'quality',
                        'fix': 'Split the function into smaller, more focused functions'
                    })

        # Check for too many function arguments
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                args_count = len(node.args.args)
                if args_count > 5:
                    issues.append({
                        'message': f'Function {node.name} has too many parameters ({args_count})',
                        'line': node.lineno,
                        'severity': 'medium',
                        'type': 'quality',
                        'fix': 'Consider using a class or data structure to group related parameters'
                    })

        return issues
