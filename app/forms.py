from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.form import FormField
from wtforms.fields.list import FieldList
from wtforms.fields.numeric import FloatField
from wtforms.validators import DataRequired, ValidationError, NumberRange, AnyOf

import sqlalchemy as sa
from app import db
from app.models import Alternative, Criterion, Expert, Task, Analysis, AnalysisAlternative, AnalysisCriterion


class ExpertForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    submit = SubmitField('Новый')

    def validate_name(self, name):
        x = db.session.scalar(sa.select(Expert).where(
            Expert.name == name.data))
        if x is not None:
            raise ValidationError('This analyse already exists.')


class TaskForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    description = StringField('Описание', validators=[])
    submit = SubmitField('Новый')

    def validate_name(self, name):
        x = db.session.scalar(sa.select(Task).where(
            Task.name == name.data))
        if x is not None:
            raise ValidationError('This analyse already exists.')


class AlternativeForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    submit = SubmitField('Новый')

    def validate_name(self, name):
        x = db.session.scalar(sa.select(Alternative).where(
            Alternative.name == name.data))
        if x is not None:
            raise ValidationError('This alternative already exists.')


class CriterionForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    submit = SubmitField('Новый')

    def validate_name(self, name):
        x = db.session.scalar(sa.select(Criterion).where(
            Criterion.name == name.data))
        if x is not None:
            raise ValidationError('This criterion already exists.')


class MatrixCellForm(FlaskForm):
    value = FloatField('Value', validators=[DataRequired()])


class ComparisonMatrixForm(FlaskForm):
    matrix = FieldList(FieldList(FormField(MatrixCellForm)), min_entries=1)
    submit = SubmitField("Submit")

