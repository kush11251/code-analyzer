"""
Java code parser module.
"""
import javalang
from typing import Dict, Any, Optional, Union

class JavaParser:
    """Parse Java code for analysis."""
    
    @staticmethod
    def parse(content: str) -> Optional[javalang.tree.CompilationUnit]:
        """
        Parse Java code into an AST.
        
        Args:
            content: Java source code
            
        Returns:
            CompilationUnit object or None if parsing fails
        """
        try:
            return javalang.parse.parse(content)
        except Exception as e:
            print(f"Error parsing Java code: {str(e)}")
            return None

    @staticmethod
    def get_imports(tree: javalang.tree.CompilationUnit) -> Dict[str, Any]:
        """Extract import information from AST."""
        imports = {
            'standard': [],
            'static': []
        }
        
        for imp in tree.imports:
            if imp.static:
                imports['static'].append({
                    'path': imp.path,
                    'wildcard': imp.wildcard
                })
            else:
                imports['standard'].append({
                    'path': imp.path,
                    'wildcard': imp.wildcard
                })
                
        return imports

    @staticmethod
    def get_package(tree: javalang.tree.CompilationUnit) -> str:
        """Get package declaration."""
        return tree.package.name if tree.package else ''

    @staticmethod
    def get_classes(tree: javalang.tree.CompilationUnit) -> Dict[str, Any]:
        """Extract class information from AST."""
        classes = []
        
        for path, node in tree.filter(javalang.tree.ClassDeclaration):
            class_info = {
                'name': node.name,
                'modifiers': list(node.modifiers),
                'extends': node.extends.name if node.extends else None,
                'implements': [i.name for i in node.implements] if node.implements else [],
                'methods': [],
                'fields': []
            }
            
            # Get methods
            for method in node.methods:
                method_info = {
                    'name': method.name,
                    'modifiers': list(method.modifiers),
                    'return_type': JavaParser._get_type_name(method.return_type),
                    'parameters': [
                        {
                            'name': param.name,
                            'type': JavaParser._get_type_name(param.type)
                        }
                        for param in method.parameters
                    ],
                    'throws': [t.name for t in method.throws] if method.throws else []
                }
                class_info['methods'].append(method_info)
            
            # Get fields
            for field in node.fields:
                for declarator in field.declarators:
                    field_info = {
                        'name': declarator.name,
                        'type': JavaParser._get_type_name(field.type),
                        'modifiers': list(field.modifiers)
                    }
                    class_info['fields'].append(field_info)
                    
            classes.append(class_info)
            
        return {'classes': classes}

    @staticmethod
    def get_interfaces(tree: javalang.tree.CompilationUnit) -> Dict[str, Any]:
        """Extract interface information from AST."""
        interfaces = []
        
        for path, node in tree.filter(javalang.tree.InterfaceDeclaration):
            interface_info = {
                'name': node.name,
                'modifiers': list(node.modifiers),
                'extends': [e.name for e in node.extends] if node.extends else [],
                'methods': []
            }
            
            # Get method declarations
            for method in node.methods:
                method_info = {
                    'name': method.name,
                    'modifiers': list(method.modifiers),
                    'return_type': JavaParser._get_type_name(method.return_type),
                    'parameters': [
                        {
                            'name': param.name,
                            'type': JavaParser._get_type_name(param.type)
                        }
                        for param in method.parameters
                    ]
                }
                interface_info['methods'].append(method_info)
                
            interfaces.append(interface_info)
            
        return {'interfaces': interfaces}

    @staticmethod
    def analyze_complexity(tree: javalang.tree.CompilationUnit) -> Dict[str, Any]:
        """Analyze code complexity metrics."""
        metrics = {
            'num_classes': 0,
            'num_interfaces': 0,
            'num_methods': 0,
            'num_fields': 0,
            'complexity': 0
        }
        
        # Count classes and their members
        for _, node in tree.filter(javalang.tree.ClassDeclaration):
            metrics['num_classes'] += 1
            metrics['num_methods'] += len(node.methods)
            metrics['num_fields'] += sum(len(f.declarators) for f in node.fields)
            
        # Count interfaces
        for _, node in tree.filter(javalang.tree.InterfaceDeclaration):
            metrics['num_interfaces'] += 1
            metrics['num_methods'] += len(node.methods)
            
        # Calculate cyclomatic complexity
        for _, node in tree.filter((
            javalang.tree.IfStatement,
            javalang.tree.WhileStatement,
            javalang.tree.DoStatement,
            javalang.tree.ForStatement,
            javalang.tree.SwitchStatementCase,
            javalang.tree.CatchClause
        )):
            metrics['complexity'] += 1
            
        return metrics

    @staticmethod
    def _get_type_name(type_node: Union[javalang.tree.ReferenceType, None]) -> Optional[str]:
        """Get the string representation of a type node."""
        if type_node is None:
            return None
        if isinstance(type_node, javalang.tree.ReferenceType):
            return type_node.name
        return str(type_node)
