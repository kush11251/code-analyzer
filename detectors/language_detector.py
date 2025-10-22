"""
Language detection module for the code analyzer.
Identifies programming languages based on file extensions and content analysis.
"""
from pathlib import Path
from typing import Optional, Dict, List
import re

class LanguageDetector:
    def __init__(self, config):
        self.config = config
        self._setup_language_patterns()

    def _setup_language_patterns(self):
        """Setup language-specific patterns for content-based detection."""
        self.language_patterns = {
            'python': {
                'shebang': r'^#!.*python',
                'imports': r'^(?:import|from)\s+\w+',
                'decorators': r'@\w+',
                'keywords': r'\b(?:def|class|lambda|yield|async|await)\b'
            },
            'javascript': {
                'imports': r'^(?:import|export)\s+.*?(?:from\s+[\'"]|[\'"];?$)',
                'jsx': r'<[\w.]+>.*?</[\w.]+>',
                'keywords': r'\b(?:const|let|var|function|class|async|await)\b',
                'module_exports': r'module\.exports\s*=|export\s+(?:default|const|let|var|function|class)'
            },
            'java': {
                'package': r'^package\s+[\w.]+;',
                'imports': r'^import\s+[\w.]+;',
                'class_def': r'(?:public|private|protected)\s+class\s+\w+',
                'annotations': r'@\w+'
            }
        }

    def detect_language(self, file_path: Path) -> Optional[str]:
        """
        Detect the programming language of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Language name if detected, None otherwise
        """
        # Check by file extension first
        extension = file_path.suffix.lower()
        lang_by_ext = self._detect_by_extension(extension)
        if lang_by_ext:
            # Verify with content analysis
            if self._verify_language_by_content(file_path, lang_by_ext):
                return lang_by_ext

        # If extension detection fails or needs verification,
        # try content-based detection
        return self._detect_by_content(file_path)

    def _detect_by_extension(self, extension: str) -> Optional[str]:
        """Detect language based on file extension."""
        for language, config in self.config.settings['languages'].items():
            if extension in config.get('extensions', []):
                return language
        return None

    def _verify_language_by_content(self, file_path: Path, language: str) -> bool:
        """Verify detected language by analyzing file content."""
        try:
            content = file_path.read_text()
            patterns = self.language_patterns.get(language, {})
            
            # Check for language-specific patterns
            matches = 0
            for pattern in patterns.values():
                if re.search(pattern, content, re.MULTILINE):
                    matches += 1
            
            # Require at least 2 pattern matches for verification
            return matches >= 2
        except Exception:
            return False

    def _detect_by_content(self, file_path: Path) -> Optional[str]:
        """Detect language by analyzing file content."""
        try:
            content = file_path.read_text()
            scores = self._calculate_language_scores(content)
            
            # Return language with highest score if it meets threshold
            if scores:
                best_match = max(scores.items(), key=lambda x: x[1])
                if best_match[1] >= 2:  # Minimum score threshold
                    return best_match[0]
        except Exception:
            pass
        return None

    def _calculate_language_scores(self, content: str) -> Dict[str, int]:
        """Calculate confidence scores for each language based on content patterns."""
        scores = {}
        
        for language, patterns in self.language_patterns.items():
            score = 0
            for pattern in patterns.values():
                matches = re.findall(pattern, content, re.MULTILINE)
                score += len(matches)
            if score > 0:
                scores[language] = score
                
        return scores

    def get_supported_languages(self) -> List[str]:
        """Get list of supported programming languages."""
        return list(self.language_patterns.keys())
