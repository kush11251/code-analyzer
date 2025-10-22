"""
AI-powered code analysis engine.
Uses machine learning models to provide intelligent code analysis and suggestions.
"""
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForCausalLM
import numpy as np

class AIEngine:
    """AI-powered code analysis engine."""
    
    def __init__(self, config):
        """
        Initialize AI engine with configuration.
        
        Args:
            config: Configuration object containing AI settings
        """
        self.config = config
        self.ai_config = config.get_ai_config()
        
        # Initialize models
        self.tokenizer = None
        self.classification_model = None
        self.generation_model = None
        
        if self.ai_config['enabled']:
            self._initialize_models()

    def _initialize_models(self):
        """Initialize AI models."""
        try:
            # Initialize classification model for vulnerability detection
            self.tokenizer = AutoTokenizer.from_pretrained('microsoft/codebert-base')
            self.classification_model = AutoModelForSequenceClassification.from_pretrained(
                'microsoft/codebert-base',
                num_labels=3  # Low, Medium, High risk
            )
            
            # Initialize code generation model for fix suggestions
            self.generation_model = AutoModelForCausalLM.from_pretrained(
                'Salesforce/codegen-350M-mono'
            )
            
        except Exception as e:
            print(f"Error initializing AI models: {str(e)}")
            self.ai_config['enabled'] = False

    def analyze_code(self, content: str, language: str) -> Dict[str, Any]:
        """
        Analyze code using AI models.
        
        Args:
            content: Source code to analyze
            language: Programming language
            
        Returns:
            Dictionary containing AI analysis results
        """
        if not self.ai_config['enabled']:
            return {}
            
        results = {
            'risk_level': self._assess_risk(content),
            'suggestions': self._generate_suggestions(content, language),
            'similar_patterns': self._find_similar_patterns(content),
            'complexity_analysis': self._analyze_complexity(content)
        }
        
        return results

    def analyze_results(self, analysis_results: Dict) -> Dict[str, Any]:
        """
        Analyze tool results to provide AI-powered insights.
        
        Args:
            analysis_results: Results from code analysis
            
        Returns:
            Dictionary containing AI insights
        """
        if not self.ai_config['enabled']:
            return {}
            
        insights = {
            'summary': self._generate_summary(analysis_results),
            'recommendations': self._generate_recommendations(analysis_results),
            'priority_fixes': self._prioritize_fixes(analysis_results)
        }
        
        return insights

    def suggest_fixes(self, content: str, issues: List[Dict]) -> List[Dict]:
        """
        Generate AI-powered fix suggestions for issues.
        
        Args:
            content: Original source code
            issues: List of detected issues
            
        Returns:
            List of suggested fixes
        """
        if not self.ai_config['enabled']:
            return []
            
        suggestions = []
        for issue in issues:
            fix = self._generate_fix(content, issue)
            if fix:
                suggestions.append(fix)
                
        return suggestions

    def _assess_risk(self, content: str) -> Dict[str, float]:
        """Assess code risk level using classification model."""
        try:
            inputs = self.tokenizer(content, return_tensors='pt', truncation=True, max_length=512)
            outputs = self.classification_model(**inputs)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)
            
            risk_levels = ['low', 'medium', 'high']
            return {
                level: float(prob)
                for level, prob in zip(risk_levels, probabilities[0])
            }
        except Exception as e:
            print(f"Error assessing risk: {str(e)}")
            return {'low': 0.0, 'medium': 0.0, 'high': 0.0}

    def _generate_suggestions(self, content: str, language: str) -> List[Dict]:
        """Generate code improvement suggestions."""
        try:
            # Prepare prompt for the model
            prompt = f"# Improve this {language} code:\n{content}\n# Suggestions:"
            
            inputs = self.tokenizer(prompt, return_tensors='pt', truncation=True)
            outputs = self.generation_model.generate(
                inputs['input_ids'],
                max_length=200,
                num_return_sequences=3,
                temperature=0.7
            )
            
            suggestions = []
            for output in outputs:
                suggestion = self.tokenizer.decode(output, skip_special_tokens=True)
                if suggestion and suggestion != prompt:
                    suggestions.append({
                        'description': suggestion.split('\n')[0],
                        'confidence': self._calculate_confidence(output)
                    })
                    
            return suggestions
        except Exception as e:
            print(f"Error generating suggestions: {str(e)}")
            return []

    def _find_similar_patterns(self, content: str) -> List[Dict]:
        """Find similar code patterns from known vulnerabilities."""
        try:
            # Load vulnerability database
            patterns = self._load_vulnerability_patterns()
            
            similar_patterns = []
            for pattern in patterns:
                similarity = self._calculate_similarity(content, pattern['code'])
                if similarity > self.ai_config['confidence_threshold']:
                    similar_patterns.append({
                        'pattern_type': pattern['type'],
                        'similarity': similarity,
                        'description': pattern['description']
                    })
                    
            return similar_patterns
        except Exception as e:
            print(f"Error finding similar patterns: {str(e)}")
            return []

    def _analyze_complexity(self, content: str) -> Dict[str, Any]:
        """Analyze code complexity using AI models."""
        try:
            # Prepare input for complexity analysis
            inputs = self.tokenizer(content, return_tensors='pt', truncation=True)
            
            # Use model to predict complexity metrics
            with torch.no_grad():
                outputs = self.classification_model(**inputs)
                
            return {
                'cognitive_complexity': self._estimate_cognitive_complexity(outputs),
                'maintainability_index': self._calculate_maintainability(outputs),
                'readability_score': self._calculate_readability(outputs)
            }
        except Exception as e:
            print(f"Error analyzing complexity: {str(e)}")
            return {}

    def _generate_summary(self, results: Dict) -> str:
        """Generate natural language summary of analysis results."""
        try:
            # Prepare summary context
            context = f"""
            Analysis Results Summary:
            - Total Files: {results.get('summary', {}).get('total_files', 0)}
            - Issues Found: {results.get('summary', {}).get('total_issues', 0)}
            """
            
            inputs = self.tokenizer(context, return_tensors='pt', truncation=True)
            outputs = self.generation_model.generate(
                inputs['input_ids'],
                max_length=150,
                num_return_sequences=1,
                temperature=0.3
            )
            
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return "Unable to generate summary"

    def _generate_recommendations(self, results: Dict) -> List[Dict]:
        """Generate prioritized recommendations based on analysis."""
        try:
            recommendations = []
            
            # Analyze issue patterns
            issue_types = results.get('summary', {}).get('issues_by_type', {})
            for issue_type, count in issue_types.items():
                if count > 0:
                    recommendations.append({
                        'type': issue_type,
                        'priority': self._calculate_priority(issue_type, count),
                        'suggestion': self._generate_fix_suggestion(issue_type)
                    })
                    
            return sorted(recommendations, key=lambda x: x['priority'], reverse=True)
        except Exception as e:
            print(f"Error generating recommendations: {str(e)}")
            return []

    def _prioritize_fixes(self, results: Dict) -> List[Dict]:
        """Prioritize fixes based on impact and effort."""
        try:
            fixes = []
            
            # Extract issues
            for file_path, file_results in results.get('files', {}).items():
                for issue in file_results.get('issues', []):
                    fix = {
                        'file': file_path,
                        'issue': issue,
                        'impact': self._calculate_impact(issue),
                        'effort': self._estimate_effort(issue),
                        'priority_score': 0.0
                    }
                    
                    # Calculate priority score
                    fix['priority_score'] = (fix['impact'] * 0.7 + (1 - fix['effort']) * 0.3)
                    fixes.append(fix)
                    
            return sorted(fixes, key=lambda x: x['priority_score'], reverse=True)
        except Exception as e:
            print(f"Error prioritizing fixes: {str(e)}")
            return []

    def _generate_fix(self, content: str, issue: Dict) -> Optional[Dict]:
        """Generate a specific fix for an issue."""
        try:
            # Prepare context for fix generation
            context = f"""
            Code:
            {content}
            
            Issue:
            {issue['message']}
            
            Fix:
            """
            
            inputs = self.tokenizer(context, return_tensors='pt', truncation=True)
            outputs = self.generation_model.generate(
                inputs['input_ids'],
                max_length=200,
                num_return_sequences=1,
                temperature=0.2
            )
            
            fix_suggestion = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            return {
                'original_issue': issue,
                'fix_suggestion': fix_suggestion,
                'confidence': self._calculate_confidence(outputs[0])
            }
        except Exception as e:
            print(f"Error generating fix: {str(e)}")
            return None

    def _load_vulnerability_patterns(self) -> List[Dict]:
        """Load known vulnerability patterns from database."""
        # This is a placeholder - in production, load from actual database
        return [
            {
                'type': 'sql_injection',
                'code': 'query = "SELECT * FROM users WHERE id = " + user_input',
                'description': 'Potential SQL injection vulnerability'
            },
            {
                'type': 'xss',
                'code': 'element.innerHTML = userInput',
                'description': 'Potential XSS vulnerability'
            }
        ]

    def _calculate_similarity(self, code1: str, code2: str) -> float:
        """Calculate similarity between two code snippets."""
        try:
            # Use model embeddings for similarity calculation
            inputs1 = self.tokenizer(code1, return_tensors='pt', truncation=True)
            inputs2 = self.tokenizer(code2, return_tensors='pt', truncation=True)
            
            with torch.no_grad():
                embedding1 = self.classification_model(**inputs1).logits
                embedding2 = self.classification_model(**inputs2).logits
                
            similarity = torch.nn.functional.cosine_similarity(embedding1, embedding2)
            return float(similarity[0])
        except Exception:
            return 0.0

    def _calculate_confidence(self, model_output: torch.Tensor) -> float:
        """Calculate confidence score for model output."""
        try:
            probabilities = torch.nn.functional.softmax(model_output, dim=-1)
            return float(torch.max(probabilities))
        except Exception:
            return 0.0

    def _estimate_cognitive_complexity(self, model_outputs) -> int:
        """Estimate cognitive complexity from model outputs."""
        try:
            scores = model_outputs.logits.mean(dim=1)
            return int(torch.sigmoid(scores[0]) * 25)  # Scale to 0-25 range
        except Exception:
            return 0

    def _calculate_maintainability(self, model_outputs) -> float:
        """Calculate maintainability index from model outputs."""
        try:
            scores = model_outputs.logits.mean(dim=1)
            return float(torch.sigmoid(scores[0]) * 100)  # Scale to 0-100 range
        except Exception:
            return 0.0

    def _calculate_readability(self, model_outputs) -> float:
        """Calculate readability score from model outputs."""
        try:
            scores = model_outputs.logits.mean(dim=1)
            return float(torch.sigmoid(scores[0]) * 10)  # Scale to 0-10 range
        except Exception:
            return 0.0

    def _calculate_priority(self, issue_type: str, count: int) -> float:
        """Calculate priority score for an issue type."""
        # Priority weights for different issue types
        weights = {
            'security': 1.0,
            'vulnerability': 0.9,
            'bug': 0.8,
            'code_smell': 0.6,
            'style': 0.4
        }
        
        base_weight = 0.5
        for key, weight in weights.items():
            if key in issue_type.lower():
                base_weight = weight
                break
                
        return base_weight * min(1.0, count / 10.0)

    def _generate_fix_suggestion(self, issue_type: str) -> str:
        """Generate a fix suggestion based on issue type."""
        try:
            prompt = f"Suggest a fix for {issue_type} issues:"
            
            inputs = self.tokenizer(prompt, return_tensors='pt', truncation=True)
            outputs = self.generation_model.generate(
                inputs['input_ids'],
                max_length=100,
                num_return_sequences=1,
                temperature=0.3
            )
            
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        except Exception:
            return f"Review and fix {issue_type} issues according to best practices"

    def _calculate_impact(self, issue: Dict) -> float:
        """Calculate the impact score of an issue."""
        severity_weights = {
            'critical': 1.0,
            'high': 0.8,
            'medium': 0.5,
            'low': 0.2,
            'info': 0.1
        }
        
        return severity_weights.get(issue.get('severity', 'low'), 0.1)

    def _estimate_effort(self, issue: Dict) -> float:
        """Estimate the effort required to fix an issue."""
        # Effort estimation based on issue type and complexity
        base_effort = 0.5
        
        if 'fix' in issue and isinstance(issue['fix'], str):
            # Lower effort if automated fix is available
            base_effort *= 0.6
            
        if 'complexity' in issue:
            # Increase effort for complex issues
            base_effort *= min(1.0, issue['complexity'] / 10.0)
            
        return min(1.0, base_effort)
