"""
GitHub integration for code analyzer.
"""
import os
from typing import Dict, List, Optional
import requests

class GitHubIntegration:
    """
    Integration with GitHub API for analyzing repositories and creating issues.
    """
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.base_url = 'https://api.github.com'
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        } if self.token else {}
    
    def analyze_repository(self, owner: str, repo: str) -> Dict:
        """
        Analyze a GitHub repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Analysis results
        """
        if not self.token:
            raise ValueError("GitHub token is required")
        
        # Get repository info
        repo_url = f'{self.base_url}/repos/{owner}/{repo}'
        repo_info = self._make_request('GET', repo_url)
        
        # Get languages used
        languages = self._make_request('GET', f'{repo_url}/languages')
        
        # Get security alerts if available
        alerts = self._make_request('GET', f'{repo_url}/code-scanning/alerts')
        
        return {
            'repository': repo_info,
            'languages': languages,
            'security_alerts': alerts
        }
    
    def create_issues(self, owner: str, repo: str, issues: List[Dict]) -> List[Dict]:
        """
        Create GitHub issues from analysis results.
        
        Args:
            owner: Repository owner
            repo: Repository name
            issues: List of issues to create
            
        Returns:
            Created issues
        """
        if not self.token:
            raise ValueError("GitHub token is required")
        
        created_issues = []
        issues_url = f'{self.base_url}/repos/{owner}/{repo}/issues'
        
        for issue in issues:
            # Convert our issue format to GitHub issue format
            github_issue = {
                'title': f'[Code Analyzer] {issue["type"].title()} Issue: {issue["message"]}',
                'body': self._format_issue_body(issue),
                'labels': ['code-analyzer', issue['type'], issue['severity']]
            }
            
            response = self._make_request('POST', issues_url, json=github_issue)
            if response:
                created_issues.append(response)
        
        return created_issues
    
    def _make_request(self, method: str, url: str, **kwargs) -> Optional[Dict]:
        """Make an HTTP request to GitHub API."""
        try:
            response = requests.request(
                method,
                url,
                headers=self.headers,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"GitHub API request failed: {str(e)}")
            return None
    
    def _format_issue_body(self, issue: Dict) -> str:
        """Format an issue for GitHub."""
        return f"""
## Code Analysis Issue

- **Type:** {issue['type']}
- **Severity:** {issue['severity']}
- **Rule:** {issue['rule']}
- **Line:** {issue.get('line', 'N/A')}

### Description
{issue['message']}

### Fix Suggestion
{issue.get('fix_suggestion', 'No fix suggestion available.')}

---
*This issue was automatically created by Code Analyzer*
"""
