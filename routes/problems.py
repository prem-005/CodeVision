from flask import Blueprint, render_template, request, jsonify, session
from models import db, Problem, TestCase, UserProgress, Bookmark, Note

problems_bp = Blueprint('problems', __name__)

@problems_bp.route('/problems')
def problems_page():
    return render_template('problems.html')


@problems_bp.route('/problems/<identifier>')
def problem_detail_page(identifier):
    problem = None
    if identifier.isdigit():
        problem = Problem.query.get(int(identifier))
    if not problem:
        problem = Problem.query.filter_by(slug=identifier).first()
    if not problem:
        problem = Problem.query.filter_by(title=identifier).first_or_404()

    return render_template('problem.html', problem=problem)


@problems_bp.route('/api/problems', methods=['GET'])
def api_get_problems():
    difficulty = request.args.get('difficulty')
    topic = request.args.get('topic')
    company = request.args.get('company')
    search = request.args.get('search')
    status_filter = request.args.get('status')  # 'solved', 'unsolved'

    query = Problem.query

    if difficulty and difficulty.lower() != 'all':
        query = query.filter(Problem.difficulty.ilike(difficulty))

    if topic and topic.lower() != 'all':
        query = query.filter(Problem.topic.ilike(f'%{topic}%'))

    if company and company.lower() != 'all':
        query = query.filter(Problem.company_tags.ilike(f'%{company}%'))

    if search:
        query = query.filter(Problem.title.ilike(f'%{search}%') | Problem.topic.ilike(f'%{search}%'))

    problems = query.order_by(Problem.id.asc()).all()

    user_id = session.get('user_id')
    solved_set = set()
    attempted_set = set()
    bookmarked_set = set()

    if user_id:
        progresses = UserProgress.query.filter_by(user_id=user_id).all()
        for p in progresses:
            if p.status == 'solved':
                solved_set.add(p.problem_id)
            else:
                attempted_set.add(p.problem_id)
        
        bms = Bookmark.query.filter_by(user_id=user_id).all()
        bookmarked_set = {b.problem_id for b in bms}

    results = []
    for prob in problems:
        p_dict = prob.to_dict()
        if prob.id in solved_set:
            p_dict['status'] = 'Solved'
            p_dict['user_status'] = 'solved'
        elif prob.id in attempted_set:
            p_dict['status'] = 'Attempted'
            p_dict['user_status'] = 'attempted'
        else:
            p_dict['status'] = 'Todo'
            p_dict['user_status'] = 'unsolved'
        p_dict['is_bookmarked'] = prob.id in bookmarked_set

        if status_filter == 'solved' and p_dict['status'] != 'Solved':
            continue
        if status_filter == 'unsolved' and p_dict['status'] == 'Solved':
            continue

        results.append(p_dict)

    return jsonify({'success': True, 'count': len(results), 'problems': results})


@problems_bp.route('/api/problems/<int:problem_id>', methods=['GET'])
def api_get_problem(problem_id):
    problem = Problem.query.get(problem_id)
    if not problem:
        return jsonify({'success': False, 'error': 'Problem not found'}), 404

    user_id = session.get('user_id')
    user_note = None
    is_bookmarked = False

    if user_id:
        note = Note.query.filter_by(user_id=user_id, problem_id=problem.id).first()
        if note:
            user_note = note.to_dict()
        bm = Bookmark.query.filter_by(user_id=user_id, problem_id=problem.id).first()
        is_bookmarked = (bm is not None)

    prob_data = problem.to_dict(include_testcases=True, include_hidden=False)
    prob_data['user_note'] = user_note
    prob_data['is_bookmarked'] = is_bookmarked

    return jsonify({'success': True, 'problem': prob_data})
