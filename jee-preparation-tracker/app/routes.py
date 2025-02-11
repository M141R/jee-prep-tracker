import requests
from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models import Subject, Chapter, Topic, MockTest
from app.forms import MockTestForm
from datetime import datetime

@app.route('/')
def index():
    subjects = Subject.query.all()
    return render_template('index.html', subjects=subjects)

@app.route('/dashboard')
def dashboard():
    subjects = Subject.query.all()
    quote = get_motivational_quote()
    mock_tests = MockTest.query.order_by(MockTest.date).all()
    return render_template('dashboard.html', subjects=subjects, quote=quote, mock_tests=mock_tests)

@app.route('/subjects')
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