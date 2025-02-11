from flask_wtf import FlaskForm
from wtforms import StringField, DateField, FloatField, SubmitField
from wtforms.validators import DataRequired

class MockTestForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    score = FloatField('Score', validators=[DataRequired()])
    total_marks = FloatField('Total Marks', validators=[DataRequired()])
    submit = SubmitField('Submit')