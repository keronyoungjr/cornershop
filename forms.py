from flask_wtf import FlaskForm
from wtforms import StringField

from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    item = StringField('item', validators=[DataRequired()])
