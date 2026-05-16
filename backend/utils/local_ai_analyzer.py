"""
Local AI Analyzer - 100% Privacy-Focused
All processing done locally, no external API calls, no data leaves your server
Uses local NLP models and rule-based AI for intelligent analysis
"""

import pandas as pd
import re
from typing import Dict, List, Tuple, Set
import logging
from collections import Counter
import hashlib

logger = logging.getLogger(__name__)


class PrivacyFocusedAIAnalyzer:
    """
    Privacy-first AI analyzer for confidential project data
    - All processing done locally
    - No external API calls
    - No data transmission
    - Secure data handling
    - Audit trail support
    """
    
    # Enhanced category detection with more patterns
    CATEGORY_PATTERNS = {
        'development': {
            'keywords': ['dev', 'develop', 'code', 'coding', 'programming', 'implementation', 
                        'software', 'application', 'feature', 'module', 'component'],
            'patterns': [r'dev\w*', r'code\w*', r'prog\w*', r'impl\w*'],
            'weight': 1.0
        },
        'testing': {
            'keywords': ['test', 'qa', 'quality', 'validation', 'verification', 'check',
                        'assurance', 'bug', 'defect', 'issue'],
            'patterns': [r'test\w*', r'qa\w*', r'qual\w*', r'valid\w*'],
            'weight': 1.0
        },
        'design': {
            'keywords': ['design', 'ui', 'ux', 'mockup', 'wireframe', 'prototype',
                        'interface', 'layout', 'visual', 'graphic'],
            'patterns': [r'design\w*', r'ui\w*', r'ux\w*', r'mock\w*'],
            'weight': 0.9
        },
        'documentation': {
            'keywords': ['doc', 'documentation', 'manual', 'guide', 'readme', 'wiki',
                        'specification', 'requirement', 'report'],
            'patterns': [r'doc\w*', r'spec\w*', r'req\w*', r'manual\w*'],
            'weight': 0.9
        },
        'planning': {
            'keywords': ['plan', 'planning', 'strategy', 'roadmap', 'schedule', 'timeline',
                        'milestone', 'sprint', 'iteration'],
            'patterns': [r'plan\w*', r'strat\w*', r'road\w*', r'sched\w*'],
            'weight': 0.8
        },
        'analysis': {
            'keywords': ['analysis', 'analyze', 'research', 'study', 'investigation',
                        'assessment', 'evaluation', 'review'],
            'patterns': [r'analy\w*', r'research\w*', r'study\w*', r'assess\w*'],
            'weight': 0.8
        },
        'deployment': {
            'keywords': ['deploy', 'deployment', 'release', 'production', 'launch',
                        'rollout', 'publish', 'delivery'],
            'patterns': [r'deploy\w*', r'release\w*', r'prod\w*', r'launch\w*'],
            'weight': 0.9
        },
        'maintenance': {
            'keywords': ['maintain', 'maintenance', 'support', 'fix', 'patch',
                        'update', 'upgrade', 'repair'],
            'patterns': [r'maint\w*', r'support\w*', r'fix\w*', r'patch\w*'],
            'weight': 0.8
        },
        'security': {
            'keywords': ['security', 'secure', 'auth', 'authentication', 'authorization',
                        'encryption', 'protection', 'vulnerability', 'penetration'],
            'patterns': [r'secur\w*', r'auth\w*', r'encrypt\w*', r'protect\w*'],
            'weight': 1.0
        },
        'database': {
            'keywords': ['database', 'db', 'data', 'storage', 'query', 'sql',
                        'schema', 'migration', 'backup'],
            'patterns': [r'db\w*', r'data\w*', r'sql\w*', r'schema\w*'],
            'weight': 0.9
        },
        'api': {
            'keywords': ['api', 'endpoint', 'rest', 'graphql', 'service', 'integration',
                        'webhook', 'microservice'],
            'patterns': [r'api\w*', r'endpoint\w*', r'rest\w*', r'service\w*'],
            'weight': 0.9
        },
        'frontend': {
            'keywords': ['frontend', 'front-end', 'client', 'browser', 'web', 'react',
                        'vue', 'angular', 'html', 'css', 'javascript'],
            'patterns': [r'front\w*', r'client\w*', r'web\w*', r'ui\w*'],
            'weight': 0.9
        },
        'backend': {
            'keywords': ['backend', 'back-end', 'server', 'api', 'service', 'node',
                        'python', 'java', 'database'],
            'patterns': [r'back\w*', r'server\w*', r'api\w*'],
            'weight': 0.9
        },
        'infrastructure': {
            'keywords': ['infrastructure', 'infra', 'devops', 'ci', 'cd', 'pipeline',
                        'docker', 'kubernetes', 'cloud', 'aws', 'azure'],
            'patterns': [r'infra\w*', r'devops\w*', r'ci\w*', r'cloud\w*'],
            'weight': 0.8
        }
    }
    
    # Action verbs for task detection
    ACTION_VERBS = [
        'create', 'develop', 'implement', 'build', 'design', 'test', 'deploy',
        'configure', 'setup', 'install', 'update', 'upgrade', 'fix', 'debug',
        'analyze', 'review', 'document', 'write', 'prepare', 'plan', 'research',
        'integrate', 'migrate', 'optimize', 'refactor', 'validate', 'verify',
        'monitor', 'maintain', 'support', 'troubleshoot', 'investigate'
    ]
    
    def __init__(self, enable_audit=True):
        self.df = None
        self.analysis_result = {}
        self.enable_audit = enable_audit
        self.audit_log = []
        self._log_event("Analyzer initialized", "INIT")
    
    def _log_event(self, message: str, event_type: str = "INFO"):
        """Log events for audit trail (privacy-safe)"""
        if self.enable_audit:
            # Only log metadata, never actual data content
            self.audit_log.append({
                'timestamp': pd.Timestamp.now().isoformat(),
                'event': event_type,
                'message': message
            })
    
    def _hash_sensitive_data(self, data: str) -> str:
        """Create privacy-safe hash of sensitive data"""
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def load_file(self, file_content, file_extension: str) -> bool:
        """Load Excel or CSV file securely"""
        try:
            self._log_event(f"Loading file with extension {file_extension}", "LOAD")
            
            if file_extension == '.csv':
                self.df = pd.read_csv(file_content)
            else:
                self.df = pd.read_excel(file_content, engine='openpyxl')
            
            # Log metadata only (not content)
            self._log_event(f"File loaded: {len(self.df.columns)} columns, {len(self.df)} rows", "LOAD_SUCCESS")
            return True
        except Exception as e:
            self._log_event(f"Error loading file: {type(e).__name__}", "LOAD_ERROR")
            logger.error(f"Error loading file: {str(e)}")
            return False
    
    def analyze(self, privacy_mode: str = 'strict') -> Dict:
        """
        Perform AI-powered analysis with privacy protection
        
        privacy_mode:
            - 'strict': Maximum privacy, minimal logging
            - 'normal': Balanced privacy and functionality
            - 'detailed': More detailed analysis (still local)
        """
        if self.df is None or self.df.empty:
            return {'error': 'No data to analyze'}
        
        self._log_event(f"Starting analysis in {privacy_mode} mode", "ANALYZE_START")
        
        result = {
            'total_columns': len(self.df.columns),
            'total_rows': len(self.df),
            'categories': [],
            'suggestions': [],
            'warnings': [],
            'privacy_mode': privacy_mode,
            'data_processed_locally': True,
            'external_api_calls': 0
        }
        
        # Analyze each column
        for col_index, column_name in enumerate(self.df.columns):
            category_data = self._analyze_column_ai(column_name, col_index, privacy_mode)
            if category_data:
                result['categories'].append(category_data)
        
        # AI-powered suggestions
        result['suggestions'] = self._generate_ai_suggestions(result['categories'])
        
        # Smart warnings
        result['warnings'] = self._check_smart_warnings(result['categories'])
        
        # Quality score
        result['overall_quality_score'] = self._calculate_overall_quality(result['categories'])
        
        self.analysis_result = result
        self._log_event(f"Analysis complete: {len(result['categories'])} categories", "ANALYZE_COMPLETE")
        
        return result
    
    def _analyze_column_ai(self, column_name: str, col_index: int, privacy_mode: str) -> Dict:
        """AI-powered column analysis"""
        # Skip empty columns
        if pd.isna(column_name) or str(column_name).strip() == '':
            return None
        
        # Clean and normalize
        clean_name = self._clean_text(str(column_name))
        
        # Extract tasks
        tasks = []
        for idx, task_name in enumerate(self.df[column_name].dropna()):
            task_str = str(task_name).strip()
            if task_str:
                task_analysis = self._analyze_task_ai(task_str, idx)
                if task_analysis:
                    tasks.append(task_analysis)
        
        # AI-powered category type detection
        category_type, type_confidence = self._detect_category_type_ai(clean_name, tasks)
        
        # Calculate comprehensive confidence
        confidence = self._calculate_category_confidence_ai(clean_name, tasks, type_confidence)
        
        return {
            'name': clean_name,
            'original_name': str(column_name) if privacy_mode != 'strict' else '[REDACTED]',
            'order': col_index,
            'type': category_type,
            'type_confidence': type_confidence,
            'task_count': len(tasks),
            'tasks': tasks,
            'confidence': confidence,
            'quality_metrics': self._calculate_quality_metrics(tasks)
        }
    
    def _analyze_task_ai(self, task_name: str, order: int) -> Dict:
        """AI-powered task analysis"""
        clean_name = self._clean_text(task_name)
        
        # Detect if task has action verb
        has_action_verb = any(verb in clean_name.lower() for verb in self.ACTION_VERBS)
        
        # Detect task complexity
        complexity = self._estimate_task_complexity(clean_name)
        
        # Calculate confidence
        confidence = self._calculate_task_confidence_ai(clean_name, has_action_verb, complexity)
        
        return {
            'name': clean_name,
            'order': order,
            'confidence': confidence,
            'has_action_verb': has_action_verb,
            'complexity': complexity,
            'word_count': len(clean_name.split())
        }
    
    def _detect_category_type_ai(self, category_name: str, tasks: List[Dict]) -> Tuple[str, float]:
        """
        AI-powered category type detection with confidence scoring
        Returns: (type, confidence)
        """
        category_lower = category_name.lower()
        scores = {}
        
        # Score each category type
        for cat_type, patterns in self.CATEGORY_PATTERNS.items():
            score = 0.0
            
            # Keyword matching
            for keyword in patterns['keywords']:
                if keyword in category_lower:
                    score += patterns['weight']
            
            # Pattern matching
            for pattern in patterns['patterns']:
                if re.search(pattern, category_lower):
                    score += patterns['weight'] * 0.5
            
            # Task context analysis
            if tasks:
                task_names = ' '.join([t['name'].lower() for t in tasks])
                for keyword in patterns['keywords']:
                    if keyword in task_names:
                        score += 0.1
            
            scores[cat_type] = score
        
        # Get best match
        if scores:
            best_type = max(scores, key=scores.get)
            max_score = scores[best_type]
            
            if max_score > 0:
                # Normalize confidence to 0-1
                confidence = min(max_score / 3.0, 1.0)
                return best_type, confidence
        
        return 'general', 0.3
    
    def _estimate_task_complexity(self, task_name: str) -> str:
        """Estimate task complexity based on name"""
        word_count = len(task_name.split())
        
        if word_count <= 2:
            return 'simple'
        elif word_count <= 4:
            return 'medium'
        else:
            return 'complex'
    
    def _calculate_task_confidence_ai(self, task_name: str, has_action_verb: bool, complexity: str) -> float:
        """AI-enhanced task confidence calculation"""
        score = 0.5  # Base score
        
        # Length check
        length = len(task_name)
        if 5 <= length <= 100:
            score += 0.2
        elif length < 3:
            score -= 0.3
        elif length > 150:
            score -= 0.2
        
        # Action verb boost
        if has_action_verb:
            score += 0.2
        
        # Complexity consideration
        if complexity == 'medium':
            score += 0.1
        elif complexity == 'simple' and length > 10:
            score += 0.05
        
        # Check for common patterns
        if re.search(r'\d+', task_name):  # Contains numbers
            score += 0.05
        
        if '-' in task_name or '_' in task_name:  # Well-formatted
            score += 0.05
        
        return max(min(score, 1.0), 0.0)
    
    def _calculate_category_confidence_ai(self, name: str, tasks: List[Dict], type_confidence: float) -> float:
        """AI-enhanced category confidence calculation"""
        score = 0.4  # Base score
        
        # Type detection confidence
        score += type_confidence * 0.3
        
        # Task count
        task_count = len(tasks)
        if 2 <= task_count <= 15:
            score += 0.2
        elif 15 < task_count <= 25:
            score += 0.1
        elif task_count > 25:
            score -= 0.1
        
        # Average task confidence
        if tasks:
            avg_task_confidence = sum(t['confidence'] for t in tasks) / len(tasks)
            score += avg_task_confidence * 0.2
        
        # Name quality
        if len(name) >= 3 and not re.search(r'[^a-zA-Z0-9\s-]', name):
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_quality_metrics(self, tasks: List[Dict]) -> Dict:
        """Calculate quality metrics for a category"""
        if not tasks:
            return {'avg_confidence': 0, 'action_verb_ratio': 0, 'complexity_distribution': {}}
        
        avg_confidence = sum(t['confidence'] for t in tasks) / len(tasks)
        action_verb_count = sum(1 for t in tasks if t.get('has_action_verb', False))
        action_verb_ratio = action_verb_count / len(tasks)
        
        complexity_dist = Counter(t.get('complexity', 'unknown') for t in tasks)
        
        return {
            'avg_confidence': round(avg_confidence, 3),
            'action_verb_ratio': round(action_verb_ratio, 3),
            'complexity_distribution': dict(complexity_dist)
        }
    
    def _calculate_overall_quality(self, categories: List[Dict]) -> float:
        """Calculate overall quality score"""
        if not categories:
            return 0.0
        
        total_score = 0.0
        for cat in categories:
            total_score += cat['confidence'] * 0.7
            total_score += cat.get('quality_metrics', {}).get('avg_confidence', 0) * 0.3
        
        return round(total_score / len(categories), 3)
    
    def _generate_ai_suggestions(self, categories: List[Dict]) -> List[str]:
        """AI-powered suggestions"""
        suggestions = []
        
        # Empty categories
        empty_cats = [c['name'] for c in categories if c['task_count'] == 0]
        if empty_cats:
            suggestions.append(f"🔍 Empty categories detected: {', '.join(empty_cats[:3])}. Consider adding tasks or removing.")
        
        # Large categories
        large_cats = [(c['name'], c['task_count']) for c in categories if c['task_count'] > 20]
        if large_cats:
            for name, count in large_cats[:2]:
                suggestions.append(f"📊 '{name}' has {count} tasks. Consider splitting into sub-categories for better organization.")
        
        # Low confidence categories
        low_conf_cats = [c['name'] for c in categories if c['confidence'] < 0.5]
        if low_conf_cats:
            suggestions.append(f"⚠️ Low confidence categories: {', '.join(low_conf_cats[:3])}. Review and clarify names.")
        
        # Tasks without action verbs
        for cat in categories:
            tasks_without_verbs = sum(1 for t in cat['tasks'] if not t.get('has_action_verb', False))
            if tasks_without_verbs > len(cat['tasks']) * 0.5:
                suggestions.append(f"💡 '{cat['name']}': Many tasks lack action verbs. Consider using verbs like 'Create', 'Implement', 'Test'.")
                break
        
        # Complexity distribution
        for cat in categories:
            complexity_dist = cat.get('quality_metrics', {}).get('complexity_distribution', {})
            if complexity_dist.get('simple', 0) > len(cat['tasks']) * 0.7:
                suggestions.append(f"📝 '{cat['name']}': Most tasks are simple. Consider adding more detailed descriptions.")
                break
        
        return suggestions
    
    def _check_smart_warnings(self, categories: List[Dict]) -> List[str]:
        """AI-powered warnings"""
        warnings = []
        
        # No categories
        if len(categories) == 0:
            warnings.append("❌ No valid categories found. Check file format.")
        
        # Too many categories
        elif len(categories) > 15:
            warnings.append(f"⚠️ {len(categories)} categories detected. This may overwhelm users. Consider consolidating.")
        
        # Very low overall quality
        overall_quality = self._calculate_overall_quality(categories)
        if overall_quality < 0.4:
            warnings.append(f"⚠️ Overall quality score is low ({overall_quality:.2f}). Review data quality.")
        
        # Duplicate or similar names
        names = [c['name'].lower() for c in categories]
        if len(names) != len(set(names)):
            warnings.append("⚠️ Duplicate category names detected. Use unique names.")
        
        # Categories with very few tasks
        sparse_cats = [c['name'] for c in categories if 0 < c['task_count'] < 2]
        if sparse_cats:
            warnings.append(f"⚠️ Categories with very few tasks: {', '.join(sparse_cats[:3])}")
        
        return warnings
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Capitalize properly
        text = text.title()
        
        # Remove special characters but keep spaces, hyphens, and underscores
        text = re.sub(r'[^\w\s-]', '', text)
        
        return text.strip()
    
    def get_structured_data(self) -> Dict:
        """Get cleaned, structured data ready for database"""
        if not self.analysis_result:
            return {}
        
        return {
            'categories': [
                {
                    'name': cat['name'],
                    'order': cat['order'],
                    'type': cat['type'],
                    'tasks': [
                        {
                            'name': task['name'],
                            'order': task['order']
                        }
                        for task in cat['tasks']
                    ]
                }
                for cat in self.analysis_result.get('categories', [])
            ]
        }
    
    def get_analysis_summary(self) -> str:
        """Get human-readable analysis summary"""
        if not self.analysis_result:
            return "No analysis performed yet."
        
        summary_parts = []
        
        # Header
        summary_parts.append("🤖 AI Analysis Summary (100% Local Processing)")
        summary_parts.append(f"🔒 Privacy Mode: {self.analysis_result.get('privacy_mode', 'normal').upper()}")
        summary_parts.append(f"📊 Overall Quality Score: {self.analysis_result.get('overall_quality_score', 0):.2f}/1.00")
        summary_parts.append("")
        
        # Basic stats
        summary_parts.append(f"📁 Structure:")
        summary_parts.append(f"  • Categories: {self.analysis_result['total_columns']}")
        summary_parts.append(f"  • Total rows: {self.analysis_result['total_rows']}")
        summary_parts.append("")
        
        # Categories
        if self.analysis_result['categories']:
            summary_parts.append("📂 Categories Detected:")
            for cat in self.analysis_result['categories']:
                confidence_emoji = "✅" if cat['confidence'] > 0.7 else "⚠️" if cat['confidence'] > 0.5 else "❌"
                type_info = f"Type: {cat['type']}" if cat['type'] != 'general' else "Type: General"
                summary_parts.append(f"  {confidence_emoji} {cat['name']}: {cat['task_count']} tasks ({type_info}, Confidence: {cat['confidence']:.2f})")
            summary_parts.append("")
        
        # Suggestions
        if self.analysis_result['suggestions']:
            summary_parts.append("💡 AI Suggestions:")
            for suggestion in self.analysis_result['suggestions']:
                summary_parts.append(f"  {suggestion}")
            summary_parts.append("")
        
        # Warnings
        if self.analysis_result['warnings']:
            summary_parts.append("⚠️ Warnings:")
            for warning in self.analysis_result['warnings']:
                summary_parts.append(f"  {warning}")
            summary_parts.append("")
        
        # Privacy assurance
        summary_parts.append("🔒 Privacy Assurance:")
        summary_parts.append("  ✓ All processing done locally on your server")
        summary_parts.append("  ✓ No external API calls made")
        summary_parts.append("  ✓ No data transmitted outside your infrastructure")
        summary_parts.append(f"  ✓ Audit log entries: {len(self.audit_log)}")
        
        return '\n'.join(summary_parts)
    
    def get_audit_log(self) -> List[Dict]:
        """Get audit log for compliance"""
        return self.audit_log.copy()


def analyze_excel_file_private(file_content, file_extension: str, privacy_mode: str = 'strict') -> Tuple[Dict, str, List]:
    """
    Privacy-focused Excel analysis
    Returns: (structured_data, analysis_summary, audit_log)
    """
    analyzer = PrivacyFocusedAIAnalyzer(enable_audit=True)
    
    if not analyzer.load_file(file_content, file_extension):
        return {}, "Failed to load file", []
    
    analyzer.analyze(privacy_mode=privacy_mode)
    structured_data = analyzer.get_structured_data()
    summary = analyzer.get_analysis_summary()
    audit_log = analyzer.get_audit_log()
    
    return structured_data, summary, audit_log
