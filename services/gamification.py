from datetime import datetime, date, timedelta
from models import db, User, Achievement, UserAchievement, Submission, UserProgress

class GamificationService:
    POINTS_MAP = {
        'Easy': 10,
        'Medium': 20,
        'Hard': 30,
        'Beginner': 100,
        'Intermediate': 200,
        'Advanced': 300
    }

    @classmethod
    def record_problem_solve(cls, user: User, problem) -> dict:
        points_earned = cls.POINTS_MAP.get(problem.difficulty, 10)
        user.points += points_earned

        today = date.today()
        if user.last_active_date:
            if user.last_active_date == today - timedelta(days=1):
                user.current_streak += 1
            elif user.last_active_date < today - timedelta(days=1):
                user.current_streak = 1
        else:
            user.current_streak = 1

        user.longest_streak = max(user.longest_streak, user.current_streak)
        user.last_active_date = today

        db.session.commit()
        new_badges = cls.check_and_unlock_badges(user)

        return {
            'points_earned': points_earned,
            'total_points': user.points,
            'streak': user.current_streak,
            'new_badges': new_badges
        }

    @classmethod
    def record_project_completion(cls, user: User, project) -> dict:
        points_earned = cls.POINTS_MAP.get(project.difficulty, 100)
        user.points += points_earned
        db.session.commit()
        new_badges = cls.check_and_unlock_badges(user)
        return {
            'points_earned': points_earned,
            'total_points': user.points,
            'new_badges': new_badges
        }

    @classmethod
    def check_and_unlock_badges(cls, user: User) -> list:
        solved_count = UserProgress.query.filter_by(user_id=user.id, status='solved').count()
        existing_ach_ids = [ua.achievement_id for ua in UserAchievement.query.filter_by(user_id=user.id).all()]

        badges_to_check = [
            ('first_solve', solved_count >= 1),
            ('solve_10', solved_count >= 10),
            ('solve_25', solved_count >= 25),
            ('solve_50', solved_count >= 50),
            ('solve_100', solved_count >= 100),
            ('streak_7', user.current_streak >= 7),
            ('streak_30', user.current_streak >= 30),
            ('dsa_master', solved_count >= 30)
        ]

        newly_unlocked = []
        for code_name, condition in badges_to_check:
            if condition:
                ach = Achievement.query.filter_by(code_name=code_name).first()
                if ach and ach.id not in existing_ach_ids:
                    ua = UserAchievement(user_id=user.id, achievement_id=ach.id)
                    db.session.add(ua)
                    user.points += ach.points
                    newly_unlocked.append(ach.name)

        if newly_unlocked:
            db.session.commit()
        return newly_unlocked
