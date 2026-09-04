from datetime import datetime
from models import db

class ContestSubmission(db.Model):
    __tablename__ = 'contest_submissions'

    id = db.Column(db.Integer, primary_key=True)
    contest_id = db.Column(db.Integer, db.ForeignKey('contests.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False, index=True)
    language = db.Column(db.String(20), nullable=False)
    code = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False)  # 'Accepted', 'Wrong Answer'
    score = db.Column(db.Integer, default=0)
    penalty_minutes = db.Column(db.Integer, default=0)
    time_taken_seconds = db.Column(db.Integer, default=0)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    problem = db.relationship('Problem', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'contest_id': self.contest_id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'Unknown',
            'problem_id': self.problem_id,
            'problem_title': self.problem.title if self.problem else 'Unknown',
            'language': self.language,
            'status': self.status,
            'score': self.score,
            'penalty_minutes': self.penalty_minutes,
            'time_taken_seconds': self.time_taken_seconds,
            'submitted_at': self.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if self.submitted_at else None
        }
