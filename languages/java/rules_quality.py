"""
Quality rules for Java code analysis.
"""
from typing import List, Dict
import javalang
from detectors.rule_engine import BaseRule

class ComplexityRule(BaseRule):
    """Check Java code complexity."""
    
    def __init__(self, config):
        super().__init__(config)
        self.max_complexity = 10

    def analyze(self, content: str) -> List[Dict]:
        issues = []
        try:
            tree = javalang.parse.parse(content)
            for _, node in tree.filter(javalang.tree.MethodDeclaration):
                complexity = self._calculate_complexity(node)
                if complexity > self.max_complexity:
                    issues.append({
                        'message': f'Method {node.name} has high cyclomatic complexity ({complexity})',
                        'line': node.position[0] if node.position else 0,
                        'severity': 'high',
                        'type': 'quality',
                        'fix': 'Consider breaking down the method into smaller methods'
                    })
        except Exception as e:
            print(f"Error in Java complexity analysis: {str(e)}")
        return issues

    def _calculate_complexity(self, node) -> int:
        """Calculate cyclomatic complexity of a method."""
        complexity = 1  # Base complexity

        # Count branching statements
        for _, child in node.filter((
            javalang.tree.IfStatement,
            javalang.tree.WhileStatement,
            javalang.tree.DoStatement,
            javalang.tree.ForStatement,
            javalang.tree.SwitchStatementCase,
            javalang.tree.CatchClause,
            javalang.tree.ConditionalExpression
        )):
            complexity += 1

        return complexity

class StyleRule(BaseRule):
    """Check Java code style."""
    
    def __init__(self, config):
        super().__init__(config)
        self.max_line_length = 100

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
            tree = javalang.parse.parse(content)
            self._check_naming_conventions(tree, issues)
        except Exception as e:
            print(f"Error in Java style analysis: {str(e)}")

        return issues

    def _check_naming_conventions(self, tree, issues: List[Dict]) -> None:
        """Check Java naming conventions."""
        # Check class names
        for _, node in tree.filter(javalang.tree.ClassDeclaration):
            if not self._is_valid_class_name(node.name):
                issues.append({
                    'message': f'Class name "{node.name}" should start with uppercase letter',
                    'line': node.position[0] if node.position else 0,
                    'severity': 'medium',
                    'type': 'quality',
                    'fix': f'Rename to {node.name.capitalize()}'
                })

        # Check method names
        for _, node in tree.filter(javalang.tree.MethodDeclaration):
            if not self._is_valid_method_name(node.name):
                issues.append({
                    'message': f'Method name "{node.name}" should start with lowercase letter',
                    'line': node.position[0] if node.position else 0,
                    'severity': 'medium',
                    'type': 'quality',
                    'fix': f'Rename to {node.name[0].lower() + node.name[1:]}'
                })

        # Check variable names
        for _, node in tree.filter(javalang.tree.LocalVariableDeclaration):
            for declarator in node.declarators:
                if not self._is_valid_variable_name(declarator.name):
                    issues.append({
                        'message': f'Variable name "{declarator.name}" should start with lowercase letter',
                        'line': node.position[0] if node.position else 0,
                        'severity': 'low',
                        'type': 'quality',
                        'fix': f'Rename to {declarator.name[0].lower() + declarator.name[1:]}'
                    })

    def _is_valid_class_name(self, name: str) -> bool:
        """Check if class name follows Java conventions."""
        return name[0].isupper() if name else False

    def _is_valid_method_name(self, name: str) -> bool:
        """Check if method name follows Java conventions."""
        return name[0].islower() if name else False

    def _is_valid_variable_name(self, name: str) -> bool:
        """Check if variable name follows Java conventions."""
        return name[0].islower() if name else False

class DesignRule(BaseRule):
    """Check Java design patterns and best practices."""
    
    def analyze(self, content: str) -> List[Dict]:
        issues = []
        try:
            tree = javalang.parse.parse(content)
            self._check_design_issues(tree, issues)
        except Exception as e:
            print(f"Error in Java design analysis: {str(e)}")
        return issues

    def _check_design_issues(self, tree, issues: List[Dict]) -> None:
        """Check for design issues in Java code."""
        # Check for large classes
        for _, node in tree.filter(javalang.tree.ClassDeclaration):
            method_count = len([m for m in node.methods])
            if method_count > 20:
                issues.append({
                    'message': f'Class has too many methods ({method_count})',
                    'line': node.position[0] if node.position else 0,
                    'severity': 'medium',
                    'type': 'quality',
                    'fix': 'Consider splitting the class into smaller classes'
                })

        # Check for long parameter lists
        for _, node in tree.filter(javalang.tree.MethodDeclaration):
            param_count = len(node.parameters) if node.parameters else 0
            if param_count > 5:
                issues.append({
                    'message': f'Method {node.name} has too many parameters ({param_count})',
                    'line': node.position[0] if node.position else 0,
                    'severity': 'medium',
                    'type': 'quality',
                    'fix': 'Consider using a parameter object'
                })

        # Check for proper exception handling
        for _, node in tree.filter(javalang.tree.CatchClause):
            if node.parameter.types == ['Exception']:
                issues.append({
                    'message': 'Catching generic Exception is not recommended',
                    'line': node.position[0] if node.position else 0,
                    'severity': 'medium',
                    'type': 'quality',
                    'fix': 'Catch specific exceptions instead'
                })

        # Check for proper interface usage
        for _, node in tree.filter(javalang.tree.InterfaceDeclaration):
            method_count = len([m for m in node.methods])
            if method_count > 10:
                issues.append({
                    'message': f'Interface has too many methods ({method_count})',
                    'line': node.position[0] if node.position else 0,
                    'severity': 'medium',
                    'type': 'quality',
                    'fix': 'Consider splitting the interface into smaller interfaces'
                })
