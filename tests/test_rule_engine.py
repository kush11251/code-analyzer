"""
Test cases for the rule engine.
"""
import unittest
from unittest.mock import Mock, patch

from core.config import AnalyzerConfig
from detectors.rule_engine import RuleEngine

class TestRuleEngine(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.config = AnalyzerConfig()
        self.config.load_user_config()
        self.rule_engine = RuleEngine(self.config)
    
    def test_get_rules_for_language(self):
        """Test retrieving rules for a specific language."""
        # Test Python rules
        python_rules = self.rule_engine.get_rules_for_language('python')
        self.assertTrue(len(python_rules) > 0)
        
        # Test JavaScript rules
        js_rules = self.rule_engine.get_rules_for_language('javascript')
        self.assertTrue(len(js_rules) > 0)
        
        # Test unknown language
        unknown_rules = self.rule_engine.get_rules_for_language('brainfuck')
        self.assertEqual(len(unknown_rules), 0)
    
    def test_rule_loading(self):
        """Test that rules are properly loaded from modules."""
        for language in ['python', 'javascript', 'java']:
            rules = self.rule_engine.get_rules_for_language(language)
            
            # Check both quality and security rules are loaded
            rule_types = set(rule.__class__.__module__.split('.')[-1]
                           for rule in rules)
            self.assertTrue('rules_quality' in rule_types)
            self.assertTrue('rules_security' in rule_types)
    
    def test_custom_rules(self):
        """Test loading custom rules from plugins."""
        # Create a mock custom rule
        mock_rule = Mock()
        mock_rule.languages = ['python']
        
        with patch('plugins.custom_rules.sample_rule.CustomRule', 
                  return_value=mock_rule):
            # Reload rules to include custom rule
            self.rule_engine.load_rules()
            
            # Get Python rules
            python_rules = self.rule_engine.get_rules_for_language('python')
            
            # Verify custom rule is included
            self.assertIn(mock_rule, python_rules)
    
    def test_disabled_rules(self):
        """Test handling of disabled rules."""
        # Disable Python quality rules
        with patch.dict(self.config.settings['languages']['python']['rules'],
                       {'quality': []}):
            python_rules = self.rule_engine.get_rules_for_language('python')
            
            # Verify only security rules are loaded
            rule_types = set(rule.__class__.__module__.split('.')[-1]
                           for rule in python_rules)
            self.assertNotIn('rules_quality', rule_types)
            self.assertIn('rules_security', rule_types)

if __name__ == '__main__':
    unittest.main()