"""
Java code fixer module.
Provides automated fixes for common code issues.
"""
import javalang
from typing import Dict, List, Optional, Tuple
import re

class JavaFixer:
    """Fix Java code issues automatically."""
    
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
        fixed = content
        applied_fixes = []
        
        for issue in issues:
            if 'fix' not in issue:
                continue
                
            fix_result = None
            if 'cyclomatic complexity' in issue['message'].lower():
                fix_result = JavaFixer._fix_complexity(fixed, issue)
            elif 'naming convention' in issue['message'].lower():
                fix_result = JavaFixer._fix_naming(fixed, issue)
            elif 'too many parameters' in issue['message'].lower():
                fix_result = JavaFixer._fix_parameters(fixed, issue)
            elif 'exception' in issue['message'].lower():
                fix_result = JavaFixer._fix_exception_handling(fixed, issue)
            
            if fix_result:
                fixed, fix_info = fix_result
                applied_fixes.append(fix_info)
                
        return fixed, applied_fixes

    @staticmethod
    def _fix_complexity(content: str, issue: Dict) -> Optional[Tuple[str, Dict]]:
        """Fix cyclomatic complexity issues."""
        try:
            tree = javalang.parse.parse(content)
            
            # Find the complex method
            target_method = None
            for _, node in tree.filter(javalang.tree.MethodDeclaration):
                if node.position.line == issue['line']:
                    target_method = node
                    break
                    
            if target_method:
                # Extract method content
                method_lines = JavaFixer._get_method_lines(content, target_method)
                method_content = '\n'.join(method_lines)
                
                # Create helper methods
                fixed_content = JavaFixer._split_complex_method(
                    method_content,
                    target_method.name
                )
                
                # Replace original method
                start_line = target_method.position.line - 1
                end_line = start_line + len(method_lines)
                
                lines = content.splitlines()
                fixed = (
                    '\n'.join(lines[:start_line]) +
                    '\n' + fixed_content + '\n' +
                    '\n'.join(lines[end_line:])
                )
                
                return (
                    fixed,
                    {
                        'type': 'complexity',
                        'line': issue['line'],
                        'message': 'Split complex method into smaller methods'
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
            
            if 'class' in issue['message'].lower():
                new_name = JavaFixer._to_pascal_case(old_name)
            else:
                new_name = JavaFixer._to_camel_case(old_name)
                
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
        """Fix methods with too many parameters."""
        try:
            tree = javalang.parse.parse(content)
            
            # Find the method with too many parameters
            target_method = None
            for _, node in tree.filter(javalang.tree.MethodDeclaration):
                if node.position.line == issue['line']:
                    target_method = node
                    break
                    
            if target_method:
                # Create parameter object
                class_name = JavaFixer._create_parameter_class(target_method)
                
                # Update method signature
                method_lines = JavaFixer._get_method_lines(content, target_method)
                updated_method = JavaFixer._update_method_signature(
                    method_lines,
                    target_method.name,
                    class_name
                )
                
                # Insert the new class before the method
                lines = content.splitlines()
                class_insert_line = target_method.position.line - 1
                
                fixed = (
                    '\n'.join(lines[:class_insert_line]) +
                    '\n\n' + class_name + '\n\n' +
                    updated_method + '\n' +
                    '\n'.join(lines[class_insert_line + len(method_lines):])
                )
                
                return (
                    fixed,
                    {
                        'type': 'parameters',
                        'line': issue['line'],
                        'message': 'Created parameter class and updated method signature'
                    }
                )
        except Exception as e:
            print(f"Error fixing parameters: {str(e)}")
        return None

    @staticmethod
    def _fix_exception_handling(content: str, issue: Dict) -> Optional[Tuple[str, Dict]]:
        """Fix exception handling issues."""
        try:
            lines = content.splitlines()
            line = lines[issue['line'] - 1]
            
            if 'catch (Exception' in line:
                # Replace generic Exception with specific exceptions
                specific_exceptions = JavaFixer._suggest_specific_exceptions(content, issue['line'])
                if specific_exceptions:
                    fixed_line = line.replace(
                        'Exception',
                        ' | '.join(specific_exceptions)
                    )
                    lines[issue['line'] - 1] = fixed_line
                    
                    return (
                        '\n'.join(lines),
                        {
                            'type': 'exception',
                            'line': issue['line'],
                            'message': 'Replaced generic Exception with specific exceptions'
                        }
                    )
        except Exception as e:
            print(f"Error fixing exception handling: {str(e)}")
        return None

    @staticmethod
    def _get_method_lines(content: str, method_node) -> List[str]:
        """Extract method lines from content."""
        lines = content.splitlines()
        start_line = method_node.position.line - 1
        
        # Find method end by matching braces
        brace_count = 0
        end_line = start_line
        
        for i, line in enumerate(lines[start_line:], start_line):
            brace_count += line.count('{') - line.count('}')
            if brace_count == 0:
                end_line = i + 1
                break
                
        return lines[start_line:end_line]

    @staticmethod
    def _split_complex_method(method_content: str, method_name: str) -> str:
        """Split a complex method into smaller methods."""
        # Extract conditions into helper methods
        helper_methods = []
        condition_count = 0
        
        def extract_condition(match):
            nonlocal condition_count
            condition_count += 1
            helper_name = f'handle{method_name}Condition{condition_count}'
            condition_body = match.group(2)
            
            helper = f"""
    private void {helper_name}() {{
        {condition_body}
    }}"""
            helper_methods.append(helper)
            
            return f"""if ({match.group(1)}) {{
            {helper_name}();
        }}"""
        
        # Find and extract complex conditions
        pattern = r'if\s*\((.*?)\)\s*\{((?:[^{}]|{[^{}]*})*)\}'
        fixed_content = re.sub(pattern, extract_condition, method_content)
        
        # Combine helper methods with main method
        return '\n'.join(helper_methods) + '\n\n' + fixed_content

    @staticmethod
    def _create_parameter_class(method_node) -> str:
        """Create a parameter class for the method."""
        class_name = f'{method_node.name.capitalize()}Params'
        params = [(param.type.name, param.name) for param in method_node.parameters]
        
        lines = [f'private static class {class_name} {{']
        
        # Add fields
        for param_type, param_name in params:
            lines.append(f'    private final {param_type} {param_name};')
            
        # Add constructor
        lines.append(f'\n    public {class_name}({", ".join(f"{t} {n}" for t, n in params)}) {{')
        for _, param_name in params:
            lines.append(f'        this.{param_name} = {param_name};')
        lines.append('    }')
        
        # Add getters
        for param_type, param_name in params:
            lines.append(f'''
    public {param_type} get{param_name.capitalize()}() {{
        return {param_name};
    }}''')
            
        lines.append('}')
        return '\n'.join(lines)

    @staticmethod
    def _update_method_signature(method_lines: List[str], method_name: str, class_name: str) -> str:
        """Update method signature to use parameter class."""
        # Update signature
        signature_pattern = rf'(.*?){method_name}\s*\((.*?)\)'
        
        def update_signature(match):
            return f'{match.group(1)}{method_name}({class_name} params)'
            
        new_signature = re.sub(signature_pattern, update_signature, method_lines[0])
        method_lines[0] = new_signature
        
        # Update parameter usage in method body
        for i in range(1, len(method_lines)):
            line = method_lines[i]
            if '{' in line or '}' in line:
                continue
                
            # Replace direct parameter usage with getter calls
            words = re.findall(r'\b\w+\b', line)
            for word in words:
                if re.search(rf'\b{word}\b', method_lines[0]):  # Check if word was a parameter
                    line = re.sub(
                        rf'\b{word}\b',
                        f'params.get{word.capitalize()}()',
                        line
                    )
            method_lines[i] = line
            
        return '\n'.join(method_lines)

    @staticmethod
    def _suggest_specific_exceptions(content: str, line_num: str) -> List[str]:
        """Suggest specific exceptions based on code context."""
        try:
            tree = javalang.parse.parse(content)
            exceptions = set()
            
            # Find risky operations and suggest appropriate exceptions
            for _, node in tree.filter((
                javalang.tree.MethodInvocation,
                javalang.tree.ClassCreator,
                javalang.tree.Assignment
            )):
                if hasattr(node, 'position') and node.position:
                    if abs(node.position.line - line_num) <= 5:  # Check nearby context
                        if 'read' in str(node) or 'write' in str(node):
                            exceptions.add('IOException')
                        if 'parse' in str(node):
                            exceptions.add('ParseException')
                        if 'new' in str(node):
                            exceptions.add('InstantiationException')
                        
            return list(exceptions) or ['IllegalArgumentException', 'RuntimeException']
        except Exception:
            return ['IllegalArgumentException', 'RuntimeException']

    @staticmethod
    def _to_camel_case(name: str) -> str:
        """Convert a name to camelCase."""
        components = name.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    @staticmethod
    def _to_pascal_case(name: str) -> str:
        """Convert a name to PascalCase."""
        return ''.join(x.title() for x in name.split('_'))
