from flask import Blueprint, render_template, request, jsonify, session
from models import db, User, UserAchievement
from services.skill_engine import SkillEngine

portfolio_bp = Blueprint('portfolio', __name__)

@portfolio_bp.route('/portfolio')
def portfolio_page():
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    return render_template('portfolio.html', user=user)


@portfolio_bp.route('/portfolio/<username>')
def public_portfolio_page(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('portfolio.html', user=user, is_public_view=True)


@portfolio_bp.route('/api/portfolio')
def api_get_portfolio():
    user_id = session.get('user_id')
    username = request.args.get('username')

    if username:
        user = User.query.filter_by(username=username).first()
    elif user_id:
        user = User.query.get(user_id)
    else:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    achievements = UserAchievement.query.filter_by(user_id=user.id).all()
    skills = SkillEngine.get_skill_radar_data(user.id)

    return jsonify({
        'success': True,
        'user': user.to_dict(),
        'projects': [],
        'achievements': [a.to_dict() for a in achievements],
        'skills': skills
    })


@portfolio_bp.route('/api/portfolio/toggle-visibility', methods=['POST'])
def api_toggle_portfolio_visibility():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    return jsonify({'success': False, 'error': 'Project portfolio feature removed'}), 410
