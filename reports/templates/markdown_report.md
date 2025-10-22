# Code Analysis Report

Generated on {{ timestamp }}

## Summary

- Total Files Analyzed: {{ summary.total_files }}
- Total Issues Found: {{ summary.total_issues }}

### Issues by Severity

{% for severity, count in summary.issues_by_severity.items() %}
- {{ severity|title }}: {{ count }}
{% endfor %}

### Issues by Type

{% for type, count in summary.issues_by_type.items() %}
- {{ type|title }}: {{ count }}
{% endfor %}

{% if ai_insights %}
## AI Insights

{{ ai_insights.summary }}

### Recommendations

{% for rec in ai_insights.recommendations %}
- {{ rec }}
{% endfor %}
{% endif %}

## Detailed Analysis

{% for file_path, file_results in files.items() %}
### {{ file_path }}

Language: {{ file_results.language }}

{% for issue in file_results.issues %}
#### {{ issue.severity|upper }}: {{ issue.message }}

- Type: {{ issue.type }}
- Line: {{ issue.line }}
{% if issue.code_snippet %}
```{{ file_results.language }}
{{ issue.code_snippet }}
```
{% endif %}
{% if issue.fix_suggestion %}
**Suggestion:** {{ issue.fix_suggestion }}
{% endif %}

{% endfor %}
{% endfor %}
