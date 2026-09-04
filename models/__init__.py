from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.project import Project, ProjectMilestone, ProjectTestCase
from models.project_submission import ProjectSubmission
from models.user import User
from models.problem import Problem
from models.testcase import TestCase
from models.submission import Submission
from models.achievement import Achievement, UserAchievement
from models.progress import UserProgress, Skill, UserSkill, Recommendation
from models.contest import Contest, ContestProblem
from models.contest_submission import ContestSubmission
from models.note import Note
from models.bookmark import Bookmark
from models.settings import UserSettings
