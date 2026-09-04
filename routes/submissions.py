from flask import Blueprint, render_template, request, jsonify, session
from models import db, Problem, Submission, UserProgress, User
from services.judge import OnlineJudge
from services.code_quality import CodeQualityAnalyzer
from services.skill_engine import SkillEngine
from services.gamification import GamificationService

submissions_bp = Blueprint('submissions', __name__)

@submissions_bp.route('/submissions')
def submissions_page():
    return render_template('submissions.html')


@submissions_bp.route('/api/run', methods=['POST'])
def api_run_code():
    data = request.get_json() or {}
    language = data.get('language', 'python')
    code = data.get('code', '')
    stdin_data = data.get('stdin', '')

    if not code:
        return jsonify({'success': False, 'error': 'Code cannot be empty'}), 400

    result = OnlineJudge.run_custom(language, code, stdin_data)
    quality = CodeQualityAnalyzer.analyze(code, language)
    result['quality'] = quality

    return jsonify(result)


@submissions_bp.route('/api/submit', methods=['POST'])
def api_submit_code():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Please login to submit code.'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': 'User not found.'}), 404

    data = request.get_json() or {}
    problem_id = data.get('problem_id')
    language = data.get('language', 'python')
    code = data.get('code', '')
    solution_approach = data.get('solution_approach', 'Optimal')

    problem = Problem.query.get(problem_id)
    if not problem:
        return jsonify({'success': False, 'error': 'Problem not found'}), 404

    if not code:
        return jsonify({'success': False, 'error': 'Code cannot be empty'}), 400

    # Evaluate against all tests (visible + hidden)
    eval_res = OnlineJudge.evaluate_submission(problem, language, code)
    quality = CodeQualityAnalyzer.analyze(code, language)

    status = eval_res['status']
    passed_tests = eval_res['passed_testcases']
    total_tests = eval_res['total_testcases']
    runtime_ms = eval_res['runtime_ms']
    memory_kb = eval_res['memory_kb']
    error_msg = eval_res.get('error_message')

    # Save submission record
    sub = Submission(
        user_id=user.id,
        problem_id=problem.id,
        language=language,
        code=code,
        status=status,
        passed_testcases=passed_tests,
        total_testcases=total_tests,
        runtime_ms=runtime_ms,
        memory_kb=memory_kb,
        error_message=error_msg,
        code_quality_score=quality['score'],
        time_complexity=quality['time_complexity'],
        space_complexity=quality['space_complexity'],
        solution_approach=solution_approach
    )
    db.session.add(sub)

    # Update user progress
    prog = UserProgress.query.filter_by(user_id=user.id, problem_id=problem.id).first()
    if not prog:
        prog = UserProgress(user_id=user.id, problem_id=problem.id, status='solved' if status == 'Accepted' else 'attempted')
        db.session.add(prog)
    elif status == 'Accepted':
        prog.status = 'solved'

    db.session.commit()

    # Update skills and gamification
    skill_update = SkillEngine.update_after_problem_solve(user.id, problem.topic, language, status == 'Accepted', problem.difficulty)
    game_update = {}
    if status == 'Accepted':
        game_update = GamificationService.record_problem_solve(user, problem)

    return jsonify({
        'success': True,
        'submission_id': sub.id,
        'status': status,
        'passed_testcases': passed_tests,
        'total_testcases': total_tests,
        'runtime_ms': runtime_ms,
        'memory_kb': memory_kb,
        'test_results': eval_res['test_results'],
        'error_message': error_msg,
        'quality': quality,
        'skill_update': skill_update,
        'gamification': game_update
    })


@submissions_bp.route('/api/submissions/user')
def api_user_submissions():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    problem_id = request.args.get('problem_id')
    query = Submission.query.filter_by(user_id=user_id)
    if problem_id:
        query = query.filter_by(problem_id=problem_id)

    subs = query.order_by(Submission.submitted_at.desc()).limit(20).all()
    return jsonify({'success': True, 'submissions': [s.to_dict() for s in subs]})
