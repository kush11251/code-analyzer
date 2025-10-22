"""
Python code parser module.
"""
import ast
from typing import Dict, Any, Optional

class PythonParser:
    """Parse Python code for analysis."""
    
    @staticmethod
    def parse(content: str) -> Optional[ast.AST]:
        """
        Parse Python code into an AST.
        
        Args:
            content: Python source code
            
        Returns:
            AST object or None if parsing fails
        """
        try:
            return ast.parse(content)
        except SyntaxError as e:
            print(f"Syntax error in Python code: {str(e)}")
            return None
        except Exception as e:
            print(f"Error parsing Python code: {str(e)}")
            return None

    @staticmethod
    def get_imports(tree: ast.AST) -> Dict[str, Any]:
        """Extract import information from AST."""
        imports = {
            'standard': [],
            'third_party': [],
            'local': []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports['standard'].append(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.level > 0:  # Relative import
                    imports['local'].append(f"{'.' * node.level}{node.module if node.module else ''}")
                else:
                    imports['standard'].append(node.module)
                    
        return imports

    @staticmethod
    def get_functions(tree: ast.AST) -> Dict[str, Any]:
        """Extract function information from AST."""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_info = {
                    'name': node.name,
                    'async': isinstance(node, ast.AsyncFunctionDef),
                    'args': len(node.args.args),
                    'decorators': [d.id for d in node.decorator_list if isinstance(d, ast.Name)],
                    'line': node.lineno
                }
                functions.append(func_info)
                
        return {'functions': functions}

    @staticmethod
    def get_classes(tree: ast.AST) -> Dict[str, Any]:
        """Extract class information from AST."""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    'name': node.name,
                    'bases': [base.id for base in node.bases if isinstance(base, ast.Name)],
                    'methods': [],
                    'decorators': [d.id for d in node.decorator_list if isinstance(d, ast.Name)],
                    'line': node.lineno
                }
                
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_info = {
                            'name': item.name,
                            'async': isinstance(item, ast.AsyncFunctionDef),
                            'args': len(item.args.args),
                            'decorators': [d.id for d in item.decorator_list if isinstance(d, ast.Name)],
                            'line': item.lineno
                        }
                        class_info['methods'].append(method_info)
                        
                classes.append(class_info)
                
        return {'classes': classes}

    @staticmethod
    def get_assignments(tree: ast.AST) -> Dict[str, Any]:
        """Extract assignment information from AST."""
        assignments = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assign_info = {
                            'name': target.id,
                            'line': node.lineno,
                            'type': type(node.value).__name__
                        }
                        assignments.append(assign_info)
                        
        return {'assignments': assignments}

    @staticmethod
    def analyze_complexity(tree: ast.AST) -> Dict[str, Any]:
        """Analyze code complexity metrics."""
        metrics = {
            'num_functions': 0,
            'num_classes': 0,
            'num_imports': 0,
            'lines_of_code': 0,
            'complexity': 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                metrics['num_functions'] += 1
            elif isinstance(node, ast.ClassDef):
                metrics['num_classes'] += 1
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                metrics['num_imports'] += 1
            
            # Calculate cyclomatic complexity
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor,
                               ast.ExceptHandler, ast.With, ast.AsyncWith)):
                metrics['complexity'] += 1
                
        return metrics
