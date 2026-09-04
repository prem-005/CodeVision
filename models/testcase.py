from models import db

class TestCase(db.Model):
    __tablename__ = 'test_cases'

    id = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False, index=True)
    input_data = db.Column(db.Text, nullable=False)
    expected_output = db.Column(db.Text, nullable=False)
    is_hidden = db.Column(db.Boolean, default=False)
    explanation = db.Column(db.Text, nullable=True)

    def to_dict(self, include_hidden=False):
        if self.is_hidden and not include_hidden:
            return {
                'id': self.id,
                'problem_id': self.problem_id,
                'is_hidden': True,
                'explanation': 'Hidden test case for submission evaluation'
            }
        return {
            'id': self.id,
            'problem_id': self.problem_id,
            'input_data': self.input_data,
            'expected_output': self.expected_output,
            'is_hidden': self.is_hidden,
            'explanation': self.explanation
        }
