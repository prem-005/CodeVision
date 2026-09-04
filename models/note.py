from datetime import datetime
from models import db

class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False, default='Problem Note')
    content = db.Column(db.Text, nullable=False)
    tag = db.Column(db.String(50), default='Important')  # 'Important', 'Revision', 'Interview', 'Difficult'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'problem_id': self.problem_id,
            'problem_title': self.problem.title if self.problem else 'Unknown',
            'title': self.title,
            'content': self.content,
            'tag': self.tag,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
