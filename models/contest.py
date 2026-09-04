import json
from datetime import datetime, timedelta
from models import db

class Contest(db.Model):
    __tablename__ = 'contests'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)  # 30, 60, 90
    difficulty = db.Column(db.String(20), default='Medium')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    contest_problems = db.relationship('ContestProblem', backref='contest', lazy=True, cascade='all, delete-orphan')
    submissions = db.relationship('ContestSubmission', backref='contest', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'duration_minutes': self.duration_minutes,
            'difficulty': self.difficulty,
            'is_active': self.is_active,
            'problem_count': len(self.contest_problems),
            'problems': [cp.to_dict() for cp in self.contest_problems],
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class ContestProblem(db.Model):
    __tablename__ = 'contest_problems'

    id = db.Column(db.Integer, primary_key=True)
    contest_id = db.Column(db.Integer, db.ForeignKey('contests.id'), nullable=False, index=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False, index=True)
    order_index = db.Column(db.Integer, default=1)
    points = db.Column(db.Integer, default=100)

    problem = db.relationship('Problem', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'contest_id': self.contest_id,
            'problem_id': self.problem_id,
            'order_index': self.order_index,
            'points': self.points,
            'title': self.problem.title if self.problem else 'Unknown',
            'difficulty': self.problem.difficulty if self.problem else 'Unknown',
            'topic': self.problem.topic if self.problem else 'Unknown'
        }
