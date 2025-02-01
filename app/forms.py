from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError

import sqlalchemy as sa
from app import db
from app.models import Alternative


class AlternativeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Save')

    def validate_name(self, name):
        user = db.session.scalar(sa.select(Alternative).where(
            Alternative.name == name.data))
        if user is not None:
            raise ValidationError('This alternative already exists.')
