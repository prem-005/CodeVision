from flask import Blueprint, render_template, jsonify
from models import db, User, UserProgress

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('/leaderboard')
def leaderboard_page():
    return render_template('leaderboard.html')


@leaderboard_bp.route('/api/leaderboard')
def api_leaderboard():
    users = User.query.all()
    rows = []

    for u in users:
        solved_cnt = UserProgress.query.filter_by(user_id=u.id, status='solved').count()

        rows.append({
            'user_id': u.id,
            'username': u.username,
            'role': u.role,
            'points': u.points,
            'problems_solved': solved_cnt,
            'streak': u.current_streak,
            'contest_rating': u.contest_rating
        })

    # Sort primary: Points descending; Tie-break: Problems solved descending
    rows.sort(key=lambda x: (-x['points'], -x['problems_solved']))

    for rank, row in enumerate(rows, start=1):
        row['rank'] = rank

    return jsonify({'success': True, 'leaderboard': rows[:50]})
