from flask import Blueprint, render_template, request, jsonify, session
from models import db, Contest, ContestProblem, ContestSubmission, User, Problem
from services.judge import OnlineJudge

contests_bp = Blueprint('contests', __name__)

@contests_bp.route('/contests')
def contests_page():
    return render_template('contests.html')


@contests_bp.route('/contests/<slug>')
def contest_detail_page(slug):
    contest = Contest.query.filter_by(slug=slug).first_or_404()
    return render_template('contest.html', contest=contest)


@contests_bp.route('/api/contests')
def api_get_contests():
    contests = Contest.query.order_by(Contest.id.desc()).all()
    return jsonify({'success': True, 'contests': [c.to_dict() for c in contests]})


@contests_bp.route('/api/contests/<int:contest_id>')
def api_get_contest(contest_id):
    contest = Contest.query.get(contest_id)
    if not contest:
        return jsonify({'success': False, 'error': 'Contest not found'}), 404
    return jsonify({'success': True, 'contest': contest.to_dict()})


@contests_bp.route('/api/contests/<int:contest_id>/submit', methods=['POST'])
def api_submit_contest(contest_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Please login to participate in contests.'}), 401

    contest = Contest.query.get(contest_id)
    if not contest:
        return jsonify({'success': False, 'error': 'Contest not found'}), 404

    data = request.get_json() or {}
    problem_id = data.get('problem_id')
    language = data.get('language', 'python')
    code = data.get('code', '')
    time_taken_seconds = data.get('time_taken_seconds', 0)

    problem = Problem.query.get(problem_id)
    if not problem:
        return jsonify({'success': False, 'error': 'Problem not found'}), 404

    eval_res = OnlineJudge.evaluate_submission(problem, language, code)
    status = eval_res['status']
    score = 100 if status == 'Accepted' else 0

    c_sub = ContestSubmission(
        contest_id=contest.id,
        user_id=user_id,
        problem_id=problem.id,
        language=language,
        code=code,
        status=status,
        score=score,
        time_taken_seconds=time_taken_seconds
    )
    db.session.add(c_sub)
    db.session.commit()

    return jsonify({
        'success': True,
        'status': status,
        'score': score,
        'test_results': eval_res['test_results']
    })


@contests_bp.route('/api/contests/<int:contest_id>/leaderboard')
def api_contest_leaderboard(contest_id):
    submissions = ContestSubmission.query.filter_by(contest_id=contest_id).all()
    user_scores = {}

    for s in submissions:
        if s.user_id not in user_scores:
            user_scores[s.user_id] = {
                'username': s.user.username if s.user else 'Anonymous',
                'total_score': 0,
                'solved_count': 0,
                'total_time': 0
            }
        if s.status == 'Accepted':
            user_scores[s.user_id]['total_score'] += s.score
            user_scores[s.user_id]['solved_count'] += 1
            user_scores[s.user_id]['total_time'] += s.time_taken_seconds

    leaderboard = list(user_scores.values())
    leaderboard.sort(key=lambda x: (-x['total_score'], x['total_time']))

    for rank, row in enumerate(leaderboard, start=1):
        row['rank'] = rank

    return jsonify({'success': True, 'leaderboard': leaderboard})
