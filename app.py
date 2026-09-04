import os
from flask import Flask, render_template, jsonify, session, request
from config import Config
from models import db, User, Problem

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config_class)

    db.init_app(app)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.problems import problems_bp
    from routes.submissions import submissions_bp
    from routes.visualizer import visualizer_bp
    from routes.contests import contests_bp
    from routes.interview import interview_bp
    from routes.leaderboard import leaderboard_bp
    from routes.portfolio import portfolio_bp
    from routes.settings import settings_bp
    from routes.admin import admin_bp
    from routes.code_lab import code_lab_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(problems_bp)
    app.register_blueprint(submissions_bp)
    app.register_blueprint(visualizer_bp)
    app.register_blueprint(contests_bp)
    app.register_blueprint(interview_bp)
    app.register_blueprint(leaderboard_bp)
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(code_lab_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/explore')
    def explore_page():
        return render_template('index.html')

    @app.route('/learn')
    def learn_page():
        return render_template('learning_path.html')

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/') or request.is_json:
            return jsonify({'success': False, 'error': 'Endpoint or Resource Not Found'}), 404
        return render_template('404.html', message="The requested page could not be found."), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        if request.path.startswith('/api/') or request.is_json:
            return jsonify({'success': False, 'error': '403 Forbidden Access'}), 403
        return render_template('403.html', message="Access Denied: You do not have permission."), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.path.startswith('/api/') or request.is_json:
            return jsonify({'success': False, 'error': 'Internal Server Error'}), 500
        return render_template('500.html', message="An unexpected error occurred."), 500

    return app

app = create_app()

with app.app_context():
    db.create_all()
    # Auto-seed if database is empty
    if Problem.query.count() == 0:
        try:
            from seed_data import seed_database
            seed_database()
        except Exception as e:
            print(f"Auto-seed notification: {e}")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
