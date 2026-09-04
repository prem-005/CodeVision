from datetime import datetime
from models import db

class Submission(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False, index=True)
    language = db.Column(db.String(20), nullable=False)  # 'python', 'java', 'javascript', 'cpp', 'c'
    code = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False)  # 'Accepted', 'Wrong Answer', 'Runtime Error', 'Compilation Error', 'Time Limit Exceeded'
    passed_testcases = db.Column(db.Integer, default=0)
    total_testcases = db.Column(db.Integer, default=0)
    runtime_ms = db.Column(db.Float, default=0.0)
    memory_kb = db.Column(db.Float, default=0.0)
    error_message = db.Column(db.Text, nullable=True)
    code_quality_score = db.Column(db.Integer, default=80)
    time_complexity = db.Column(db.String(30), default='O(n)')
    space_complexity = db.Column(db.String(30), default='O(1)')
    solution_approach = db.Column(db.String(50), default='Optimal')  # 'Brute Force', 'Optimized', 'Alternative'
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'Unknown',
            'problem_id': self.problem_id,
            'problem_title': self.problem.title if self.problem else 'Unknown',
            'problem_difficulty': self.problem.difficulty if self.problem else 'Unknown',
            'problem_topic': self.problem.topic if self.problem else 'Unknown',
            'language': self.language,
            'code': self.code,
            'status': self.status,
            'passed_testcases': self.passed_testcases,
            'total_testcases': self.total_testcases,
            'runtime_ms': round(self.runtime_ms, 1),
            'memory_kb': round(self.memory_kb, 1),
            'code_quality_score': self.code_quality_score,
            'time_complexity': self.time_complexity,
            'space_complexity': self.space_complexity,
            'solution_approach': self.solution_approach,
            'error_message': self.error_message,
            'submitted_at': self.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if self.submitted_at else None
        }
