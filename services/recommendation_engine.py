from models import Problem, Submission, UserProgress, UserSkill

class RecommendationEngine:
    @classmethod
    def get_recommendations_for_user(cls, user) -> dict:
        if not user:
            return cls._get_default_recommendations()

        submissions = Submission.query.filter_by(user_id=user.id).all()
        solved_problem_ids = [p.problem_id for p in UserProgress.query.filter_by(user_id=user.id, status='solved').all()]

        user_skills = UserSkill.query.filter_by(user_id=user.id).all()
        topic_scores = {s.skill_name: s.score for s in user_skills}

        weak_topic = 'Array'
        if topic_scores:
            weak_topic = min(topic_scores, key=topic_scores.get)
        else:
            failed_topics = {}
            for s in submissions:
                if s.status != 'Accepted' and s.problem:
                    failed_topics[s.problem.topic] = failed_topics.get(s.problem.topic, 0) + 1
            if failed_topics:
                weak_topic = max(failed_topics, key=failed_topics.get)

        rec_problems = Problem.query.filter(~Problem.id.in_(solved_problem_ids) if solved_problem_ids else True).order_by(Problem.id.asc()).limit(3).all()

        return {
            'weak_topic': weak_topic,
            'weak_topic_score': round(topic_scores.get(weak_topic, 35.0), 1),
            'recommended_problems': [p.to_dict() for p in rec_problems],
            'recommended_projects': [],
            'reason': f'Weak topic detected: {weak_topic}. Mastering fundamental patterns in {weak_topic} will boost your overall DSA accuracy.'
        }

    @classmethod
    def _get_default_recommendations(cls) -> dict:
        rec_problems = Problem.query.order_by(Problem.id.asc()).limit(3).all()
        return {
            'weak_topic': 'Array',
            'weak_topic_score': 50.0,
            'recommended_problems': [p.to_dict() for p in rec_problems],
            'recommended_projects': [],
            'reason': 'Start your journey with foundational Array and Hash Table techniques.'
        }
