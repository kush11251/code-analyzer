"""
Rule engine for code analysis.
Manages and executes analysis rules for different programming languages.
"""
from typing import List, Dict, Type, Optional
import importlib
import inspect
from pathlib import Path

class BaseRule:
    """Base class for all analysis rules."""
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.severity = 'medium'
        self.rule_type = 'quality'
        self.language = None

    def analyze(self, content: str) -> List[Dict]:
        """
        Analyze code content and return issues found.
        
        Args:
            content: Source code content to analyze
            
        Returns:
            List of issues found, each containing:
            - message: Description of the issue
            - line: Line number where issue was found
            - severity: Issue severity (critical, high, medium, low, info)
            - type: Issue type (quality, security, etc.)
            - fix: Optional suggested fix
        """
        raise NotImplementedError("Each rule must implement analyze method")

class RuleEngine:
    def __init__(self, config):
        self.config = config
        self.rules = {}
        self._load_rules()

    def _load_rules(self):
        """Load all available rules for each language."""
        languages_dir = Path(__file__).parent.parent / 'languages'
        
        for language in self.config.get_enabled_languages():
            self.rules[language] = {
                'quality': self._load_language_rules(language, 'quality'),
                'security': self._load_language_rules(language, 'security')
            }

    def _load_language_rules(self, language: str, rule_type: str) -> List[BaseRule]:
        """Load rules for a specific language and type."""
        rules = []
        language_config = self.config.get_language_config(language)
        
        if not language_config.get('enabled', False):
            return rules

        try:
            # Import rule modules
            module_name = f"languages.{language}.rules_{rule_type}"
            module = importlib.import_module(module_name)

            # Find all rule classes in the module
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and issubclass(obj, BaseRule) 
                    and obj != BaseRule):
                    rule = obj(self.config)
                    rule.language = language
                    rules.append(rule)

        except ImportError:
            print(f"Warning: Could not load {rule_type} rules for {language}")

        return rules

    def get_rules_for_language(self, language: str) -> List[BaseRule]:
        """Get all rules for a specific language."""
        if language not in self.rules:
            return []
            
        rules = []
        for rule_type in self.rules[language]:
            rules.extend(self.rules[language][rule_type])
        return rules

    def get_rules_by_type(self, language: str, rule_type: str) -> List[BaseRule]:
        """Get rules for a specific language and type."""
        if language not in self.rules or rule_type not in self.rules[language]:
            return []
        return self.rules[language][rule_type]

    def add_custom_rule(self, rule: Type[BaseRule], language: str, 
                       rule_type: str = 'quality') -> None:
        """Add a custom rule to the engine."""
        if language not in self.rules:
            self.rules[language] = {'quality': [], 'security': []}
            
        if rule_type not in self.rules[language]:
            self.rules[language][rule_type] = []

        rule_instance = rule(self.config)
        rule_instance.language = language
        self.rules[language][rule_type].append(rule_instance)

    def analyze_code(self, content: str, language: str, 
                    rule_types: Optional[List[str]] = None) -> List[Dict]:
        """
        Analyze code content with specified rules.
        
        Args:
            content: Source code to analyze
            language: Programming language of the code
            rule_types: Optional list of rule types to apply (quality, security)
            
        Returns:
            List of issues found by all applicable rules
        """
        issues = []
        if language not in self.rules:
            return issues

        # If no rule types specified, use all available types
        if not rule_types:
            rule_types = list(self.rules[language].keys())

        # Apply each rule and collect issues
        for rule_type in rule_types:
            if rule_type in self.rules[language]:
                for rule in self.rules[language][rule_type]:
                    try:
                        rule_issues = rule.analyze(content)
                        if rule_issues:
                            issues.extend(rule_issues)
                    except Exception as e:
                        print(f"Error applying rule {rule.__class__.__name__}: {str(e)}")

        return issues
