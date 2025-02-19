from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    chapters = db.relationship('Chapter', backref='subject', lazy='dynamic')

    def calculate_user_coverage(self, user_id):
        user_chapters = UserChapter.query.filter_by(user_id=user_id).all()
        total_coverage = 0
        num_chapters = self.chapters.count()
        for chapter in self.chapters:
            user_chapter = next((uc for uc in user_chapters if uc.chapter_id == chapter.id), None)
            if user_chapter:
                total_coverage += user_chapter.coverage
        return round(total_coverage / num_chapters) if num_chapters > 0 else 0

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    topics = db.relationship('Topic', backref='chapter', lazy='dynamic')

class UserChapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'))
    coverage = db.Column(db.Float, default=0.0)  # Coverage percentage
    status = db.Column(db.String(64), default='Not Started')  # Status
    prev_year_questions = db.Column(db.String(64), default='')  # Years of previous year questions solved
    revisions = db.Column(db.Integer, default=0)  # Number of revisions

    def calculate_coverage(self):
        # Define weights for each factor
        status_weight = {
            'Not Started': 0,
            'Basic': 0.3,
            'Intermediate': 0.6,
            'Master': 1.0
        }
        prev_year_weight = 0.1  # Each year solved adds 10%
        revision_weight = 0.1  # Each revision adds 10%
        # Calculate coverage based on status
        coverage = status_weight.get(self.status, 0)

        # Add coverage for previous year questions solved
        years_solved = len(self.prev_year_questions.split(',')) if self.prev_year_questions else 0
        coverage += years_solved * prev_year_weight

        # Add coverage for revisions
        coverage += self.revisions * revision_weight

        # Ensure coverage does not exceed 100%
        self.coverage = min(coverage, 1.0) * 100

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'))
    status = db.Column(db.String(64), default='Not Started')  # Status

class MockTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    date = db.Column(db.Date, nullable=False)

class UserMockTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    mock_test_id = db.Column(db.Integer, db.ForeignKey('mock_test.id'))
    score = db.Column(db.Float, nullable=False)
    total_marks = db.Column(db.Float, nullable=False)
    mock_test = db.relationship('MockTest', backref='user_mock_tests')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(500))
    user_mock_tests = db.relationship('UserMockTest', backref='user', lazy='dynamic')
    user_chapters = db.relationship('UserChapter', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))