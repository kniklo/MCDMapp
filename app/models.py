#app/models.py
import sqlalchemy as sa
import sqlalchemy.orm as so
from fsspec.registry import default

from app import db
from typing import Optional


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
    expert_id = db.Column(db.Integer, db.ForeignKey('expert.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)

    # Связи
    analysis_alternatives = db.relationship('AnalysisAlternative', backref='analysis', lazy=True)
    analysis_criterion = db.relationship('AnalysisCriterion', backref='analysis', lazy=True)

    @classmethod
    def get_by_expert_task_id(cls, expert_id, task_id):
        return cls.query.filter_by(expert_id=expert_id, task_id=task_id).first()

    @classmethod
    def get_by_task_id_and_not_expert_id(cls, task_id, expert_id):
        return cls.query.filter(cls.task_id == task_id, cls.expert_id != expert_id).first()


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
            Alternative.name,
            Alternative.id
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
            Criterion.id
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

    # @classmethod
    # def build_comparison_matrix(cls, analysis_id: int) -> list[list[float]]:
    #     """
    #     Строит матрицу парных сравнений на основе subj_value критериев.
    #     Возвращает квадратную матрицу NxN, где N - число критериев.
    #     """
    #     # Получаем все критерии анализа, отсортированные по ID
    #     criteria = cls.query.filter_by(analysis_id=analysis_id) \
    #         .order_by(cls.criterion_id) \
    #         .all()
    #
    #     # Проверка входных данных
    #     if not criteria:
    #         raise ValueError("No criteria found for this analysis")
    #     if any(c.subj_value <= 0 for c in criteria):
    #         raise ValueError("All subj_value must be positive")
    #
    #     # Создаем матрицу
    #     size = len(criteria)
    #     matrix = np.ones((size, size), dtype=np.float64)
    #
    #     for i in range(size):
    #         for j in range(size):
    #             if i != j:
    #                 matrix[i][j] = criteria[j].subj_value / criteria[i].subj_value
    #
    #     return matrix.tolist()


# Модель для таблицы `alternative_evaluation`
class AlternativeEvaluation(db.Model):
    __tablename__ = 'alternative_evaluation'
    id = db.Column(db.Integer, primary_key=True)
    analysis_alternative_id = db.Column(db.Integer, db.ForeignKey('analysis_alternative.id'), nullable=False)
    analysis_criterion_id = db.Column(db.Integer, db.ForeignKey('analysis_criterion.id'), nullable=False)
    subj_value = db.Column(db.Float, nullable=False, default=1)
    subj_value_relative = db.Column(db.Float, nullable=False, default=0)

    @classmethod
    def get_by_alternative_id(cls, alternative_id):
        results = (
            db.session.query(
                cls.id,
                cls.analysis_criterion_id,
                cls.subj_value
            )
            .filter(cls.analysis_alternative_id == alternative_id)
            .all()
        )
        res = [
            {
                'id': result.id,
                'criterion_id': result.analysis_criterion_id,
                'subj_value': result.subj_value
            }
            for result in results]
        return res


# Модель для таблицы `criterion`
class Criterion(db.Model):
    __tablename__ = 'criterion'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(65), unique=True, nullable=False)

    # Связи
    analysis_criterion = db.relationship('AnalysisCriterion', backref='criterion', lazy=True)


# Модель для таблицы `expert`
class Expert(db.Model):
    __tablename__ = 'expert'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(45), unique=True, nullable=False)

    # Связи
    analyses = db.relationship('Analysis', backref='expert', lazy=True)


# Модель для таблицы `task`
class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(65), nullable=False)
    description = db.Column(db.String(95), nullable=True)
    fl_new = db.Column(db.Integer, nullable=False, default=1)

    # Связи
    analyses = db.relationship('Analysis', backref='task', lazy=True)
    task_data = db.relationship('TaskData', backref='task', lazy=True)

    @classmethod
    def get_task(cls, task_id):
        task = Task.query.get(task_id)
        return task if task else None

    @classmethod
    def update_fl_new_by_id(cls, task_id, new_value):
        task = Task.query.get(task_id)
        if task:
            task.fl_new = new_value
            db.session.commit()
        return task if task else None


# Модель для таблицы `task_data`
class TaskData(db.Model):
    __tablename__ = 'task_data'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    criterion_id = db.Column(db.Integer, db.ForeignKey('criterion.id'), nullable=False)
    alternative_id = db.Column(db.Integer, db.ForeignKey('alternative.id'), nullable=False)
    value = db.Column(db.String(60), nullable=False)
