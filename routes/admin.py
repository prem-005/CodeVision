import json
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from models import db, User, Problem, TestCase, Contest, Submission
from services.analytics import AnalyticsService

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required():
    user_id = session.get('user_id')
    if not user_id:
        return False
    user = User.query.get(user_id)
    return user and user.is_admin()

@admin_bp.route('/')
def dashboard():
    if not admin_required():
        return redirect(url_for('auth.login'))
    return render_template('admin/dashboard.html')

@admin_bp.route('/problems')
def problems():
    if not admin_required():
        return redirect(url_for('auth.login'))
    return render_template('admin/problems.html')

@admin_bp.route('/problems/new')
@admin_bp.route('/problems/<int:problem_id>/edit')
def problem_form(problem_id=None):
    if not admin_required():
        return redirect(url_for('auth.login'))
    problem = Problem.query.get(problem_id) if problem_id else None
    return render_template('admin/problem_form.html', problem=problem)

@admin_bp.route('/testcases')
def testcases():
    if not admin_required():
        return redirect(url_for('auth.login'))
    return render_template('admin/testcases.html')

@admin_bp.route('/users')
def users():
    if not admin_required():
        return redirect(url_for('auth.login'))
    return render_template('admin/users.html')

@admin_bp.route('/contests')
def contests():
    if not admin_required():
        return redirect(url_for('auth.login'))
    return render_template('admin/contests.html')

@admin_bp.route('/analytics')
def analytics():
    if not admin_required():
        return redirect(url_for('auth.login'))
    return render_template('admin/analytics.html')

# Admin REST APIs
@admin_bp.route('/api/stats')
def api_admin_stats():
    if not admin_required():
        return jsonify({'success': False, 'error': 'Admin access required'}), 403
    return jsonify({'success': True, 'stats': AnalyticsService.get_admin_system_stats()})

@admin_bp.route('/api/problems', methods=['POST'])
def api_admin_save_problem():
    if not admin_required():
        return jsonify({'success': False, 'error': 'Admin access required'}), 403

    data = request.get_json() or {}
    prob_id = data.get('id')
    
    if prob_id:
        prob = Problem.query.get(prob_id)
        if not prob:
            return jsonify({'success': False, 'error': 'Problem not found'}), 404
    else:
        prob = Problem()
        db.session.add(prob)

    prob.title = data.get('title', prob.title or 'Untitled')
    prob.slug = data.get('slug') or prob.title.lower().replace(' ', '-')
    prob.difficulty = data.get('difficulty', 'Easy')
    prob.topic = data.get('topic', 'Array')
    prob.company_tags = data.get('company_tags', '')
    prob.description = data.get('description', '')
    prob.constraints = data.get('constraints', '')
    if 'starter_code' in data:
        prob.starter_code_json = json.dumps(data['starter_code'])
    if 'hints' in data:
        prob.hints = json.dumps(data['hints'])

    db.session.commit()
    return jsonify({'success': True, 'problem_id': prob.id})

@admin_bp.route('/api/problems/<int:problem_id>', methods=['DELETE'])
def api_admin_delete_problem(problem_id):
    if not admin_required():
        return jsonify({'success': False, 'error': 'Admin access required'}), 403
    prob = Problem.query.get(problem_id)
    if not prob:
        return jsonify({'success': False, 'error': 'Problem not found'}), 404
    db.session.delete(prob)
    db.session.commit()
    return jsonify({'success': True})

@admin_bp.route('/api/testcases', methods=['POST'])
def api_admin_save_testcase():
    if not admin_required():
        return jsonify({'success': False, 'error': 'Admin access required'}), 403

    data = request.get_json() or {}
    tc_id = data.get('id')
    
    if tc_id:
        tc = TestCase.query.get(tc_id)
        if not tc:
            return jsonify({'success': False, 'error': 'TestCase not found'}), 404
    else:
        tc = TestCase()
        db.session.add(tc)

    tc.problem_id = data.get('problem_id')
    tc.input_data = data.get('input_data', '')
    tc.expected_output = data.get('expected_output', '')
    tc.is_hidden = bool(data.get('is_hidden', False))
    tc.explanation = data.get('explanation', '')

    db.session.commit()
    return jsonify({'success': True, 'testcase_id': tc.id})

@admin_bp.route('/api/testcases/<int:tc_id>', methods=['DELETE'])
def api_admin_delete_testcase(tc_id):
    if not admin_required():
        return jsonify({'success': False, 'error': 'Admin access required'}), 403
    tc = TestCase.query.get(tc_id)
    if not tc:
        return jsonify({'success': False, 'error': 'TestCase not found'}), 404
    db.session.delete(tc)
    db.session.commit()
    return jsonify({'success': True})

@admin_bp.route('/api/users')
def api_admin_get_users():
    if not admin_required():
        return jsonify({'success': False, 'error': 'Admin access required'}), 403
    users = User.query.order_by(User.id.asc()).all()
    return jsonify({'success': True, 'users': [u.to_dict() for u in users]})
