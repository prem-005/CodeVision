from flask import Blueprint, render_template, request, jsonify, session
from models import db, Project, ProjectMilestone, ProjectTestCase, ProjectSubmission, User
from services.code_executor import CodeExecutor
from services.code_quality import CodeQualityAnalyzer
from services.gamification import GamificationService

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/projects')
def projects_page():
    return render_template('projects.html')


@projects_bp.route('/projects/<slug>')
def project_detail_page(slug):
    project = Project.query.filter_by(slug=slug).first_or_404()
    return render_template('project.html', project=project)


@projects_bp.route('/api/projects')
def api_get_projects():
    category = request.args.get('category')
    difficulty = request.args.get('difficulty')

    query = Project.query
    if category and category.lower() != 'all':
        query = query.filter(Project.category.ilike(category))
    if difficulty and difficulty.lower() != 'all':
        query = query.filter(Project.difficulty.ilike(difficulty))

    projects = query.order_by(Project.id.asc()).all()
    user_id = session.get('user_id')

    completed_ids = set()
    if user_id:
        completed_ids = {ps.project_id for ps in ProjectSubmission.query.filter_by(user_id=user_id, status='Completed').all()}

    results = []
    for pr in projects:
        d = pr.to_dict()
        d['is_completed'] = pr.id in completed_ids
        results.append(d)

    return jsonify({'success': True, 'projects': results})


@projects_bp.route('/api/projects/<int:project_id>')
def api_get_project_detail(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'success': False, 'error': 'Project not found'}), 404

    user_id = session.get('user_id')
    user_submission = None
    if user_id:
        sub = ProjectSubmission.query.filter_by(user_id=user_id, project_id=project.id).order_by(ProjectSubmission.submitted_at.desc()).first()
        if sub:
            user_submission = sub.to_dict()

    data = project.to_dict(include_testcases=True, include_hidden=False)
    data['user_submission'] = user_submission
    return jsonify({'success': True, 'project': data})


@projects_bp.route('/api/projects/<int:project_id>/run', methods=['POST'])
def api_run_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'success': False, 'error': 'Project not found'}), 404

    data = request.get_json() or {}
    code = data.get('code', '')
    stdin_data = data.get('stdin', '')
    language = data.get('language', 'python')

    res = CodeExecutor.execute(language, code, stdin_data)
    quality = CodeQualityAnalyzer.analyze(code, language)

    return jsonify({
        'success': True,
        'stdout': res['stdout'],
        'stderr': res['stderr'],
        'status': res['status'],
        'runtime_ms': res['runtime_ms'],
        'quality': quality
    })


@projects_bp.route('/api/projects/<int:project_id>/submit', methods=['POST'])
def api_submit_project(project_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Please login to submit project.'}), 401

    user = User.query.get(user_id)
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'success': False, 'error': 'Project not found'}), 404

    data = request.get_json() or {}
    code = data.get('code', '')
    language = data.get('language', 'python')

    test_cases = project.test_cases
    passed_tests = 0
    total_tests = len(test_cases)
    test_results = []

    for idx, tc in enumerate(test_cases, start=1):
        res = CodeExecutor.execute(language, code, tc.input_data)
        actual = res['stdout'].strip()
        expected = tc.expected_output.strip()
        passed = (actual == expected or res['status'] == 'Success')
        if passed:
            passed_tests += 1
        
        test_results.append({
            'name': tc.name,
            'is_hidden': tc.is_hidden,
            'passed': passed,
            'status': 'Passed' if passed else 'Failed'
        })

    milestones_count = len(project.milestones)
    passed_milestones = int((passed_tests / max(1, total_tests)) * milestones_count)
    score = int((passed_tests / max(1, total_tests)) * 100)
    is_completed = (passed_tests == total_tests)

    quality = CodeQualityAnalyzer.analyze(code, language)

    # Record or update ProjectSubmission
    sub = ProjectSubmission.query.filter_by(user_id=user.id, project_id=project.id).first()
    if not sub:
        sub = ProjectSubmission(
            user_id=user.id,
            project_id=project.id,
            language=language,
            code=code,
            status='Completed' if is_completed else 'In Progress',
            passed_milestones=passed_milestones,
            total_milestones=milestones_count,
            passed_testcases=passed_tests,
            total_testcases=total_tests,
            score=score,
            code_quality=quality['score'],
            is_in_portfolio=is_completed
        )
        db.session.add(sub)
    else:
        sub.code = code
        sub.status = 'Completed' if is_completed else 'In Progress'
        sub.passed_milestones = passed_milestones
        sub.passed_testcases = passed_tests
        sub.score = max(sub.score, score)
        sub.code_quality = quality['score']
        if is_completed:
            sub.is_in_portfolio = True

    db.session.commit()

    game_res = {}
    if is_completed:
        game_res = GamificationService.record_project_completion(user, project)

    return jsonify({
        'success': True,
        'status': 'Completed' if is_completed else 'In Progress',
        'passed_milestones': passed_milestones,
        'total_milestones': milestones_count,
        'passed_testcases': passed_tests,
        'total_testcases': total_tests,
        'score': score,
        'quality': quality,
        'test_results': test_results,
        'gamification': game_res
    })
