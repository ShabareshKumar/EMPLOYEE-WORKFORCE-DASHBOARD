from flask import Blueprint, jsonify
from models.database import db
from models.timesheet import Timesheet
from models.user import User
from utils.auth import token_required, role_required
from sqlalchemy import func
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics', methods=['GET'])
@token_required
@role_required('admin', 'manager')
def get_analytics(current_user):
    """Get productivity analytics"""
    try:
        # Get all timesheets
        timesheets = Timesheet.query.all()
        
        # Calculate KPIs
        total_hours = sum(t.total_hours() for t in timesheets)
        total_productive = sum(t.productive_hours for t in timesheets)
        total_non_productive = sum(t.non_productive_hours for t in timesheets)
        
        productivity_percentage = round((total_productive / total_hours * 100), 2) if total_hours > 0 else 0
        
        # Active employees (who logged time)
        active_employees = db.session.query(Timesheet.user_id).distinct().count()
        
        # Employee performance
        employee_stats = db.session.query(
            User.id,
            User.name,
            func.sum(Timesheet.productive_hours).label('productive'),
            func.sum(Timesheet.non_productive_hours).label('non_productive')
        ).join(Timesheet).group_by(User.id).all()
        
        employee_performance = []
        for emp in employee_stats:
            total = emp.productive + emp.non_productive
            score = round((emp.productive / total * 100), 2) if total > 0 else 0
            employee_performance.append({
                'id': emp.id,
                'name': emp.name,
                'productive_hours': float(emp.productive),
                'non_productive_hours': float(emp.non_productive),
                'total_hours': total,
                'productivity_score': score
            })
        
        # Sort by productivity score
        employee_performance.sort(key=lambda x: x['productivity_score'], reverse=True)
        
        # Weekly trend (last 7 days)
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        
        weekly_data = db.session.query(
            Timesheet.date,
            func.sum(Timesheet.productive_hours).label('productive'),
            func.sum(Timesheet.non_productive_hours).label('non_productive')
        ).filter(Timesheet.date >= week_ago).group_by(Timesheet.date).all()
        
        weekly_trend = []
        for day in weekly_data:
            total = day.productive + day.non_productive
            score = round((day.productive / total * 100), 2) if total > 0 else 0
            weekly_trend.append({
                'date': day.date.isoformat(),
                'productivity_score': score,
                'productive_hours': float(day.productive),
                'non_productive_hours': float(day.non_productive)
            })
        
        # Generate insights
        insights = generate_insights(employee_performance, productivity_percentage)
        
        return jsonify({
            'kpis': {
                'total_hours': round(total_hours, 2),
                'productive_hours': round(total_productive, 2),
                'non_productive_hours': round(total_non_productive, 2),
                'productivity_percentage': productivity_percentage,
                'active_employees': active_employees
            },
            'employee_performance': employee_performance,
            'weekly_trend': weekly_trend,
            'insights': insights
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

def generate_insights(employee_performance, overall_productivity):
    """Generate smart insights based on data"""
    insights = []
    
    # Overall productivity insight
    if overall_productivity < 50:
        insights.append({
            'type': 'warning',
            'message': 'Low productivity detected across the team',
            'severity': 'high'
        })
    elif overall_productivity > 80:
        insights.append({
            'type': 'success',
            'message': 'Excellent team productivity performance',
            'severity': 'low'
        })
    
    # Individual employee insights
    for emp in employee_performance[:3]:  # Top 3
        if emp['productivity_score'] > 85:
            insights.append({
                'type': 'success',
                'message': f"{emp['name']} is a high performer with {emp['productivity_score']}% productivity",
                'severity': 'low'
            })
        
        if emp['total_hours'] > 50:  # Weekly threshold
            insights.append({
                'type': 'warning',
                'message': f"{emp['name']} is at risk of burnout with {emp['total_hours']} hours logged",
                'severity': 'high'
            })
    
    # Low performers
    low_performers = [emp for emp in employee_performance if emp['productivity_score'] < 50]
    if low_performers:
        insights.append({
            'type': 'warning',
            'message': f"{len(low_performers)} employee(s) showing low productivity",
            'severity': 'medium'
        })
    
    return insights

@analytics_bp.route('/analytics/employee/<int:user_id>', methods=['GET'])
@token_required
@role_required('admin', 'manager')
def get_employee_analytics(current_user, user_id):
    """Get analytics for specific employee"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        timesheets = Timesheet.query.filter_by(user_id=user_id).all()
        
        total_hours = sum(t.total_hours() for t in timesheets)
        productive_hours = sum(t.productive_hours for t in timesheets)
        productivity_score = round((productive_hours / total_hours * 100), 2) if total_hours > 0 else 0
        
        return jsonify({
            'user': user.to_dict(),
            'stats': {
                'total_hours': round(total_hours, 2),
                'productive_hours': round(productive_hours, 2),
                'productivity_score': productivity_score,
                'total_entries': len(timesheets)
            },
            'timesheets': [t.to_dict() for t in timesheets]
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500
