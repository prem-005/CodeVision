import json
from datetime import datetime
from models import db

class Problem(db.Model):
    __tablename__ = 'problems'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), nullable=False, default='Easy')  # 'Easy', 'Medium', 'Hard'
    topic = db.Column(db.String(50), nullable=False, index=True)
    company_tags = db.Column(db.String(255), default='')  # comma-separated: 'Amazon,Google,TCS'
    constraints = db.Column(db.Text, nullable=True)
    starter_code_json = db.Column(db.Text, nullable=False, default='{}')
    hints = db.Column(db.Text, nullable=True, default='[]')
    acceptance_rate = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    test_cases = db.relationship('TestCase', backref='problem', lazy=True, cascade='all, delete-orphan')
    submissions = db.relationship('Submission', backref='problem', lazy=True, cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='problem', lazy=True, cascade='all, delete-orphan')
    bookmarks = db.relationship('Bookmark', backref='problem', lazy=True, cascade='all, delete-orphan')

    @property
    def starter_code(self):
        try:
            return json.loads(self.starter_code_json or '{}')
        except Exception:
            return {}

    @starter_code.setter
    def starter_code(self, value):
        self.starter_code_json = json.dumps(value)

    @property
    def hint_list(self):
        try:
            return json.loads(self.hints or '[]')
        except Exception:
            return []

    @property
    def companies(self):
        if not self.company_tags:
            return []
        return [c.strip() for c in self.company_tags.split(',') if c.strip()]

    def to_dict(self, include_testcases=False, include_hidden=False):
        data = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'difficulty': self.difficulty,
            'topic': self.topic,
            'company_tags': self.companies,
            'constraints': self.constraints,
            'starter_code': self.starter_code,
            'hints': self.hint_list,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
        if include_testcases:
            tests = [tc.to_dict(include_hidden=include_hidden) for tc in self.test_cases]
            if not include_hidden:
                tests = [t for t in tests if not t['is_hidden']]
            data['test_cases'] = tests
        return data
