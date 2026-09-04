from datetime import datetime
from models import db

class Achievement(db.Model):
    __tablename__ = 'achievements'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code_name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), default='fa-award')
    points = db.Column(db.Integer, default=50)

    user_achievements = db.relationship('UserAchievement', backref='achievement', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code_name': self.code_name,
            'description': self.description,
            'icon': self.icon,
            'points': self.points
        }


class UserAchievement(db.Model):
    __tablename__ = 'user_achievements'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'achievement_id': self.achievement_id,
            'name': self.achievement.name if self.achievement else '',
            'description': self.achievement.description if self.achievement else '',
            'icon': self.achievement.icon if self.achievement else '',
            'points': self.achievement.points if self.achievement else 0,
            'unlocked_at': self.unlocked_at.strftime('%Y-%m-%d %H:%M:%S') if self.unlocked_at else None
        }
