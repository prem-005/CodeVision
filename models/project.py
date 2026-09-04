import json
from datetime import datetime
from models import db

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, default='Software Engineering')  # 'Backend', 'Automation', 'Fullstack', 'Data'
    difficulty = db.Column(db.String(20), nullable=False, default='Beginner')  # 'Beginner', 'Intermediate', 'Advanced'
    description = db.Column(db.Text, nullable=False)
    scenario = db.Column(db.Text, nullable=False)
    objective = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    constraints = db.Column(db.Text, nullable=True)
    starter_code_json = db.Column(db.Text, nullable=False, default='{}')
    skills_covered = db.Column(db.String(255), default='Python, OOP, Clean Code')
    points_reward = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    milestones = db.relationship('ProjectMilestone', backref='project', lazy=True, cascade='all, delete-orphan')
    test_cases = db.relationship('ProjectTestCase', backref='project', lazy=True, cascade='all, delete-orphan')
    submissions = db.relationship('ProjectSubmission', backref='project', lazy=True, cascade='all, delete-orphan')

    @property
    def starter_code(self):
        try:
            return json.loads(self.starter_code_json or '{}')
        except Exception:
            return {}

    @starter_code.setter
    def starter_code(self, value):
        self.starter_code_json = json.dumps(value)

    def to_dict(self, include_testcases=False, include_hidden=False):
        data = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'category': self.category,
            'difficulty': self.difficulty,
            'description': self.description,
            'scenario': self.scenario,
            'objective': self.objective,
            'requirements': self.requirements,
            'constraints': self.constraints,
            'starter_code': self.starter_code,
            'skills_covered': [s.strip() for s in self.skills_covered.split(',') if s.strip()],
            'points_reward': self.points_reward,
            'milestones': [m.to_dict() for m in self.milestones],
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
        if include_testcases:
            tests = [tc.to_dict(include_hidden=include_hidden) for tc in self.test_cases]
            if not include_hidden:
                tests = [t for t in tests if not t['is_hidden']]
            data['test_cases'] = tests
        return data


class ProjectMilestone(db.Model):
    __tablename__ = 'project_milestones'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)
    order = db.Column(db.Integer, default=1)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    validation_key = db.Column(db.String(100), nullable=False)  # test case group or method signature to match

    def to_dict(self):
        return {
            'id': self.id,
            'order': self.order,
            'title': self.title,
            'description': self.description,
            'validation_key': self.validation_key
        }


class ProjectTestCase(db.Model):
    __tablename__ = 'project_test_cases'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)
    milestone_id = db.Column(db.Integer, db.ForeignKey('project_milestones.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    input_data = db.Column(db.Text, nullable=False)
    expected_output = db.Column(db.Text, nullable=False)
    is_hidden = db.Column(db.Boolean, default=False)
    explanation = db.Column(db.Text, nullable=True)

    def to_dict(self, include_hidden=False):
        if self.is_hidden and not include_hidden:
            return {
                'id': self.id,
                'name': self.name,
                'is_hidden': True,
                'explanation': 'Hidden verification test case'
            }
        return {
            'id': self.id,
            'name': self.name,
            'input_data': self.input_data,
            'expected_output': self.expected_output,
            'is_hidden': self.is_hidden,
            'explanation': self.explanation
        }
