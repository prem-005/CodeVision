from datetime import datetime
from models import db

class UserProgress(db.Model):
    __tablename__ = 'user_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default='attempted')  # 'solved' or 'attempted'
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'problem_id', name='_user_problem_uc'),)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'problem_id': self.problem_id,
            'status': self.status,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50), default='DSA')  # 'Language', 'DSA', 'System', 'Engineering'

    user_skills = db.relationship('UserSkill', backref='skill', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category
        }


class UserSkill(db.Model):
    __tablename__ = 'user_skills'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    skill_name = db.Column(db.String(50), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=True)
    score = db.Column(db.Float, default=10.0)  # 0 to 100%
    problems_solved = db.Column(db.Integer, default=0)
    accuracy = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'skill_name', name='_user_skill_uc'),)

    def to_dict(self):
        return {
            'skill_name': self.skill_name,
            'score': round(self.score, 1),
            'problems_solved': self.problems_solved,
            'accuracy': round(self.accuracy, 1),
            'last_updated': self.last_updated.strftime('%Y-%m-%d %H:%M:%S') if self.last_updated else None
        }


class Recommendation(db.Model):
    __tablename__ = 'recommendations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    type = db.Column(db.String(30), nullable=False)  # 'Problem', 'Project', 'Algorithm', 'Topic'
    reference_id = db.Column(db.Integer, nullable=True)
    title = db.Column(db.String(200), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    priority = db.Column(db.Integer, default=1)
    is_dismissed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'reference_id': self.reference_id,
            'title': self.title,
            'reason': self.reason,
            'priority': self.priority,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
