"""
JavaScript code parser module.
"""
import esprima
from typing import Dict, Any, Optional

class JavaScriptParser:
    """Parse JavaScript code for analysis."""
    
    @staticmethod
    def parse(content: str) -> Optional[Dict]:
        """
        Parse JavaScript code into an AST.
        
        Args:
            content: JavaScript source code
            
        Returns:
            AST object or None if parsing fails
        """
        try:
            return esprima.parseScript(content, {'loc': True, 'range': True})
        except Exception as e:
            print(f"Error parsing JavaScript code: {str(e)}")
            return None

    @staticmethod
    def get_imports(tree: Dict) -> Dict[str, Any]:
        """Extract import information from AST."""
        imports = {
            'es_modules': [],
            'require': [],
            'dynamic': []
        }
        
        def visit(node):
            if node['type'] == 'ImportDeclaration':
                imports['es_modules'].append({
                    'source': node['source']['value'],
                    'line': node['loc']['start']['line']
                })
            elif (node['type'] == 'CallExpression' and
                  node['callee']['type'] == 'Identifier' and
                  node['callee']['name'] == 'require'):
                if node['arguments'][0]['type'] == 'Literal':
                    imports['require'].append({
                        'source': node['arguments'][0]['value'],
                        'line': node['loc']['start']['line']
                    })
            elif (node['type'] == 'ImportExpression'):
                imports['dynamic'].append({
                    'source': node['source']['value'],
                    'line': node['loc']['start']['line']
                })
                
            for key, value in node.items():
                if isinstance(value, dict):
                    visit(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            visit(item)
                            
        visit(tree)
        return imports

    @staticmethod
    def get_functions(tree: Dict) -> Dict[str, Any]:
        """Extract function information from AST."""
        functions = []
        
        def visit(node):
            if node['type'] in ['FunctionDeclaration', 'FunctionExpression', 'ArrowFunctionExpression']:
                func_info = {
                    'name': node.get('id', {}).get('name', 'anonymous'),
                    'type': node['type'],
                    'params': len(node.get('params', [])),
                    'async': node.get('async', False),
                    'generator': node.get('generator', False),
                    'line': node['loc']['start']['line']
                }
                functions.append(func_info)
                
            for key, value in node.items():
                if isinstance(value, dict):
                    visit(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            visit(item)
                            
        visit(tree)
        return {'functions': functions}

    @staticmethod
    def get_classes(tree: Dict) -> Dict[str, Any]:
        """Extract class information from AST."""
        classes = []
        
        def visit(node):
            if node['type'] == 'ClassDeclaration':
                class_info = {
                    'name': node['id']['name'],
                    'superClass': node.get('superClass', {}).get('name'),
                    'methods': [],
                    'line': node['loc']['start']['line']
                }
                
                for item in node.get('body', {}).get('body', []):
                    if item['type'] == 'MethodDefinition':
                        method_info = {
                            'name': item['key']['name'],
                            'static': item['static'],
                            'kind': item['kind'],
                            'line': item['loc']['start']['line']
                        }
                        class_info['methods'].append(method_info)
                        
                classes.append(class_info)
                
            for key, value in node.items():
                if isinstance(value, dict):
                    visit(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            visit(item)
                            
        visit(tree)
        return {'classes': classes}

    @staticmethod
    def get_variables(tree: Dict) -> Dict[str, Any]:
        """Extract variable declarations from AST."""
        variables = []
        
        def visit(node):
            if node['type'] == 'VariableDeclaration':
                for declarator in node['declarations']:
                    if declarator['id']['type'] == 'Identifier':
                        var_info = {
                            'name': declarator['id']['name'],
                            'kind': node['kind'],
                            'line': node['loc']['start']['line']
                        }
                        variables.append(var_info)
                        
            for key, value in node.items():
                if isinstance(value, dict):
                    visit(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            visit(item)
                            
        visit(tree)
        return {'variables': variables}

    @staticmethod
    def analyze_complexity(tree: Dict) -> Dict[str, Any]:
        """Analyze code complexity metrics."""
        metrics = {
            'num_functions': 0,
            'num_classes': 0,
            'num_imports': 0,
            'lines_of_code': 0,
            'complexity': 0
        }
        
        def visit(node):
            if node['type'] in ['FunctionDeclaration', 'FunctionExpression', 'ArrowFunctionExpression']:
                metrics['num_functions'] += 1
            elif node['type'] == 'ClassDeclaration':
                metrics['num_classes'] += 1
            elif node['type'] in ['ImportDeclaration', 'CallExpression'] and \
                 node.get('callee', {}).get('name') == 'require':
                metrics['num_imports'] += 1
                
            # Calculate cyclomatic complexity
            if node['type'] in ['IfStatement', 'WhileStatement', 'DoWhileStatement',
                              'ForStatement', 'ForInStatement', 'ForOfStatement',
                              'ConditionalExpression', 'SwitchCase']:
                metrics['complexity'] += 1
                
            for key, value in node.items():
                if isinstance(value, dict):
                    visit(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            visit(item)
                            
        visit(tree)
        return metrics
