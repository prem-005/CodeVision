from datetime import datetime
from models import db, UserSkill

DEFAULT_SKILLS = [
    'Python', 'Java', 'C++', 'JavaScript',
    'Array', 'String', 'Linked List', 'Stack & Queue',
    'Tree', 'Graph', 'Sorting & Searching', 'Dynamic Programming',
    'OOP', 'Database', 'API Design'
]

class SkillEngine:
    @classmethod
    def initialize_user_skills(cls, user_id: int):
        for s_name in DEFAULT_SKILLS:
            existing = UserSkill.query.filter_by(user_id=user_id, skill_name=s_name).first()
            if not existing:
                uskill = UserSkill(
                    user_id=user_id,
                    skill_name=s_name,
                    score=15.0,
                    problems_solved=0,
                    accuracy=0.0
                )
                db.session.add(uskill)
        db.session.commit()

    @classmethod
    def update_after_problem_solve(cls, user_id: int, topic: str, language: str, passed: bool, difficulty: str) -> dict:
        cls.initialize_user_skills(user_id)
        delta_score = 0.0

        matched_topic = None
        for s in DEFAULT_SKILLS:
            if s.lower() in topic.lower() or topic.lower() in s.lower():
                matched_topic = s
                break
        if not matched_topic:
            matched_topic = 'Array'

        topic_skill = UserSkill.query.filter_by(user_id=user_id, skill_name=matched_topic).first()
        if topic_skill:
            old_score = topic_skill.score
            if passed:
                diff_mult = 1.0 if difficulty == 'Easy' else (2.0 if difficulty == 'Medium' else 3.5)
                topic_skill.score = min(100.0, topic_skill.score + (5.0 * diff_mult))
                topic_skill.problems_solved += 1
            else:
                topic_skill.score = max(5.0, topic_skill.score - 1.5)
            delta_score = topic_skill.score - old_score

        lang_name = 'Python'
        if 'java' in language.lower() and 'script' not in language.lower():
            lang_name = 'Java'
        elif 'cpp' in language.lower() or 'c++' in language.lower():
            lang_name = 'C++'
        elif 'js' in language.lower() or 'javascript' in language.lower():
            lang_name = 'JavaScript'

        lang_skill = UserSkill.query.filter_by(user_id=user_id, skill_name=lang_name).first()
        if lang_skill and passed:
            lang_skill.score = min(100.0, lang_skill.score + 3.0)

        db.session.commit()
        return {
            'topic': matched_topic,
            'delta': round(delta_score, 1),
            'new_score': round(topic_skill.score, 1) if topic_skill else 20.0
        }

    @classmethod
    def get_skill_radar_data(cls, user_id: int) -> dict:
        cls.initialize_user_skills(user_id)
        skills = UserSkill.query.filter_by(user_id=user_id).all()
        labels = [s.skill_name for s in skills]
        scores = [round(s.score, 1) for s in skills]
        return {
            'labels': labels,
            'scores': scores
        }
