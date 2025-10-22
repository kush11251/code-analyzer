"""
JavaScript code fixer module.
Provides automated fixes for common code issues.
"""
import esprima
import escodegen
from typing import Dict, List, Optional, Tuple
import re

class JavaScriptFixer:
    """Fix JavaScript code issues automatically."""
    
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
        try:
            tree = esprima.parseScript(content, {'range': True, 'tokens': True, 'comment': True})
            fixed = content
            applied_fixes = []
            
            for issue in issues:
                if 'fix' not in issue:
                    continue
                    
                fix_result = None
                if 'cyclomatic complexity' in issue['message'].lower():
                    fix_result = JavaScriptFixer._fix_complexity(fixed, issue)
                elif 'naming convention' in issue['message'].lower():
                    fix_result = JavaScriptFixer._fix_naming(fixed, issue)
                elif 'too many parameters' in issue['message'].lower():
                    fix_result = JavaScriptFixer._fix_parameters(fixed, issue)
                elif '==' in issue['message']:
                    fix_result = JavaScriptFixer._fix_equality(fixed, issue)
                elif 'var' in issue['message']:
                    fix_result = JavaScriptFixer._fix_var_usage(fixed, issue)
                
                if fix_result:
                    fixed, fix_info = fix_result
                    applied_fixes.append(fix_info)
                    
            return fixed, applied_fixes
        except Exception as e:
            print(f"Error fixing JavaScript code: {str(e)}")
            return content, []

    @staticmethod
    def _fix_complexity(content: str, issue: Dict) -> Optional[Tuple[str, Dict]]:
        """Fix cyclomatic complexity issues."""
        try:
            tree = esprima.parseScript(content)
            
            # Find the complex function
            def find_function(node):
                if node.get('type') in ['FunctionDeclaration', 'FunctionExpression']:
                    if node.get('loc', {}).get('start', {}).get('line') == issue['line']:
                        return node
                for key, value in node.items():
                    if isinstance(value, dict):
                        result = find_function(value)
                        if result:
                            return result
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                result = find_function(item)
                                if result:
                                    return result
                return None
            
            function_node = find_function(tree)
            if function_node:
                # Extract complex conditions into helper functions
                fixed_function = JavaScriptFixer._split_complex_function(function_node)
                
                # Replace the original function
                start, end = function_node['range']
                fixed = content[:start] + fixed_function + content[end:]
                
                return (
                    fixed,
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
            new_name = JavaScriptFixer._to_camel_case(old_name)
            
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
            tree = esprima.parseScript(content)
            
            # Find the function with too many parameters
            def find_function(node):
                if node.get('type') in ['FunctionDeclaration', 'FunctionExpression']:
                    if node.get('loc', {}).get('start', {}).get('line') == issue['line']:
                        return node
                for key, value in node.items():
                    if isinstance(value, dict):
                        result = find_function(value)
                        if result:
                            return result
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                result = find_function(item)
                                if result:
                                    return result
                return None
            
            function_node = find_function(tree)
            if function_node:
                # Create an options object
                fixed_function = JavaScriptFixer._create_options_object(function_node)
                
                # Replace the original function
                start, end = function_node['range']
                fixed = content[:start] + fixed_function + content[end:]
                
                return (
                    fixed,
                    {
                        'type': 'parameters',
                        'line': issue['line'],
                        'message': 'Converted parameters to options object'
                    }
                )
        except Exception as e:
            print(f"Error fixing parameters: {str(e)}")
        return None

    @staticmethod
    def _fix_equality(content: str, issue: Dict) -> Optional[Tuple[str, Dict]]:
        """Fix loose equality (==) to strict equality (===)."""
        try:
            lines = content.splitlines()
            line = lines[issue['line'] - 1]
            fixed_line = line.replace('==', '===').replace('!=', '!==')
            lines[issue['line'] - 1] = fixed_line
            
            return (
                '\n'.join(lines),
                {
                    'type': 'equality',
                    'line': issue['line'],
                    'message': 'Converted == to ==='
                }
            )
        except Exception as e:
            print(f"Error fixing equality: {str(e)}")
        return None

    @staticmethod
    def _fix_var_usage(content: str, issue: Dict) -> Optional[Tuple[str, Dict]]:
        """Fix var usage to let/const."""
        try:
            lines = content.splitlines()
            line = lines[issue['line'] - 1]
            
            # Check if the variable is reassigned
            var_name = re.search(r'var\s+(\w+)', line).group(1)
            is_reassigned = JavaScriptFixer._is_variable_reassigned(content, var_name)
            
            # Replace var with appropriate declaration
            fixed_line = line.replace('var', 'let' if is_reassigned else 'const')
            lines[issue['line'] - 1] = fixed_line
            
            return (
                '\n'.join(lines),
                {
                    'type': 'var_usage',
                    'line': issue['line'],
                    'message': f'Converted var to {"let" if is_reassigned else "const"}'
                }
            )
        except Exception as e:
            print(f"Error fixing var usage: {str(e)}")
        return None

    @staticmethod
    def _split_complex_function(node: Dict) -> str:
        """Split a complex function into smaller functions."""
        # Extract the function name or create one for anonymous functions
        func_name = node.get('id', {}).get('name', '_anonymousFunc')
        
        # Create helper functions for complex conditions
        helper_functions = []
        helper_count = 0
        
        def extract_conditions(node):
            nonlocal helper_count
            if node.get('type') == 'IfStatement' and len(node.get('consequent', {}).get('body', [])) > 2:
                helper_count += 1
                helper_name = f'_{func_name}_condition_{helper_count}'
                
                # Create helper function
                helper = {
                    'type': 'FunctionDeclaration',
                    'id': {'name': helper_name},
                    'params': [],
                    'body': node['consequent']
                }
                helper_functions.append(helper)
                
                # Replace original condition body with helper call
                node['consequent'] = {
                    'type': 'BlockStatement',
                    'body': [{
                        'type': 'ExpressionStatement',
                        'expression': {
                            'type': 'CallExpression',
                            'callee': {'type': 'Identifier', 'name': helper_name},
                            'arguments': []
                        }
                    }]
                }
            
            for key, value in node.items():
                if isinstance(value, dict):
                    extract_conditions(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            extract_conditions(item)
        
        # Transform the AST
        extract_conditions(node)
        
        # Generate code
        result = []
        for helper in helper_functions:
            result.append(escodegen.generate(helper))
        result.append(escodegen.generate(node))
        
        return '\n\n'.join(result)

    @staticmethod
    def _create_options_object(node: Dict) -> str:
        """Convert function parameters to an options object."""
        params = [p['name'] for p in node['params']]
        func_name = node.get('id', {}).get('name', '')
        
        # Create the function with options parameter
        new_function = {
            'type': 'FunctionDeclaration',
            'id': {'name': func_name},
            'params': [{
                'type': 'Identifier',
                'name': 'options'
            }],
            'body': node['body']
        }
        
        # Add parameter destructuring
        new_function['body']['body'].insert(0, {
            'type': 'VariableDeclaration',
            'kind': 'const',
            'declarations': [{
                'type': 'VariableDeclarator',
                'id': {
                    'type': 'ObjectPattern',
                    'properties': [
                        {
                            'type': 'Property',
                            'key': {'type': 'Identifier', 'name': p},
                            'value': {'type': 'Identifier', 'name': p},
                            'kind': 'init',
                            'shorthand': True
                        } for p in params
                    ]
                },
                'init': {'type': 'Identifier', 'name': 'options'}
            }]
        })
        
        return escodegen.generate(new_function)

    @staticmethod
    def _is_variable_reassigned(content: str, var_name: str) -> bool:
        """Check if a variable is reassigned after declaration."""
        try:
            tree = esprima.parseScript(content)
            reassigned = False
            
            def check_reassignment(node):
                nonlocal reassigned
                if node.get('type') == 'AssignmentExpression':
                    if (node.get('left', {}).get('type') == 'Identifier' and
                        node.get('left', {}).get('name') == var_name):
                        reassigned = True
                
                for key, value in node.items():
                    if isinstance(value, dict):
                        check_reassignment(value)
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                check_reassignment(item)
            
            check_reassignment(tree)
            return reassigned
        except Exception:
            # If we can't determine, assume it's reassigned to be safe
            return True

    @staticmethod
    def _to_camel_case(name: str) -> str:
        """Convert a name to camelCase."""
        components = name.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])
