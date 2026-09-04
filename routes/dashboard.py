from flask import Blueprint, render_template, jsonify, session, redirect, url_for
from models import db, User, Submission, UserAchievement, UserProgress, Problem
from services.analytics import AnalyticsService
from services.skill_engine import SkillEngine
from services.recommendation_engine import RecommendationEngine

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard_page():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('auth.login'))

    stats = AnalyticsService.get_user_dashboard_stats(user_id)
    total_problems = Problem.query.count()

    submissions = Submission.query.filter_by(user_id=user_id).all()
    total_subs = len(submissions)
    accepted_subs = sum(1 for s in submissions if s.status == 'Accepted')
    accuracy = round((accepted_subs / total_subs * 100.0), 1) if total_subs > 0 else 0.0

    recent_subs = (
        Submission.query.filter_by(user_id=user_id)
        .order_by(Submission.submitted_at.desc())
        .limit(8)
        .all()
    )
    recent_submissions = []
    for s in recent_subs:
        prob = Problem.query.get(s.problem_id)
        recent_submissions.append({
            'problem_id': s.problem_id,
            'problem_title': prob.title if prob else f"Problem {s.problem_id}",
            'language': s.language,
            'status': s.status,
            'runtime_ms': s.runtime_ms,
            'submitted_at': s.submitted_at.strftime('%Y-%m-%d %H:%M') if s.submitted_at else ''
        })

    user_achievements = UserAchievement.query.filter_by(user_id=user_id).all()
    achievements = [ua.to_dict() for ua in user_achievements]

    return render_template(
        'dashboard.html',
        user=user,
        total_solved=stats.get('total_solved', 0),
        total_problems=total_problems,
        easy_count=stats.get('easy_solved', 0),
        medium_count=stats.get('medium_solved', 0),
        hard_count=stats.get('hard_solved', 0),
        accuracy=accuracy,
        best_runtime=stats.get('best_runtime', 0.0),
        recent_submissions=recent_submissions,
        achievements=achievements
    )


@dashboard_bp.route('/api/dashboard')
def api_dashboard_data():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    stats = AnalyticsService.get_user_dashboard_stats(user_id)
    skills = SkillEngine.get_skill_radar_data(user_id)
    recs = RecommendationEngine.get_recommendations_for_user(user)

    recent_subs = (
        Submission.query.filter_by(user_id=user_id)
        .order_by(Submission.submitted_at.desc())
        .limit(8)
        .all()
    )
    user_achievements = UserAchievement.query.filter_by(user_id=user_id).all()

    return jsonify({
        'success': True,
        'user': user.to_dict(),
        'stats': stats,
        'skills': skills,
        'recommendations': recs,
        'recent_submissions': [s.to_dict() for s in recent_subs],
        'achievements': [ua.to_dict() for ua in user_achievements]
    })
