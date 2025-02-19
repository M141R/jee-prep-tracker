import requests
from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.models import Subject, Chapter, Topic, MockTest, User, UserChapter, UserMockTest
from app.forms import MockTestForm, LoginForm, RegistrationForm
from datetime import datetime

@app.route('/')
def index():
    subjects = Subject.query.all()
    return render_template('index.html', subjects=subjects)

@app.route('/dashboard')
@login_required
def dashboard():
    subjects = Subject.query.all()
    user_coverages = {subject.id: subject.calculate_user_coverage(current_user.id) for subject in subjects}
    user_chapters = UserChapter.query.filter_by(user_id=current_user.id).all()
    user_mock_tests = UserMockTest.query.filter_by(user_id=current_user.id).all()
    quote = get_motivational_quote()
    return render_template('dashboard.html', subjects=subjects, user_chapters=user_chapters, quote=quote, user_mock_tests=user_mock_tests,user_coverages=user_coverages)

@app.route('/subjects')
@login_required
def subjects():
    subjects = Subject.query.all()
    user_coverages = {subject.id: subject.calculate_user_coverage(current_user.id) for subject in subjects}
    return render_template('subjects.html', subjects=subjects, user_coverages=user_coverages)

@app.route('/subject/<int:subject_id>')
@login_required
def subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject.id).all()
    user_chapters = {uc.chapter_id: uc for uc in UserChapter.query.filter_by(user_id=current_user.id).all()}
    return render_template('subject.html', subject=subject, chapters=chapters, user_chapters=user_chapters)

@app.route('/chapter/<int:chapter_id>', methods=['GET', 'POST'])
@login_required
def chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    user_chapter = UserChapter.query.filter_by(user_id=current_user.id, chapter_id=chapter.id).first()
    if not user_chapter:
        user_chapter = UserChapter(user_id=current_user.id, chapter_id=chapter.id)
        db.session.add(user_chapter)
        db.session.commit()
    if request.method == 'POST':
        user_chapter.status = request.form['status']
        user_chapter.prev_year_questions = ','.join(request.form.getlist('prev_year_questions'))
        user_chapter.revisions = int(request.form['revisions'])
        user_chapter.calculate_coverage()  # Calculate coverage based on updates
        db.session.commit()
        return redirect(url_for('chapter', chapter_id=chapter.id))
    return render_template('chapter.html', chapter=chapter, user_chapter=user_chapter)

@app.route('/mock_tests')
@login_required
def mock_tests():
    user_mock_tests = UserMockTest.query.filter_by(user_id=current_user.id).all()
    return render_template('mock_tests.html', user_mock_tests=user_mock_tests)

@app.route('/mock_tests/add', methods=['GET', 'POST'])
@login_required
def add_mock_test():
    form = MockTestForm()
    if form.validate_on_submit():
        mock_test = MockTest(
            name=form.name.data,
            date=form.date.data
        )
        db.session.add(mock_test)
        db.session.commit()
        user_mock_test = UserMockTest(
            user_id=current_user.id,
            mock_test_id=mock_test.id,
            score=form.score.data,
            total_marks=form.total_marks.data
        )
        db.session.add(user_mock_test)
        db.session.commit()
        return redirect(url_for('mock_tests'))
    return render_template('add_mock_test.html', form=form)

@app.route('/mock_tests/edit/<int:user_mock_test_id>', methods=['GET', 'POST'])
@login_required
def edit_mock_test(user_mock_test_id):
    user_mock_test = UserMockTest.query.get_or_404(user_mock_test_id)
    if user_mock_test.user_id != current_user.id:
        flash('You do not have access to this mock test.')
        return redirect(url_for('mock_tests'))
    form = MockTestForm(obj=user_mock_test)
    if form.validate_on_submit():
        user_mock_test.mock_test.name = form.name.data
        user_mock_test.mock_test.date = form.date.data
        user_mock_test.score = form.score.data
        user_mock_test.total_marks = form.total_marks.data
        db.session.commit()
        return redirect(url_for('mock_tests'))
    return render_template('edit_mock_test.html', form=form, user_mock_test=user_mock_test)

@app.route('/mock_tests/delete/<int:user_mock_test_id>', methods=['POST'])
@login_required
def delete_mock_test(user_mock_test_id):
    user_mock_test = UserMockTest.query.get_or_404(user_mock_test_id)
    if user_mock_test.user_id != current_user.id:
        flash('You do not have access to this mock test.')
        return redirect(url_for('mock_tests'))
    db.session.delete(user_mock_test)
    db.session.commit()
    return redirect(url_for('mock_tests'))

def get_motivational_quote():
    response = requests.get("https://api.quotable.io/random?tags=motivational", verify=False)
    if response.status_code == 200:
        data = response.json()
        return f'"{data["content"]}" - {data["author"]}'
    return "Keep pushing forward!"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# @app.route('/test_db')
# def test_db():
#     user = User(username='testuser', email='test@example.com')
#     user.set_password('password')
#     db.session.add(user)
#     db.session.commit()
#     return 'User added to the database!'