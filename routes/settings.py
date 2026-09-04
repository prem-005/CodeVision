from flask import Blueprint, render_template, request, jsonify, session
from models import db, UserSettings, User, Note, Bookmark

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings')
def settings_page():
    return render_template('settings.html')


@settings_bp.route('/notes')
def notes_page():
    return render_template('notes.html')


@settings_bp.route('/api/settings', methods=['GET', 'POST'])
def api_user_settings():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    settings = UserSettings.query.filter_by(user_id=user_id).first()
    if not settings:
        settings = UserSettings(user_id=user_id)
        db.session.add(settings)
        db.session.commit()

    if request.method == 'POST':
        data = request.get_json() or {}
        settings.theme = data.get('theme', settings.theme)
        settings.editor_theme = data.get('editor_theme', settings.editor_theme)
        settings.editor_font_size = int(data.get('editor_font_size', settings.editor_font_size))
        settings.default_language = data.get('default_language', settings.default_language)
        settings.tab_size = int(data.get('tab_size', settings.tab_size))
        settings.auto_save = bool(data.get('auto_save', settings.auto_save))
        settings.visualizer_speed = data.get('visualizer_speed', settings.visualizer_speed)
        settings.sound_effects = bool(data.get('sound_effects', settings.sound_effects))
        db.session.commit()
        return jsonify({'success': True, 'settings': settings.to_dict()})

    return jsonify({'success': True, 'settings': settings.to_dict()})


@settings_bp.route('/api/notes', methods=['GET', 'POST', 'DELETE'])
def api_notes():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    if request.method == 'POST':
        data = request.get_json() or {}
        problem_id = data.get('problem_id')
        content = data.get('content', '')
        tag = data.get('tag', 'Important')

        note = Note.query.filter_by(user_id=user_id, problem_id=problem_id).first()
        if not note:
            note = Note(user_id=user_id, problem_id=problem_id, content=content, tag=tag)
            db.session.add(note)
        else:
            note.content = content
            note.tag = tag
        db.session.commit()
        return jsonify({'success': True, 'note': note.to_dict()})

    notes = Note.query.filter_by(user_id=user_id).order_by(Note.updated_at.desc()).all()
    return jsonify({'success': True, 'notes': [n.to_dict() for n in notes]})


@settings_bp.route('/api/bookmarks', methods=['GET', 'POST', 'DELETE'])
def api_bookmarks():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    if request.method == 'POST':
        data = request.get_json() or {}
        problem_id = data.get('problem_id')
        folder = data.get('folder', 'Favorites')

        bm = Bookmark.query.filter_by(user_id=user_id, problem_id=problem_id).first()
        if not bm:
            bm = Bookmark(user_id=user_id, problem_id=problem_id, folder=folder)
            db.session.add(bm)
            db.session.commit()
            return jsonify({'success': True, 'bookmarked': True})
        else:
            db.session.delete(bm)
            db.session.commit()
            return jsonify({'success': True, 'bookmarked': False})

    bookmarks = Bookmark.query.filter_by(user_id=user_id).all()
    return jsonify({'success': True, 'bookmarks': [b.to_dict() for b in bookmarks]})
