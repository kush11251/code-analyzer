"""
Test cases for Python rules.
"""
import unittest
from pathlib import Path
from unittest.mock import Mock

from core.config import AnalyzerConfig
from languages.python.rules_quality import (
    ComplexityRule,
    StyleRule,
    MaintainabilityRule
)
from languages.python.rules_security import (
    InjectionRule,
    AuthenticationRule,
    DataValidationRule
)

class TestPythonQualityRules(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.config = AnalyzerConfig()
        self.config.load_user_config()
    
    def test_complexity_rule(self):
        """Test the complexity rule."""
        rule = ComplexityRule(self.config)
        
        # Test highly complex code
        complex_code = """
def factorial(n):
    if n == 0:
        return 1
    elif n == 1:
        if True:
            while False:
                for i in range(10):
                    if i > 5:
                        return n
                    else:
                        continue
        else:
            return 1
    else:
        return n * factorial(n-1)
"""
        issues = rule.analyze(complex_code)
        self.assertTrue(any(issue['type'] == 'complexity' for issue in issues))
        
        # Test simple code
        simple_code = """
def add(a, b):
    return a + b
"""
        issues = rule.analyze(simple_code)
        self.assertFalse(any(issue['type'] == 'complexity' for issue in issues))
    
    def test_style_rule(self):
        """Test the style rule."""
        rule = StyleRule(self.config)
        
        # Test code with style issues
        bad_style = """
def BAD_NAME( x,y):
    z=x+y
    return z
"""
        issues = rule.analyze(bad_style)
        self.assertTrue(any(issue['type'] == 'style' for issue in issues))
        
        # Test code with good style
        good_style = """
def add_numbers(x, y):
    result = x + y
    return result
"""
        issues = rule.analyze(good_style)
        self.assertFalse(any(issue['type'] == 'style' for issue in issues))

class TestPythonSecurityRules(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.config = AnalyzerConfig()
        self.config.load_user_config()
    
    def test_injection_rule(self):
        """Test the injection rule."""
        rule = InjectionRule(self.config)
        
        # Test code with SQL injection vulnerability
        vulnerable_code = """
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE id = " + user_id)
"""
        issues = rule.analyze(vulnerable_code)
        self.assertTrue(any(issue['type'] == 'sql_injection' for issue in issues))
        
        # Test safe code
        safe_code = """
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
"""
        issues = rule.analyze(safe_code)
        self.assertFalse(any(issue['type'] == 'sql_injection' for issue in issues))
    
    def test_authentication_rule(self):
        """Test the authentication rule."""
        rule = AuthenticationRule(self.config)
        
        # Test code with weak password handling
        weak_auth = """
def check_password(password):
    if len(password) >= 6:
        return True
"""
        issues = rule.analyze(weak_auth)
        self.assertTrue(any(issue['type'] == 'weak_authentication' for issue in issues))
        
        # Test secure code
        secure_auth = """
from passlib.hash import pbkdf2_sha256

def check_password(password, hashed):
    return pbkdf2_sha256.verify(password, hashed)
"""
        issues = rule.analyze(secure_auth)
        self.assertFalse(any(issue['type'] == 'weak_authentication' for issue in issues))

if __name__ == '__main__':
    unittest.main()
