import requests
from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.models import Subject, Chapter, Topic, MockTest, User
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
    quote = get_motivational_quote()
    mock_tests = MockTest.query.order_by(MockTest.date).all()
    return render_template('dashboard.html', subjects=subjects, quote=quote, mock_tests=mock_tests)

@app.route('/subjects')
@login_required
def subjects():
    subjects = Subject.query.all()
    for subject in subjects:
        subject.calculate_coverage()
        db.session.commit()
    return render_template('subjects.html', subjects=subjects)

@app.route('/subject/<int:subject_id>')
def subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return render_template('subject.html', subject=subject)

@app.route('/chapter/<int:chapter_id>', methods=['GET', 'POST'])
@login_required
def chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    if request.method == 'POST':
        chapter.status = request.form['status']
        chapter.prev_year_questions = ','.join(request.form.getlist('prev_year_questions'))
        chapter.revisions = int(request.form['revisions'])
        chapter.calculate_coverage()  # Calculate coverage based on updates
        db.session.commit()
        chapter.subject.calculate_coverage()  # Update subject coverage
        db.session.commit()
        return redirect(url_for('chapter', chapter_id=chapter.id))
    return render_template('chapter.html', chapter=chapter)

@app.route('/mock_tests')
@login_required
def mock_tests():
    tests = MockTest.query.all()
    return render_template('mock_tests.html', tests=tests)

@app.route('/mock_tests/add', methods=['GET', 'POST'])
def add_mock_test():
    form = MockTestForm()
    if form.validate_on_submit():
        mock_test = MockTest(
            name=form.name.data,
            date=form.date.data,
            score=form.score.data,
            total_marks=form.total_marks.data
        )
        db.session.add(mock_test)
        db.session.commit()
        return redirect(url_for('mock_tests'))
    return render_template('add_mock_test.html', form=form)

@app.route('/mock_tests/edit/<int:test_id>', methods=['GET', 'POST'])
def edit_mock_test(test_id):
    mock_test = MockTest.query.get_or_404(test_id)
    form = MockTestForm(obj=mock_test)
    if form.validate_on_submit():
        mock_test.name = form.name.data
        mock_test.date = form.date.data
        mock_test.score = form.score.data
        mock_test.total_marks = form.total_marks.data
        db.session.commit()
        return redirect(url_for('mock_tests'))
    return render_template('edit_mock_test.html', form=form, mock_test=mock_test)

@app.route('/mock_tests/delete/<int:test_id>', methods=['POST'])
def delete_mock_test(test_id):
    mock_test = MockTest.query.get_or_404(test_id)
    db.session.delete(mock_test)
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

@app.route('/test_db')
def test_db():
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()
    return 'User added to the database!'