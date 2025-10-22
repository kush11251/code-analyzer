"""
Report generation module.
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import jinja2
import json

class ReportBuilder:
    """
    Generates analysis reports in various formats.
    """
    def __init__(self, config):
        self.config = config
        self.template_dir = Path(__file__).parent / 'templates'
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.template_dir)),
            autoescape=jinja2.select_autoescape(['html'])
        )
        
    def generate_report(self, results: Dict, output_path: str) -> None:
        """
        Generate an analysis report.
        
        Args:
            results: Analysis results
            output_path: Path to save the report
        """
        # Add timestamp to results
        results['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Get report format from output file extension or config
        format = Path(output_path).suffix[1:] or self.config.get_reporting_config()['format']
        
        # Generate report in specified format
        if format == 'html':
            self._generate_html_report(results, output_path)
        elif format == 'md' or format == 'markdown':
            self._generate_markdown_report(results, output_path)
        elif format == 'json':
            self._generate_json_report(results, output_path)
        else:
            raise ValueError(f"Unsupported report format: {format}")
    
    def _generate_html_report(self, results: Dict, output_path: str) -> None:
        """Generate HTML report."""
        template = self.env.get_template('html_report.html')
        html = template.render(**results)
        
        with open(output_path, 'w') as f:
            f.write(html)
    
    def _generate_markdown_report(self, results: Dict, output_path: str) -> None:
        """Generate Markdown report."""
        template = self.env.get_template('markdown_report.md')
        markdown = template.render(**results)
        
        with open(output_path, 'w') as f:
            f.write(markdown)
    
    def _generate_json_report(self, results: Dict, output_path: str) -> None:
        """Generate JSON report."""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
    
    def _format_code_snippet(self, code: str, line_number: int,
                         context_lines: int = 3) -> Optional[str]:
        """
        Format a code snippet with line numbers and highlighting.
        
        Args:
            code: Source code
            line_number: Line number to highlight
            context_lines: Number of context lines before and after
            
        Returns:
            Formatted code snippet
        """
        if not code:
            return None
            
        lines = code.split('\n')
        start = max(0, line_number - context_lines - 1)
        end = min(len(lines), line_number + context_lines)
        
        snippet_lines = []
        for i in range(start, end):
            prefix = '> ' if i == line_number - 1 else '  '
            snippet_lines.append(f"{prefix}{i+1:4d} | {lines[i]}")
        
        return '\n'.join(snippet_lines)
    
    def _add_code_snippets(self, results: Dict) -> Dict:
        """
        Add formatted code snippets to results.
        
        Args:
            results: Analysis results
            
        Returns:
            Results with code snippets added
        """
        for file_path, file_results in results['files'].items():
            try:
                with open(file_path) as f:
                    code = f.read()
                
                for issue in file_results.get('issues', []):
                    if 'line' in issue:
                        issue['code_snippet'] = self._format_code_snippet(
                            code, issue['line']
                        )
            except Exception as e:
                print(f"Error adding code snippet for {file_path}: {str(e)}")
        
        return results
