"""
Core configuration for the code analyzer tool.
This module handles all configuration settings and initialization.
"""
from pathlib import Path
from typing import Dict, List, Optional
import yaml

class AnalyzerConfig:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or str(Path.home() / '.code_analyzer' / 'config.yml')
        self.settings = self._load_default_config()
        
    def _load_default_config(self) -> Dict:
        """Load default configuration settings."""
        return {
            'logging': {
                'level': 'INFO',
                'file': None,
                'format': {
                    'console': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    'file': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
                }
            },
            'languages': {
                'python': {
                    'enabled': True,
                    'extensions': ['.py'],
                    'ignore_patterns': ['*venv*', '*.pyc', '__pycache__'],
                    'rules': {
                        'quality': ['complexity', 'style', 'maintainability'],
                        'security': ['injection', 'authentication', 'data_validation']
                    }
                },
                'javascript': {
                    'enabled': True,
                    'extensions': ['.js', '.jsx', '.ts', '.tsx'],
                    'ignore_patterns': ['node_modules', 'dist', 'build'],
                    'rules': {
                        'quality': ['complexity', 'style', 'best_practices'],
                        'security': ['xss', 'injection', 'authentication']
                    }
                },
                'java': {
                    'enabled': True,
                    'extensions': ['.java'],
                    'ignore_patterns': ['target', 'build'],
                    'rules': {
                        'quality': ['complexity', 'style', 'design'],
                        'security': ['injection', 'authentication', 'validation']
                    }
                }
            },
            'analysis': {
                'max_file_size': 1024 * 1024,  # 1MB
                'parallel_processing': True,
                'max_workers': 4
            },
            'reporting': {
                'format': 'html',
                'output_dir': 'reports',
                'severity_levels': ['critical', 'high', 'medium', 'low', 'info']
            },
            'ai_assistance': {
                'enabled': True,
                'model': 'gpt-4',
                'confidence_threshold': 0.8
            }
        }
    
    def load_user_config(self) -> None:
        """Load user configuration and merge with defaults."""
        try:
            with open(self.config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    self._merge_config(user_config)
        except FileNotFoundError:
            pass  # Use defaults if no user config exists
    
    def _merge_config(self, user_config: Dict) -> None:
        """Merge user configuration with default settings."""
        def merge_dicts(default: Dict, user: Dict) -> Dict:
            for key, value in user.items():
                if key in default and isinstance(default[key], dict):
                    merge_dicts(default[key], value)
                else:
                    default[key] = value
            return default
        
        self.settings = merge_dicts(self.settings, user_config)
    
    def get_language_config(self, language: str) -> Dict:
        """Get configuration for a specific language."""
        return self.settings['languages'].get(language, {})
    
    def get_enabled_languages(self) -> List[str]:
        """Get list of enabled languages."""
        return [lang for lang, config in self.settings['languages'].items()
                if config.get('enabled', False)]
    
    def get_analysis_config(self) -> Dict:
        """Get analysis configuration."""
        return self.settings['analysis']
    
    def get_reporting_config(self) -> Dict:
        """Get reporting configuration."""
        return self.settings['reporting']
    
    def get_ai_config(self) -> Dict:
        """Get AI assistance configuration."""
        return self.settings['ai_assistance']
        
    def get_logging_config(self) -> Dict:
        """Get logging configuration."""
        return self.settings['logging']
