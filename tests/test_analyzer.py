"""
Test cases for the main analyzer functionality.
"""
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from tempfile import TemporaryDirectory

from core.main import CodeAnalyzer

class TestCodeAnalyzer(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = CodeAnalyzer()
        
        # Create a temporary directory for test files
        self.temp_dir = TemporaryDirectory()
        self.project_path = Path(self.temp_dir.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def create_test_file(self, name: str, content: str) -> Path:
        """Helper to create a test file."""
        file_path = self.project_path / name
        file_path.write_text(content)
        return file_path
    
    def test_analyze_project(self):
        """Test analyzing a project directory."""
        # Create test files
        self.create_test_file('test.py', """
def insecure_eval(input_str):
    return eval(input_str)
""")
        
        self.create_test_file('test.js', """
function displayUser(user) {
    document.getElementById('user').innerHTML = user.input;
}
""")
        
        # Run analysis
        results = self.analyzer.analyze_project(str(self.project_path))
        
        # Verify results structure
        self.assertIn('summary', results)
        self.assertIn('files', results)
        self.assertEqual(results['summary']['total_files'], 2)
        self.assertEqual(results['summary']['analyzed_files'], 2)
        self.assertTrue(results['summary']['total_issues'] > 0)
    
    def test_analyze_file(self):
        """Test analyzing a single file."""
        # Create a test file with known issues
        file_path = self.create_test_file('test.py', """
def bad_function( x,y):
    z=x+y
    return eval(z)
""")
        
        # Analyze file
        results = self.analyzer.analyze_file(file_path)
        
        # Verify results
        self.assertIsNotNone(results)
        self.assertEqual(results['language'], 'python')
        self.assertTrue(len(results['issues']) > 0)
        
        # Check for both quality and security issues
        issue_types = set(issue['type'] for issue in results['issues'])
        self.assertTrue(any('style' in t for t in issue_types))
        self.assertTrue(any('injection' in t for t in issue_types))
    
    @patch('detectors.ai_engine.AIEngine.analyze_results')
    def test_ai_analysis(self, mock_ai_analyze):
        """Test AI-powered analysis."""
        # Set up mock AI insights
        mock_insights = {
            'summary': 'Test insights',
            'recommendations': ['Fix A', 'Fix B']
        }
        mock_ai_analyze.return_value = mock_insights
        
        # Create test file
        self.create_test_file('test.py', 'print("test")')
        
        # Enable AI analysis in config
        self.analyzer.config.settings['ai_assistance']['enabled'] = True
        
        # Run analysis
        results = self.analyzer.analyze_project(str(self.project_path))
        
        # Verify AI insights are included
        self.assertIn('ai_insights', results)
        self.assertEqual(results['ai_insights'], mock_insights)
    
    def test_error_handling(self):
        """Test error handling during analysis."""
        # Create an unreadable file
        file_path = self.create_test_file('test.py', 'print("test")')
        file_path.chmod(0o000)  # Remove read permissions
        
        # Analyze file (should handle error gracefully)
        results = self.analyzer.analyze_file(file_path)
        self.assertIsNone(results)
        
        # Restore permissions for cleanup
        file_path.chmod(0o600)

if __name__ == '__main__':
    unittest.main()