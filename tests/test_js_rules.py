"""
Test cases for JavaScript rules.
"""
import unittest
from pathlib import Path
from unittest.mock import Mock

from core.config import AnalyzerConfig
from languages.javascript.rules_quality import (
    ComplexityRule,
    StyleRule,
    BestPracticesRule
)
from languages.javascript.rules_security import (
    XSSRule,
    InjectionRule,
    AuthenticationRule
)

class TestJavaScriptQualityRules(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.config = AnalyzerConfig()
        self.config.load_user_config()
    
    def test_complexity_rule(self):
        """Test the complexity rule."""
        rule = ComplexityRule(self.config)
        
        # Test highly complex code
        complex_code = """
function processData(data) {
    if (data.type === 'user') {
        for (let i = 0; i < data.items.length; i++) {
            if (data.items[i].active) {
                while (data.items[i].retries > 0) {
                    try {
                        if (data.items[i].value > 100) {
                            return processSpecial(data.items[i]);
                        }
                    } catch (e) {
                        data.items[i].retries--;
                    }
                }
            }
        }
    }
    return null;
}
"""
        issues = rule.analyze(complex_code)
        self.assertTrue(any(issue['type'] == 'complexity' for issue in issues))
        
        # Test simple code
        simple_code = """
function add(a, b) {
    return a + b;
}
"""
        issues = rule.analyze(simple_code)
        self.assertFalse(any(issue['type'] == 'complexity' for issue in issues))
    
    def test_style_rule(self):
        """Test the style rule."""
        rule = StyleRule(self.config)
        
        # Test code with style issues
        bad_style = """
function bad_name( x,y){
    var z=x+y;
    return z;
};
"""
        issues = rule.analyze(bad_style)
        self.assertTrue(any(issue['type'] == 'style' for issue in issues))
        
        # Test code with good style
        good_style = """
function addNumbers(x, y) {
    const sum = x + y;
    return sum;
}
"""
        issues = rule.analyze(good_style)
        self.assertFalse(any(issue['type'] == 'style' for issue in issues))

class TestJavaScriptSecurityRules(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.config = AnalyzerConfig()
        self.config.load_user_config()
    
    def test_xss_rule(self):
        """Test the XSS rule."""
        rule = XSSRule(self.config)
        
        # Test code with XSS vulnerability
        vulnerable_code = """
function displayUser(user) {
    document.getElementById('user').innerHTML = user.name;
}
"""
        issues = rule.analyze(vulnerable_code)
        self.assertTrue(any(issue['type'] == 'xss' for issue in issues))
        
        # Test safe code
        safe_code = """
function displayUser(user) {
    const text = document.createTextNode(user.name);
    document.getElementById('user').appendChild(text);
}
"""
        issues = rule.analyze(safe_code)
        self.assertFalse(any(issue['type'] == 'xss' for issue in issues))
    
    def test_injection_rule(self):
        """Test the injection rule."""
        rule = InjectionRule(self.config)
        
        # Test code with eval injection
        vulnerable_code = """
function calculate(expr) {
    return eval(expr);
}
"""
        issues = rule.analyze(vulnerable_code)
        self.assertTrue(any(issue['type'] == 'eval_injection' for issue in issues))
        
        # Test safe code
        safe_code = """
function calculate(a, b, operator) {
    switch (operator) {
        case '+': return a + b;
        case '-': return a - b;
        default: throw new Error('Invalid operator');
    }
}
"""
        issues = rule.analyze(safe_code)
        self.assertFalse(any(issue['type'] == 'eval_injection' for issue in issues))

if __name__ == '__main__':
    unittest.main()
