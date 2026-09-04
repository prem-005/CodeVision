import json
import os
from models import (
    db, User, Problem, TestCase,
    Achievement, Skill, Contest, ContestProblem, UserSettings
)

def generate_question_bank(min_count=1000):
    topics = [
        'Array', 'String', 'Hash Table', 'Two Pointers', 'Sliding Window',
        'Linked List', 'Stack', 'Queue', 'Tree', 'Binary Search',
        'Graph', 'Greedy', 'Dynamic Programming', 'Backtracking', 'Trie',
        'Heap', 'Bit Manipulation', 'Math', 'Sorting', 'Recursion'
    ]
    templates = [
        ("Given an array of integers", "Return the required value after processing the data efficiently."),
        ("Given a string input", "Return the transformed output after scanning the characters carefully."),
        ("Given a set of nodes and edges", "Find the optimal result while respecting the constraints."),
        ("Given a list of values", "Design a solution that runs in linear or logarithmic time."),
    ]

    questions = []
    for i in range(1, min_count + 1):
        difficulty = 'Easy' if i % 3 == 1 else 'Medium' if i % 3 == 2 else 'Hard'
        topic = topics[(i - 1) % len(topics)]
        title_base = topic.replace(' ', '-')
        title = f"{topic} Problem {i}"
        slug = f"{title_base.lower()}-problem-{i}"
        intro, body = templates[(i - 1) % len(templates)]
        description = (
            f"{intro} for problem {i}.\n\n"
            f"{body}\n\n"
            f"Implement an efficient solution that handles the full range of inputs in the constraints below."
        )
        starter = {
            'python': f"def solve(data):\n    # Problem {i}: {title}\n    return data\n\nif __name__ == '__main__':\n    import sys\n    print(solve(list(map(int, sys.stdin.read().split()))))\n",
            'javascript': f"function solve(data) {{\n  // Problem {i}: {title}\n  return data;\n}}\nconst fs = require('fs');\nconst input = fs.readFileSync(0, 'utf-8').trim();\nconst data = input ? input.split(',').map(Number) : [];\nconsole.log(solve(data));\n",
            'cpp': f"#include <iostream>\n#include <vector>\nusing namespace std;\nint main() {{\n    vector<int> data = {{1, 2, 3}};\n    cout << data.size() << endl;\n    return 0;\n}}\n",
            'java': f"public class Solution {{\n    public static void main(String[] args) {{\n        System.out.println(\"Problem {i}\");\n    }}\n}}\n",
            'c': f"#include <stdio.h>\nint main() {{\n    printf(\"Problem {i}\\n\");\n    return 0;\n}}\n"
        }
        sample_input = "1,2,3,4" if difficulty == 'Easy' else "3,5,7,11,13"
        sample_output = "10" if difficulty == 'Easy' else "17" if difficulty == 'Medium' else "23"
        questions.append({
            'id': i,
            'title': title,
            'slug': slug,
            'difficulty': difficulty,
            'topic': topic,
            'company_tags': 'Amazon, Google, Microsoft, TCS, Infosys',
            'description': description,
            'constraints': f"1 <= n <= 10^5\n-10^9 <= values[i] <= 10^9\nO(n) or O(log n) runtime expected.",
            'starter_code': starter,
            'hints': [
                'Think about the most efficient time complexity first.',
                'Identify the core pattern behind the problem before coding.',
                'Validate your idea with small sample input before finalizing.'
            ],
            'acceptance_rate': 50.0 + (i % 19),
            'testcases': [
                {
                    'input_data': sample_input,
                    'expected_output': sample_output,
                    'is_hidden': False,
                    'explanation': 'Sample case for problem validation.'
                },
                {
                    'input_data': '2,4,6,8',
                    'expected_output': '20',
                    'is_hidden': True,
                    'explanation': 'Hidden validation input.'
                }
            ]
        })

    return questions


def seed_database():
    print("Beginning CodeVision database seeding...")

    # 1. Seed Achievements (15 Badges)
    achievements_data = [
        ("First Solve", "first_solve", "Solved your very first coding problem on CodeVision.", "fa-award", 20),
        ("10 Problems Solved", "solve_10", "Reached a milestone of 10 solved DSA problems.", "fa-code", 50),
        ("25 Problems Solved", "solve_25", "Demonstrated consistency by solving 25 coding problems.", "fa-fire", 100),
        ("50 Problems Solved", "solve_50", "Half-century! 50 challenging problems conquered.", "fa-trophy", 200),
        ("100 Problems Solved", "solve_100", "Century Club! 100 algorithm problems solved.", "fa-crown", 500),
        ("First Project", "first_project", "Successfully implemented and submitted your first real-world project.", "fa-laptop-code", 100),
        ("5 Projects Completed", "projects_5", "Built 5 complete software and automation projects in Project Lab.", "fa-cubes", 300),
        ("10 Projects Completed", "projects_10", "Software Architect! 10 production-grade projects finished.", "fa-rocket", 600),
        ("7 Day Streak", "streak_7", "Coded for 7 consecutive days without missing a beat.", "fa-bolt", 100),
        ("30 Day Streak", "streak_30", "Maintained an unbroken 30-day coding streak.", "fa-gem", 300),
        ("Perfect Submission", "perfect_submission", "Passed 100% test cases with top runtime on first attempt.", "fa-star", 50),
        ("Algorithm Master", "algo_master", "Mastered sorting, searching, and recursion fundamentals.", "fa-brain", 150),
        ("DSA Master", "dsa_master", "Solved problems across all data structures including Trees & Graphs.", "fa-medal", 250),
        ("Project Builder", "project_builder", "Demonstrated end-to-end software engineering excellence.", "fa-hammer", 200),
        ("Contest Champion", "contest_champ", "Achieved top ranking in a live timed competitive contest.", "fa-shield-alt", 300)
    ]

    for name, code_name, desc, icon, pts in achievements_data:
        if not Achievement.query.filter_by(code_name=code_name).first():
            db.session.add(Achievement(name=name, code_name=code_name, description=desc, icon=icon, points=pts))

    # 2. Seed Skills (15 dimensions)
    skills_data = [
        ('Python', 'Language'),
        ('Java', 'Language'),
        ('C++', 'Language'),
        ('JavaScript', 'Language'),
        ('Array', 'DSA'),
        ('String', 'DSA'),
        ('Linked List', 'DSA'),
        ('Stack & Queue', 'DSA'),
        ('Tree', 'DSA'),
        ('Graph', 'DSA'),
        ('Sorting & Searching', 'DSA'),
        ('Dynamic Programming', 'DSA'),
        ('OOP', 'Engineering'),
        ('Database', 'System'),
        ('API Design', 'Engineering')
    ]

    for s_name, s_cat in skills_data:
        if not Skill.query.filter_by(name=s_name).first():
            db.session.add(Skill(name=s_name, category=s_cat))

    # 3. Seed Default Users (Admin and Demo Student)
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@codevision.dev',
            role='admin',
            points=1500,
            current_streak=15,
            longest_streak=25,
            contest_rating=1850
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.flush()
        db.session.add(UserSettings(user_id=admin.id))

    if not User.query.filter_by(username='student').first():
        student = User(
            username='student',
            email='student@codevision.dev',
            role='student',
            points=350,
            current_streak=5,
            longest_streak=12,
            contest_rating=1350
        )
        student.set_password('student123')
        db.session.add(student)
        db.session.flush()
        db.session.add(UserSettings(user_id=student.id))

    # 4. Seed Questions from data/questions.json
    questions_file = os.path.join(os.path.dirname(__file__), 'data', 'questions.json')
    if os.path.exists(questions_file):
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions = json.load(f)
    else:
        questions = []

    if len(questions) < 1000:
        questions = generate_question_bank(1000)
        os.makedirs(os.path.dirname(questions_file), exist_ok=True)
        with open(questions_file, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)

    for q in questions:
        existing = Problem.query.filter_by(slug=q['slug']).first()
        if not existing:
            problem = Problem(
                id=q.get('id'),
                title=q['title'],
                slug=q['slug'],
                description=q['description'],
                difficulty=q['difficulty'],
                topic=q['topic'],
                company_tags=q.get('company_tags', ''),
                constraints=q.get('constraints', ''),
                starter_code_json=json.dumps(q.get('starter_code', {})),
                hints=json.dumps(q.get('hints', [])),
                acceptance_rate=q.get('acceptance_rate', 50.0)
            )
            db.session.add(problem)
            db.session.flush()

            for tc in q.get('testcases', []):
                test_case = TestCase(
                    problem_id=problem.id,
                    input_data=tc['input_data'],
                    expected_output=tc['expected_output'],
                    is_hidden=tc.get('is_hidden', False),
                    explanation=tc.get('explanation', '')
                )
                db.session.add(test_case)

    # 5. Seed Contests
    if not Contest.query.filter_by(slug='codevision-weekly-contest-1').first():
        c1 = Contest(
            title="CodeVision Weekly Contest 1",
            slug="codevision-weekly-contest-1",
            description="Test your speed and algorithmic accuracy across 4 curated problems in 60 minutes.",
            duration_minutes=60,
            difficulty="Medium",
            is_active=True
        )
        db.session.add(c1)
        db.session.flush()

        # Link first 4 problems
        for idx, p_id in enumerate([1, 2, 4, 5], start=1):
            if Problem.query.get(p_id):
                db.session.add(ContestProblem(contest_id=c1.id, problem_id=p_id, order_index=idx, points=100 * idx))

    if not Contest.query.filter_by(slug='codevision-biweekly-sprint-2').first():
        c2 = Contest(
            title="CodeVision Biweekly Sprint 2",
            slug="codevision-biweekly-sprint-2",
            description="Fast-paced 30-minute coding challenge focusing on Array and String algorithms.",
            duration_minutes=30,
            difficulty="Easy",
            is_active=True
        )
        db.session.add(c2)
        db.session.flush()

        for idx, p_id in enumerate([3, 7, 8], start=1):
            if Problem.query.get(p_id):
                db.session.add(ContestProblem(contest_id=c2.id, problem_id=p_id, order_index=idx, points=100 * idx))

    db.session.commit()
    print("Database seeding completed successfully!")

if __name__ == '__main__':
    from app import app
    with app.app_context():
        db.create_all()
        seed_database()
