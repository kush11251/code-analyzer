"""
Python code fixer module.
Provides automated fixes for common code issues.
"""
import ast
import astor
from typing import Dict, List, Optional, Tuple
import re

class PythonFixer:
    """Fix Python code issues automatically."""
    
    @staticmethod
    def fix_code(content: str, issues: List[Dict]) -> Tuple[str, List[Dict]]:
        """
        Apply fixes to the code based on identified issues.
        
        Args:
            content: Original source code
            issues: List of issues to fix
            
        Returns:
            Tuple of (fixed code, list of applied fixes)
        """
        tree = ast.parse(content)
        fixed = content
        applied_fixes = []
        
        for issue in issues:
            if 'fix' not in issue:
                continue
                
            fix_result = None
            if 'cyclomatic complexity' in issue['message'].lower():
                fix_result = PythonFixer._fix_complexity(fixed, issue)
            elif 'naming convention' in issue['message'].lower():
                fix_result = PythonFixer._fix_naming(fixed, issue)
            elif 'too many parameters' in issue['message'].lower():
                fix_result = PythonFixer._fix_parameters(fixed, issue)
            elif 'line too long' in issue['message'].lower():
                fix_result = PythonFixer._fix_line_length(fixed, issue)
            
            if fix_result:
                fixed, fix_info = fix_result
                applied_fixes.append(fix_info)
                
        return fixed, applied_fixes

    @staticmethod
    def _fix_complexity(content: str, issue: Dict) -> Optional[Tuple[str, Dict]]:
        """Fix cyclomatic complexity issues."""
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if (isinstance(node, ast.FunctionDef) and 
                    node.lineno == issue['line']):
                    # Extract the complex function
                    function_source = astor.to_source(node)
                    
                    # Create helper functions for nested conditions
                    fixed_source = PythonFixer._split_complex_function(function_source)
                    
                    # Replace the original function with the refactored version
                    return (
                        content.replace(function_source, fixed_source),
                        {
                            'type': 'complexity',
                            'line': issue['line'],
                            'message': 'Split complex function into smaller functions'
                        }
                    )
        except Exception as e:
            print(f"Error fixing complexity: {str(e)}")
        return None

    @staticmethod
    def _fix_naming(content: str, issue: Dict) -> Optional[Tuple[str, Dict]]:
        """Fix naming convention issues."""
        try:
            old_name = re.search(r'"([^"]+)"', issue['message']).group(1)
            if 'function' in issue['message'].lower():
                new_name = PythonFixer._to_snake_case(old_name)
            elif 'class' in issue['message'].lower():
                new_name = PythonFixer._to_pascal_case(old_name)
            else:
                new_name = PythonFixer._to_snake_case(old_name)
                
            # Replace the name while preserving whitespace
            pattern = r'(?<!\w)' + re.escape(old_name) + r'(?!\w)'
            fixed = re.sub(pattern, new_name, content)
            
            return (
                fixed,
                {
                    'type': 'naming',
                    'line': issue['line'],
                    'message': f'Renamed {old_name} to {new_name}'
                }
            )
        except Exception as e:
            print(f"Error fixing naming: {str(e)}")
        return None

    @staticmethod
    def _fix_parameters(content: str, issue: Dict) -> Optional[Tuple[str, Dict]]:
        """Fix functions with too many parameters."""
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if (isinstance(node, ast.FunctionDef) and 
                    node.lineno == issue['line']):
                    # Create a configuration class for parameters
                    config_class = PythonFixer._create_config_class(node)
                    
                    # Update the function to use the config class
                    function_source = astor.to_source(node)
                    fixed_function = PythonFixer._update_function_params(node)
                    
                    return (
                        content.replace(function_source, config_class + '\n\n' + fixed_function),
                        {
                            'type': 'parameters',
                            'line': issue['line'],
                            'message': 'Created config class for parameters'
                        }
                    )
        except Exception as e:
            print(f"Error fixing parameters: {str(e)}")
        return None

    @staticmethod
    def _fix_line_length(content: str, issue: Dict) -> Optional[Tuple[str, Dict]]:
        """Fix lines that are too long."""
        try:
            lines = content.splitlines()
            if 0 <= issue['line'] - 1 < len(lines):
                line = lines[issue['line'] - 1]
                if len(line.strip()) > 79:
                    # Try to break the line at appropriate points
                    fixed_line = PythonFixer._break_long_line(line)
                    lines[issue['line'] - 1] = fixed_line
                    
                    return (
                        '\n'.join(lines),
                        {
                            'type': 'line_length',
                            'line': issue['line'],
                            'message': 'Split long line into multiple lines'
                        }
                    )
        except Exception as e:
            print(f"Error fixing line length: {str(e)}")
        return None

    @staticmethod
    def _split_complex_function(function_source: str) -> str:
        """Split a complex function into smaller functions."""
        tree = ast.parse(function_source)
        function_node = tree.body[0]
        
        # Extract nested conditions into separate functions
        new_functions = []
        condition_count = 0
        
        class ConditionExtractor(ast.NodeTransformer):
            def visit_If(self, node):
                nonlocal condition_count
                if len(node.body) > 2:  # Extract only substantial conditions
                    condition_count += 1
                    func_name = f'_handle_condition_{condition_count}'
                    
                    # Create new function for the condition body
                    new_func = ast.FunctionDef(
                        name=func_name,
                        args=ast.arguments(
                            args=[],
                            vararg=None,
                            kwonlyargs=[],
                            kw_defaults=[],
                            kwarg=None,
                            defaults=[]
                        ),
                        body=node.body,
                        decorator_list=[]
                    )
                    new_functions.append(new_func)
                    
                    # Replace original body with function call
                    node.body = [ast.Expr(ast.Call(
                        func=ast.Name(id=func_name, ctx=ast.Load()),
                        args=[],
                        keywords=[]
                    ))]
                    
                return node
        
        # Transform the AST
        transformer = ConditionExtractor()
        new_tree = transformer.visit(tree)
        
        # Generate source code for all functions
        result = []
        for func in new_functions:
            result.append(astor.to_source(func))
        result.append(astor.to_source(new_tree))
        
        return '\n\n'.join(result)

    @staticmethod
    def _create_config_class(func_node: ast.FunctionDef) -> str:
        """Create a configuration class for function parameters."""
        class_name = func_node.name.title() + 'Config'
        params = [arg.arg for arg in func_node.args.args if arg.arg != 'self']
        
        # Generate class code
        lines = [f"class {class_name}:"]
        lines.append("    def __init__(self, " + ", ".join(params) + "):")
        for param in params:
            lines.append(f"        self.{param} = {param}")
            
        return '\n'.join(lines)

    @staticmethod
    def _update_function_params(func_node: ast.FunctionDef) -> str:
        """Update function to use config class instead of many parameters."""
        class_name = func_node.name.title() + 'Config'
        params = [arg.arg for arg in func_node.args.args if arg.arg != 'self']
        
        # Update function signature
        func_node.args.args = [
            ast.arg(arg='self', annotation=None) 
            if hasattr(func_node, 'self') else None,
            ast.arg(arg='config', annotation=ast.Name(id=class_name, ctx=ast.Load()))
        ]
        
        # Update parameter usage in the function body
        class ParamTransformer(ast.NodeTransformer):
            def visit_Name(self, node):
                if node.id in params:
                    return ast.Attribute(
                        value=ast.Name(id='config', ctx=ast.Load()),
                        attr=node.id,
                        ctx=node.ctx
                    )
                return node
                
        transformer = ParamTransformer()
        func_node = transformer.visit(func_node)
        
        return astor.to_source(func_node)

    @staticmethod
    def _break_long_line(line: str) -> str:
        """Break a long line into multiple lines."""
        # Handle function calls
        if '(' in line and ')' in line:
            return PythonFixer._break_function_call(line)
        # Handle string concatenation
        elif '+' in line:
            return PythonFixer._break_string_concat(line)
        # Handle list/dict literals
        elif '[' in line or '{' in line:
            return PythonFixer._break_literals(line)
        # Default to simple wrapping
        else:
            return PythonFixer._wrap_line(line)

    @staticmethod
    def _break_function_call(line: str) -> str:
        """Break a long function call into multiple lines."""
        match = re.match(r'^(\s*)(.+?\()(.+)(\))$', line)
        if match:
            indent, func, args, closing = match.groups()
            args_list = [arg.strip() for arg in args.split(',')]
            
            if len(args_list) > 1:
                result = [f"{indent}{func}"]
                result.extend(f"{indent}    {arg}," for arg in args_list[:-1])
                result.append(f"{indent}    {args_list[-1]}{closing}")
                return '\n'.join(result)
                
        return line

    @staticmethod
    def _break_string_concat(line: str) -> str:
        """Break string concatenation into multiple lines."""
        parts = re.split(r'\s*\+\s*', line)
        if len(parts) > 1:
            indent = re.match(r'^\s*', line).group()
            result = []
            for part in parts[:-1]:
                result.append(f"{indent}{part} +")
            result.append(f"{indent}{parts[-1]}")
            return '\n'.join(result)
        return line

    @staticmethod
    def _break_literals(line: str) -> str:
        """Break list/dict literals into multiple lines."""
        match = re.match(r'^(\s*)([\[{])(.+)([\]}])$', line)
        if match:
            indent, start, items, end = match.groups()
            items_list = [item.strip() for item in items.split(',')]
            
            if len(items_list) > 1:
                result = [f"{indent}{start}"]
                result.extend(f"{indent}    {item}," for item in items_list[:-1])
                result.append(f"{indent}    {items_list[-1]}")
                result.append(f"{indent}{end}")
                return '\n'.join(result)
                
        return line

    @staticmethod
    def _wrap_line(line: str) -> str:
        """Wrap a long line at a suitable point."""
        if len(line) <= 79:
            return line
            
        indent = re.match(r'^\s*', line).group()
        words = line.split()
        
        current_line = indent
        result = []
        
        for word in words:
            if len(current_line) + len(word) + 1 <= 79:
                current_line += ' ' + word if current_line.strip() else word
            else:
                result.append(current_line)
                current_line = indent + '    ' + word
                
        if current_line:
            result.append(current_line)
            
        return '\n'.join(result)

    @staticmethod
    def _to_snake_case(name: str) -> str:
        """Convert a name to snake_case."""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @staticmethod
    def _to_pascal_case(name: str) -> str:
        """Convert a name to PascalCase."""
        return ''.join(word.capitalize() for word in re.split(r'[_\s]+', name))
