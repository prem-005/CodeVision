from datetime import datetime
from models import db

class Bookmark(db.Model):
    __tablename__ = 'bookmarks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False, index=True)
    folder = db.Column(db.String(50), default='Favorites')  # 'Favorites', 'Review Later', 'Interview Prep', 'Hard'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'problem_id', name='_user_problem_bookmark_uc'),)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'problem_id': self.problem_id,
            'problem_title': self.problem.title if self.problem else 'Unknown',
            'problem_difficulty': self.problem.difficulty if self.problem else 'Unknown',
            'problem_topic': self.problem.topic if self.problem else 'Unknown',
            'folder': self.folder,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
