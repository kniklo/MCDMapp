from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import joinedload


# Модель для таблицы `alternative`
class Alternative(db.Model):
    __tablename__ = 'alternative'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(65), unique=True, nullable=False)

    # Связи
    analysis_alternatives = db.relationship('AnalysisAlternative', backref='alternative', lazy=True)


# Модель для таблицы `analysis`
class Analysis(db.Model):
    __tablename__ = 'analysis'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    expert_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    create_date = db.Column(db.DateTime, nullable=False)

    # Связи
    analysis_alternatives = db.relationship('AnalysisAlternative', backref='analysis', lazy=True)
    analysis_criterion = db.relationship('AnalysisCriterion', backref='analysis', lazy=True)

    @classmethod
    def get_by_task_id(cls, task_id):
        res = db.session.query(
            cls.id,
            User.username.label('name'),
            User.id.label('expert_id'),
            cls.create_date
        ).join(
            User,
            User.id == cls.expert_id
        ).filter(
            cls.task_id == task_id
        ).all()
        return res


# Модель для таблицы `analysis_alternative`
class AnalysisAlternative(db.Model):
    __tablename__ = 'analysis_alternative'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis.id'), nullable=False)
    alternative_id = db.Column(db.Integer, db.ForeignKey('alternative.id'), nullable=False)
    final_value = db.Column(db.Float, nullable=False, default=0)

    # Связи
    alternative_evaluations = db.relationship('AlternativeEvaluation', backref='analysis_alternative', lazy=True)

    @classmethod
    def get_by_analysis_id(cls, analysis_id):
        res = db.session.query(
            cls.id,
            Alternative.name.label('name'),
            cls.final_value,
            Alternative.id.label('alt_id')
        ).join(
            Alternative,
            Alternative.id == cls.alternative_id
        ).filter(
            cls.analysis_id == analysis_id
        ).all()
        return res

    @classmethod
    def delete_by_id(cls, alt_id):
        alternative = cls.query.get(alt_id)
        if alternative:
            db.session.delete(alternative)
            db.session.commit()
            return True
        return False


# Модель для таблицы `analysis_criterion`
class AnalysisCriterion(db.Model):
    __tablename__ = 'analysis_criterion'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis.id'), nullable=False)
    criterion_id = db.Column(db.Integer, db.ForeignKey('criterion.id'), nullable=False)
    subj_value = db.Column(db.Float, nullable=False, default=1)
    subj_value_relative = db.Column(db.Float, nullable=False, default=0)

    # Связи
    alternative_evaluations = db.relationship('AlternativeEvaluation', backref='analysis_criterion', lazy=True)

    @classmethod
    def get_by_analysis_id(cls, analysis_id):
        res = db.session.query(
            cls.id,
            Criterion.name,
            cls.subj_value,
            cls.subj_value_relative,
            Criterion.id.label('cr_id')
        ).join(
            Criterion,
            Criterion.id == cls.criterion_id
        ).filter(
            cls.analysis_id == analysis_id
        ).all()
        return res

    @classmethod
    def delete_by_id(cls, cr_id):
        criterion = cls.query.get(cr_id)
        if criterion:
            db.session.delete(criterion)
            db.session.commit()
            return True
        return False


# Модель для таблицы `alternative_evaluation`
class AlternativeEvaluation(db.Model):
    __tablename__ = 'alternative_evaluation'
    id = db.Column(db.Integer, primary_key=True)
    analysis_alternative_id = db.Column(db.Integer, db.ForeignKey('analysis_alternative.id'), nullable=False)
    analysis_criterion_id = db.Column(db.Integer, db.ForeignKey('analysis_criterion.id'), nullable=False)
    subj_value = db.Column(db.Float, nullable=False, default=1)
    subj_value_relative = db.Column(db.Float, nullable=False, default=0)

    @classmethod
    def get_alternative_evaluations_by_analysis(cls, analysis_id):
        return AlternativeEvaluation.query \
            .join(AnalysisCriterion, AlternativeEvaluation.analysis_criterion_id == AnalysisCriterion.id) \
            .join(AnalysisAlternative, AlternativeEvaluation.analysis_alternative_id == AnalysisAlternative.id) \
            .filter((AnalysisCriterion.analysis_id == analysis_id) | (AnalysisAlternative.analysis_id == analysis_id)) \
            .all()


# Модель для таблицы `criterion`
class Criterion(db.Model):
    __tablename__ = 'criterion'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(65), unique=True, nullable=False)

    # Связи
    analysis_criterion = db.relationship('AnalysisCriterion', backref='criterion', lazy=True)


# Модель для таблицы `task`
class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(65), nullable=False)
    description = db.Column(db.Text, nullable=True)
    fl_new = db.Column(db.Integer, nullable=False, default=1)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    create_date = db.Column(db.DateTime, nullable=False)

    # Связи
    analyses = db.relationship('Analysis', backref='task', lazy=True)
    task_data = db.relationship('TaskData', backref='task', lazy=True)
    owner_user = db.relationship('User', backref='tasks', foreign_keys=[owner])

    @classmethod
    def get_task(cls, task_id):
        task = db.session.query(
            Task.id,
            Task.name,
            Task.description,
            Task.fl_new,
            Task.create_date,
            User.username.label('owner')
        ).join(
            User, Task.owner == User.id
        ).filter(
            Task.id == task_id
        ).first()

        return task._asdict() if task else None

    @classmethod
    def update_fl_new_by_id(cls, task_id, new_value):
        task = Task.query.get(task_id)
        if task:
            task.fl_new = new_value
            db.session.commit()
        return task if task else None


class TaskAlternative(db.Model):
    __tablename__ = 'task_alternative'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    alternative_id = db.Column(db.Integer, db.ForeignKey('alternative.id'), nullable=False)

    task = db.relationship('Task', backref='task_alternatives')
    alternative = db.relationship('Alternative', backref='alternative_tasks')

    @classmethod
    def get_by_task_id(cls, task_id):
        res = db.session.query(
            cls.id,
            Alternative.name
        ).join(
            Alternative,
            Alternative.id == cls.alternative_id
        ).filter(
            cls.task_id == task_id
        ).all()
        return res

    @classmethod
    def delete_by_id(cls, alt_id):
        alternative = cls.query.get(alt_id)
        if alternative:
            db.session.delete(alternative)
            db.session.commit()
            return True
        return False


class TaskCriterion(db.Model):
    __tablename__ = 'task_criterion'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    criterion_id = db.Column(db.Integer, db.ForeignKey('criterion.id'), nullable=False)

    task = db.relationship('Task', backref='task_criterions')
    criterion = db.relationship('Criterion', backref='criterion_tasks')

    @classmethod
    def get_by_task_id(cls, task_id):
        res = db.session.query(
            cls.id,
            Criterion.name
        ).join(
            Criterion,
            Criterion.id == cls.criterion_id
        ).filter(
            cls.task_id == task_id
        ).all()
        return res

    @classmethod
    def delete_by_id(cls, cr_id):
        criterion = cls.query.get(cr_id)
        if criterion:
            db.session.delete(criterion)
            db.session.commit()
            return True
        return False


# Модель для таблицы `task_data`
class TaskData(db.Model):
    __tablename__ = 'task_data'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    criterion_id = db.Column(db.Integer, db.ForeignKey('criterion.id'), nullable=False)
    alternative_id = db.Column(db.Integer, db.ForeignKey('alternative.id'), nullable=False)
    value = db.Column(db.String(60), nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(256))

    analyses = db.relationship('Analysis', backref='expert', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)