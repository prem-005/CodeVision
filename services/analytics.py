from datetime import datetime, timedelta, date
from models import db, User, Problem, Submission, UserProgress, Contest, ContestSubmission

class AnalyticsService:
    @classmethod
    def get_user_dashboard_stats(cls, user_id: int) -> dict:
        user = User.query.get(user_id)
        if not user:
            return {}

        solved_progress = UserProgress.query.filter_by(user_id=user_id, status='solved').all()
        solved_problem_ids = [p.problem_id for p in solved_progress]
        solved_problems = Problem.query.filter(Problem.id.in_(solved_problem_ids)).all() if solved_problem_ids else []

        easy_solved = sum(1 for p in solved_problems if p.difficulty == 'Easy')
        med_solved = sum(1 for p in solved_problems if p.difficulty == 'Medium')
        hard_solved = sum(1 for p in solved_problems if p.difficulty == 'Hard')

        # Topic Breakdown
        topic_breakdown = {}
        for p in solved_problems:
            t = p.topic or 'General'
            topic_breakdown[t] = topic_breakdown.get(t, 0) + 1

        submissions = Submission.query.filter_by(user_id=user_id).all()

        # Verdict Breakdown
        verdict_breakdown = {}
        for s in submissions:
            v = s.status or 'Unknown'
            verdict_breakdown[v] = verdict_breakdown.get(v, 0) + 1

        runtimes = [s.runtime_ms for s in submissions if s.status == 'Accepted' and s.runtime_ms > 0]
        best_runtime = min(runtimes) if runtimes else 0.0

        today = date.today()
        heatmap_data = {}
        for i in range(30):
            day = today - timedelta(days=i)
            day_str = day.strftime('%Y-%m-%d')
            heatmap_data[day_str] = 0

        for s in submissions:
            if s.submitted_at:
                s_date = s.submitted_at.date().strftime('%Y-%m-%d')
                if s_date in heatmap_data:
                    heatmap_data[s_date] += 1

        # Solved over time (last 14 days)
        solved_over_time = {'labels': [], 'data': []}
        cum_count = 0
        for i in range(13, -1, -1):
            day = today - timedelta(days=i)
            day_str = day.strftime('%b %d')
            # count solved up to this day
            count_at_day = sum(
                1 for p in solved_progress
                if p.completed_at and p.completed_at.date() <= day
            )
            solved_over_time['labels'].append(day_str)
            solved_over_time['data'].append(count_at_day)

        return {
            'total_solved': len(solved_problems),
            'easy_solved': easy_solved,
            'medium_solved': med_solved,
            'hard_solved': hard_solved,
            'difficulty_breakdown': {
                'Easy': easy_solved,
                'Medium': med_solved,
                'Hard': hard_solved
            },
            'topic_breakdown': topic_breakdown if topic_breakdown else {'Arrays': 0, 'Strings': 0, 'DP': 0},
            'verdict_breakdown': verdict_breakdown if verdict_breakdown else {'Accepted': 0, 'Wrong Answer': 0},
            'solved_over_time': solved_over_time,
            'projects_completed': 0,
            'current_streak': user.current_streak,
            'longest_streak': user.longest_streak,
            'total_points': user.points,
            'contest_rating': user.contest_rating,
            'best_runtime': round(best_runtime, 1),
            'heatmap': heatmap_data
        }

    @classmethod
    def get_admin_system_stats(cls) -> dict:
        total_users = User.query.count()
        total_problems = Problem.query.count()
        total_submissions = Submission.query.count()
        accepted_submissions = Submission.query.filter_by(status='Accepted').count()
        acceptance_rate = (accepted_submissions / total_submissions * 100.0) if total_submissions > 0 else 0.0

        return {
            'total_users': total_users,
            'total_problems': total_problems,
            'total_submissions': total_submissions,
            'acceptance_rate': round(acceptance_rate, 1),
            'total_contests': Contest.query.count()
        }
