from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from models import db, User, UserSettings
from services.skill_engine import SkillEngine

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')

        if not username or not email or not password:
            if request.is_json:
                return jsonify({'success': False, 'error': 'All fields are required.'}), 400
            return render_template('register.html', error='All fields are required.')

        if User.query.filter_by(username=username).first():
            if request.is_json:
                return jsonify({'success': False, 'error': 'Username already taken.'}), 400
            return render_template('register.html', error='Username already taken.')

        if User.query.filter_by(email=email).first():
            if request.is_json:
                return jsonify({'success': False, 'error': 'Email already registered.'}), 400
            return render_template('register.html', error='Email already registered.')

        user = User(username=username, email=email, role='student')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        # Create settings & initialize skills
        db.session.add(UserSettings(user_id=user.id))
        db.session.commit()
        SkillEngine.initialize_user_skills(user.id)

        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role

        if request.is_json:
            return jsonify({'success': True, 'message': 'Account created successfully', 'redirect': url_for('dashboard.dashboard_page')})
        return redirect(url_for('dashboard.dashboard_page'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        password = data.get('password', '')

        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if not user or not user.check_password(password):
            if request.is_json:
                return jsonify({'success': False, 'error': 'Invalid username or password.'}), 401
            return render_template('login.html', error='Invalid username or password.')

        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role

        if request.is_json:
            return jsonify({'success': True, 'message': 'Logged in successfully', 'redirect': url_for('dashboard.dashboard_page')})
        return redirect(url_for('dashboard.dashboard_page'))

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@auth_bp.route('/api/auth/me')
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'authenticated': False}), 401
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'authenticated': False}), 404
    return jsonify({'success': True, 'authenticated': True, 'user': user.to_dict()})
