import json
from datetime import datetime
from models import db

class ProjectSubmission(db.Model):
    __tablename__ = 'project_submissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)
    language = db.Column(db.String(20), nullable=False, default='python')
    code = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False)  # 'Completed', 'In Progress', 'Failed'
    passed_milestones = db.Column(db.Integer, default=0)
    total_milestones = db.Column(db.Integer, default=0)
    passed_testcases = db.Column(db.Integer, default=0)
    total_testcases = db.Column(db.Integer, default=0)
    score = db.Column(db.Integer, default=0)  # 0 to 100
    code_quality = db.Column(db.Integer, default=85)
    execution_time_ms = db.Column(db.Float, default=0.0)
    is_in_portfolio = db.Column(db.Boolean, default=False)
    is_public = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'Unknown',
            'project_id': self.project_id,
            'project_title': self.project.title if self.project else 'Unknown',
            'project_category': self.project.category if self.project else 'Unknown',
            'project_difficulty': self.project.difficulty if self.project else 'Unknown',
            'language': self.language,
            'code': self.code if self.is_public else None,
            'status': self.status,
            'passed_milestones': self.passed_milestones,
            'total_milestones': self.total_milestones,
            'passed_testcases': self.passed_testcases,
            'total_testcases': self.total_testcases,
            'score': self.score,
            'code_quality': self.code_quality,
            'execution_time_ms': round(self.execution_time_ms, 1),
            'is_in_portfolio': self.is_in_portfolio,
            'is_public': self.is_public,
            'submitted_at': self.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if self.submitted_at else None
        }
