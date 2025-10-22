"""
Test cases for the language detector module.
"""
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from core.config import AnalyzerConfig
from detectors.language_detector import LanguageDetector

class TestLanguageDetector(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.config = AnalyzerConfig()
        self.config.load_user_config()
        self.detector = LanguageDetector(self.config)
        
        # Create mock files
        self.python_file = Mock(spec=Path)
        self.python_file.suffix = '.py'
        
        self.js_file = Mock(spec=Path)
        self.js_file.suffix = '.js'
        
        self.java_file = Mock(spec=Path)
        self.java_file.suffix = '.java'
        
        self.unknown_file = Mock(spec=Path)
        self.unknown_file.suffix = '.xyz'
    
    def test_detect_python(self):
        """Test Python file detection."""
        language = self.detector.detect_language(self.python_file)
        self.assertEqual(language, 'python')
    
    def test_detect_javascript(self):
        """Test JavaScript file detection."""
        language = self.detector.detect_language(self.js_file)
        self.assertEqual(language, 'javascript')
    
    def test_detect_java(self):
        """Test Java file detection."""
        language = self.detector.detect_language(self.java_file)
        self.assertEqual(language, 'java')
    
    def test_detect_unknown(self):
        """Test unknown file type."""
        language = self.detector.detect_language(self.unknown_file)
        self.assertIsNone(language)
    
    def test_disabled_language(self):
        """Test detection of a disabled language."""
        # Patch config to disable JavaScript
        with patch.dict(self.config.settings['languages']['javascript'], {'enabled': False}):
            language = self.detector.detect_language(self.js_file)
            self.assertIsNone(language)
    
    def test_ignored_file(self):
        """Test detection of an ignored file."""
        # Create a mock file in a path that should be ignored
        venv_file = Mock(spec=Path)
        venv_file.suffix = '.py'
        venv_file.__str__.return_value = 'venv/lib/python3.9/site-packages/test.py'
        
        language = self.detector.detect_language(venv_file)
        self.assertIsNone(language)

if __name__ == '__main__':
    unittest.main()
