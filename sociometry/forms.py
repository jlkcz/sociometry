from flask_wtf import Form
from wtforms import TextField
from wtforms.validators import DataRequired

class NewForm(Form):
    name = TextField('Název třídy',validators=[DataRequired()])
