"""
Excel Analyzer with AI-powered intelligence
Analyzes uploaded Excel files to intelligently detect categories and tasks
"""

import pandas as pd
import re
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class ExcelAnalyzer:
    """Intelligent Excel file analyzer for project templates"""
    
    # Common category keywords for intelligent detection
    CATEGORY_KEYWORDS = {
        'development': ['dev', 'develop', 'code', 'coding', 'programming', 'implementation'],
        'testing': ['test', 'qa', 'quality', 'validation', 'verification'],
        'design': ['design', 'ui', 'ux', 'mockup', 'wireframe', 'prototype'],
        'documentation': ['doc', 'documentation', 'manual', 'guide', 'readme'],
        'planning': ['plan', 'planning', 'strategy', 'roadmap', 'schedule'],
        'analysis': ['analysis', 'analyze', 'research', 'study', 'investigation'],
        'deployment': ['deploy', 'deployment', 'release', 'production', 'launch'],
        'maintenance': ['maintain', 'maintenance', 'support', 'fix', 'patch'],
        'review': ['review', 'audit', 'inspection', 'evaluation', 'assessment'],
        'management': ['manage', 'management', 'admin', 'coordination', 'oversight']
    }
    
    def __init__(self):
        self.df = None
        self.analysis_result = {}
    
    def load_file(self, file_content, file_extension: str) -> bool:
        """Load Excel or CSV file"""
        try:
            if file_extension == '.csv':
                self.df = pd.read_csv(file_content)
            else:
                self.df = pd.read_excel(file_content)
            return True
        except Exception as e:
            logger.error(f"Error loading file: {str(e)}")
            return False
    
    def analyze(self) -> Dict:
        """
        Perform intelligent analysis of the Excel structure
        Returns structured data with categories and tasks
        """
        if self.df is None or self.df.empty:
            return {'error': 'No data to analyze'}
        
        result = {
            'total_columns': len(self.df.columns),
            'total_rows': len(self.df),
            'categories': [],
            'suggestions': [],
            'warnings': []
        }
        
        # Analyze each column as a potential category
        for col_index, column_name in enumerate(self.df.columns):
            category_data = self._analyze_column(column_name, col_index)
            if category_data:
                result['categories'].append(category_data)
        
        # Generate suggestions
        result['suggestions'] = self._generate_suggestions(result['categories'])
        
        # Check for warnings
        result['warnings'] = self._check_warnings(result['categories'])
        
        self.analysis_result = result
        return result
    
    def _analyze_column(self, column_name: str, col_index: int) -> Dict:
        """Analyze a single column"""
        # Skip empty or unnamed columns
        if pd.isna(column_name) or str(column_name).strip() == '':
            return None
        
        # Clean column name
        clean_name = self._clean_text(str(column_name))
        
        # Get tasks from this column
        tasks = []
        for idx, task_name in enumerate(self.df[column_name].dropna()):
            task_str = str(task_name).strip()
            if task_str:
                tasks.append({
                    'name': self._clean_text(task_str),
                    'original': task_str,
                    'order': idx,
                    'confidence': self._calculate_task_confidence(task_str)
                })
        
        # Detect category type
        category_type = self._detect_category_type(clean_name)
        
        return {
            'name': clean_name,
            'original_name': str(column_name),
            'order': col_index,
            'type': category_type,
            'task_count': len(tasks),
            'tasks': tasks,
            'confidence': self._calculate_category_confidence(clean_name, tasks)
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Capitalize properly
        text = text.title()
        
        # Remove special characters but keep spaces and hyphens
        text = re.sub(r'[^\w\s-]', '', text)
        
        return text.strip()
    
    def _detect_category_type(self, category_name: str) -> str:
        """Detect the type of category based on keywords"""
        category_lower = category_name.lower()
        
        for cat_type, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in category_lower:
                    return cat_type
        
        return 'general'
    
    def _calculate_category_confidence(self, name: str, tasks: List[Dict]) -> float:
        """Calculate confidence score for category (0-1)"""
        score = 0.5  # Base score
        
        # Boost if name matches known patterns
        if self._detect_category_type(name) != 'general':
            score += 0.2
        
        # Boost if has reasonable number of tasks
        if 2 <= len(tasks) <= 20:
            score += 0.2
        
        # Boost if tasks have good confidence
        if tasks:
            avg_task_confidence = sum(t['confidence'] for t in tasks) / len(tasks)
            score += avg_task_confidence * 0.1
        
        return min(score, 1.0)
    
    def _calculate_task_confidence(self, task_name: str) -> float:
        """Calculate confidence score for task (0-1)"""
        score = 0.5  # Base score
        
        # Boost if reasonable length
        if 5 <= len(task_name) <= 100:
            score += 0.2
        
        # Boost if contains action words
        action_words = ['create', 'develop', 'test', 'design', 'implement', 
                       'review', 'analyze', 'build', 'deploy', 'configure']
        if any(word in task_name.lower() for word in action_words):
            score += 0.2
        
        # Penalize if too short or too long
        if len(task_name) < 3:
            score -= 0.3
        if len(task_name) > 150:
            score -= 0.2
        
        return max(min(score, 1.0), 0.0)
    
    def _generate_suggestions(self, categories: List[Dict]) -> List[str]:
        """Generate helpful suggestions based on analysis"""
        suggestions = []
        
        # Check for empty categories
        empty_cats = [c['name'] for c in categories if c['task_count'] == 0]
        if empty_cats:
            suggestions.append(f"Empty categories detected: {', '.join(empty_cats)}. Consider removing or adding tasks.")
        
        # Check for too many tasks
        large_cats = [c['name'] for c in categories if c['task_count'] > 20]
        if large_cats:
            suggestions.append(f"Categories with many tasks: {', '.join(large_cats)}. Consider splitting into sub-categories.")
        
        # Check for similar category names
        names = [c['name'].lower() for c in categories]
        if len(names) != len(set(names)):
            suggestions.append("Duplicate or similar category names detected. Consider using unique names.")
        
        # Suggest category types
        general_cats = [c['name'] for c in categories if c['type'] == 'general']
        if general_cats and len(general_cats) < len(categories):
            suggestions.append(f"Some categories couldn't be auto-classified: {', '.join(general_cats[:3])}")
        
        return suggestions
    
    def _check_warnings(self, categories: List[Dict]) -> List[str]:
        """Check for potential issues"""
        warnings = []
        
        # Check total categories
        if len(categories) == 0:
            warnings.append("No valid categories found in the file.")
        elif len(categories) > 15:
            warnings.append(f"Large number of categories ({len(categories)}). This might be overwhelming for users.")
        
        # Check for low confidence items
        low_confidence_cats = [c['name'] for c in categories if c['confidence'] < 0.5]
        if low_confidence_cats:
            warnings.append(f"Low confidence categories: {', '.join(low_confidence_cats[:3])}")
        
        # Check for very short task names
        for cat in categories:
            short_tasks = [t['name'] for t in cat['tasks'] if len(t['name']) < 3]
            if short_tasks:
                warnings.append(f"Very short task names in '{cat['name']}': {', '.join(short_tasks[:3])}")
        
        return warnings
    
    def get_structured_data(self) -> Dict:
        """Get cleaned, structured data ready for database insertion"""
        if not self.analysis_result:
            return {}
        
        return {
            'categories': [
                {
                    'name': cat['name'],
                    'order': cat['order'],
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
        
        # Basic stats
        summary_parts.append(f"📊 Analysis Summary:")
        summary_parts.append(f"  • Categories: {self.analysis_result['total_columns']}")
        summary_parts.append(f"  • Total rows: {self.analysis_result['total_rows']}")
        
        # Category breakdown
        if self.analysis_result['categories']:
            summary_parts.append(f"\n📁 Categories:")
            for cat in self.analysis_result['categories']:
                confidence_emoji = "✅" if cat['confidence'] > 0.7 else "⚠️" if cat['confidence'] > 0.5 else "❌"
                summary_parts.append(f"  {confidence_emoji} {cat['name']}: {cat['task_count']} tasks (Type: {cat['type']})")
        
        # Suggestions
        if self.analysis_result['suggestions']:
            summary_parts.append(f"\n💡 Suggestions:")
            for suggestion in self.analysis_result['suggestions']:
                summary_parts.append(f"  • {suggestion}")
        
        # Warnings
        if self.analysis_result['warnings']:
            summary_parts.append(f"\n⚠️ Warnings:")
            for warning in self.analysis_result['warnings']:
                summary_parts.append(f"  • {warning}")
        
        return '\n'.join(summary_parts)


def analyze_excel_file(file_content, file_extension: str) -> Tuple[Dict, str]:
    """
    Convenience function to analyze an Excel file
    Returns: (structured_data, analysis_summary)
    """
    analyzer = ExcelAnalyzer()
    
    if not analyzer.load_file(file_content, file_extension):
        return {}, "Failed to load file"
    
    analyzer.analyze()
    structured_data = analyzer.get_structured_data()
    summary = analyzer.get_analysis_summary()
    
    return structured_data, summary
