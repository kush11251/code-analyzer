"""
Main entry point for the code analyzer tool.
Handles the orchestration of analysis process across different languages and rules.
"""
from typing import Dict, List, Optional
from pathlib import Path

from core.config import AnalyzerConfig
from core.utils.logger import setup_logger
from detectors.language_detector import LanguageDetector
from detectors.rule_engine import RuleEngine
from detectors.ai_engine import AIEngine
from reports.report_builder import ReportBuilder

class CodeAnalyzer:
    def __init__(self, config_path: Optional[str] = None):
        self.config = AnalyzerConfig(config_path)
        self.config.load_user_config()
        
        # Set up logging
        log_config = self.config.get_logging_config()
        self.logger = setup_logger(log_config['level'], log_config['file'])
        
        self.language_detector = LanguageDetector(self.config)
        self.rule_engine = RuleEngine(self.config)
        self.ai_engine = AIEngine(self.config)
        self.report_builder = ReportBuilder(self.config)
        
        self.logger.info("Code Analyzer initialized")

    def analyze_project(self, project_path: str) -> Dict:
        """
        Analyze an entire project directory.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            Dictionary containing analysis results
        """
        project_path = Path(project_path)
        if not project_path.exists():
            self.logger.error(f"Project path not found: {project_path}")
            raise FileNotFoundError(f"Project path not found: {project_path}")

        self.logger.info(f"Starting analysis of project: {project_path}")
        
        # Initialize results
        results = {
            'summary': {
                'total_files': 0,
                'analyzed_files': 0,
                'total_issues': 0,
                'issues_by_severity': {},
                'issues_by_type': {}
            },
            'files': {}
        }

        # Analyze each file in the project
        for file_path in self._get_analyzable_files(project_path):
            self.logger.debug(f"Analyzing file: {file_path}")
            file_results = self.analyze_file(file_path)
            if file_results:
                self._update_results(results, file_path, file_results)
                self.logger.debug(f"Completed analysis of file: {file_path}")
            else:
                self.logger.warning(f"Failed to analyze file: {file_path}")

        # Add AI-powered insights if enabled
        if self.config.get_ai_config()['enabled']:
            self.logger.info("Running AI analysis...")
            results['ai_insights'] = self.ai_engine.analyze_results(results)
            self.logger.info("AI analysis completed")

        return results

    def analyze_file(self, file_path: Path) -> Optional[Dict]:
        """
        Analyze a single file.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Dictionary containing analysis results for the file
        """
        try:
            # Detect language
            language = self.language_detector.detect_language(file_path)
            if not language:
                return None

            # Read file content
            content = file_path.read_text()

            # Run analysis
            results = {
                'language': language,
                'size': len(content),
                'issues': []
            }

            # Apply language-specific rules
            lang_rules = self.rule_engine.get_rules_for_language(language)
            for rule in lang_rules:
                issues = rule.analyze(content)
                if issues:
                    results['issues'].extend(issues)

            return results
        except Exception as e:
            self.logger.error(f"Error analyzing {file_path}: {str(e)}", exc_info=True)
            return None

    def _get_analyzable_files(self, project_path: Path) -> List[Path]:
        """Get list of files that can be analyzed based on configuration."""
        files = []
        enabled_languages = self.config.get_enabled_languages()
        
        for language in enabled_languages:
            lang_config = self.config.get_language_config(language)
            extensions = lang_config.get('extensions', [])
            ignore_patterns = lang_config.get('ignore_patterns', [])

            for ext in extensions:
                for file_path in project_path.rglob(f'*{ext}'):
                    if not any(pattern in str(file_path) for pattern in ignore_patterns):
                        files.append(file_path)

        return files

    def _update_results(self, results: Dict, file_path: Path, file_results: Dict) -> None:
        """Update the overall results with results from a single file."""
        results['files'][str(file_path)] = file_results
        results['summary']['total_files'] += 1
        results['summary']['analyzed_files'] += 1
        
        # Update issue counts
        for issue in file_results.get('issues', []):
            results['summary']['total_issues'] += 1
            
            # Update severity counts
            severity = issue.get('severity', 'unknown')
            results['summary']['issues_by_severity'][severity] = \
                results['summary']['issues_by_severity'].get(severity, 0) + 1
            
            # Update issue type counts
            issue_type = issue.get('type', 'unknown')
            results['summary']['issues_by_type'][issue_type] = \
                results['summary']['issues_by_type'].get(issue_type, 0) + 1

    def generate_report(self, results: Dict, output_path: str) -> None:
        """Generate analysis report."""
        self.report_builder.generate_report(results, output_path)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python main.py <project_path>")
        sys.exit(1)
    
    analyzer = CodeAnalyzer()
    results = analyzer.analyze_project(sys.argv[1])
    analyzer.generate_report(results, 'report.html')
