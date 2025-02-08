from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.form import FormField
from wtforms.fields.list import FieldList
from wtforms.fields.numeric import FloatField
from wtforms.validators import DataRequired, ValidationError, NumberRange

import sqlalchemy as sa
from app import db
from app.models import Alternative, Criterion


class AlternativeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Save')

    def validate_name(self, name):
        x = db.session.scalar(sa.select(Alternative).where(
            Alternative.name == name.data))
        if x is not None:
            raise ValidationError('This alternative already exists.')


class CriteriaForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Save')

    def validate_name(self, name):
        x = db.session.scalar(sa.select(Criterion).where(
            Criterion.name == name.data))
        if x is not None:
            raise ValidationError('This criterion already exists.')


class WeightForm(FlaskForm):
    weight = FloatField('Weight', validators=[DataRequired(), NumberRange(min=0, max=1)])


class CriteriaWeightForm(FlaskForm):
    weights = FieldList(FormField(WeightForm), min_entries=1)
    submit = SubmitField('Save to JSON')