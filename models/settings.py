from models import db

class UserSettings(db.Model):
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    theme = db.Column(db.String(20), default='dark')
    editor_theme = db.Column(db.String(30), default='vs-dark')
    editor_font_size = db.Column(db.Integer, default=14)
    default_language = db.Column(db.String(20), default='python')
    tab_size = db.Column(db.Integer, default=4)
    auto_save = db.Column(db.Boolean, default=True)
    visualizer_speed = db.Column(db.String(10), default='1x')
    sound_effects = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'theme': self.theme,
            'editor_theme': self.editor_theme,
            'editor_font_size': self.editor_font_size,
            'default_language': self.default_language,
            'tab_size': self.tab_size,
            'auto_save': self.auto_save,
            'visualizer_speed': self.visualizer_speed,
            'sound_effects': self.sound_effects
        }
