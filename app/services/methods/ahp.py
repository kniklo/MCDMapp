# services/methods/ahp.py
import numpy as np
from app.models import db, AnalysisCriterion, AlternativeEvaluation, AnalysisAlternative
from typing import List

from ..base_mcdm import MCDMMethod
from ..utils.matrices import MatrixHelper
# from services.base_mcdm import MCDMMethod
# from services.utils.matrices import MatrixHelper


class AHP(MCDMMethod):
    def calculate(self, analysis_id: int):
        # Шаг 0: Получаем матрицу сравнений критериев
        criteria_matrix = MatrixHelper.build_criteria_comparison_matrix(analysis_id)

        # Шаг 1: Проверка согласованности
        cr = MatrixHelper.calculate_consistency_ratio(criteria_matrix)
        if cr > 0.1:
            raise ValueError("Матрица критериев не согласована")

        # Шаг 2: Рассчет весов критериев
        criteria_weights = self._calculate_priority_vector(criteria_matrix)

        # Шаг 3: Сохраняем веса критериев
        self._save_criteria_weights(analysis_id, criteria_weights)

        # Шаг 4: Обработка альтернатив для каждого критерия
        criteria = AnalysisCriterion.query.filter_by(analysis_id=analysis_id).all()

        for criterion in criteria:
            # Шаг 4.1: Матрица сравнений альтернатив для критерия
            alt_matrix = MatrixHelper.build_alternative_comparison_matrix(criterion.id)

            # Шаг 4.2: Проверка согласованности
            alt_cr = MatrixHelper.calculate_consistency_ratio(alt_matrix)
            if alt_cr > 0.1:
                raise ValueError(f"Матрица альтернатив для критерия {criterion.id} не согласована")

            # Шаг 4.3: Рассчет весов альтернатив
            alt_weights = self._calculate_priority_vector(alt_matrix)

            # Шаг 4.4: Сохраняем веса альтернатив
            self._save_alternative_weights(criterion.id, alt_weights)

        # Шаг 5: Расчет финальных весов
        self._calculate_final_scores(analysis_id)

    def _calculate_priority_vector(self, matrix: List[List[float]]) -> np.ndarray:
        """Рассчитывает вектор приоритетов методом среднего геометрического"""
        geometric_means = np.prod(matrix, axis=1) ** (1 / len(matrix))
        normalized = geometric_means / geometric_means.sum()
        return normalized

    def _save_criteria_weights(self, analysis_id: int, weights: np.ndarray):
        """Сохраняет веса критериев в БД"""
        criteria = AnalysisCriterion.query.filter_by(analysis_id=analysis_id) \
            .order_by(AnalysisCriterion.criterion_id).all()

        for idx, criterion in enumerate(criteria):
            criterion.subj_value_relative = weights[idx]

        db.session.commit()

    def _save_alternative_weights(self, criterion_id: int, weights: np.ndarray):
        """Сохраняет веса альтернатив для критерия"""
        evaluations = AlternativeEvaluation.query.filter_by(
            analysis_criterion_id=criterion_id
        ).order_by(AlternativeEvaluation.analysis_alternative_id).all()

        for idx, eval in enumerate(evaluations):
            eval.subj_value_relative = weights[idx]

        db.session.commit()

    def _calculate_final_scores(self, analysis_id: int):
        """Рассчитывает финальные оценки альтернатив"""
        # Получаем все данные
        criteria = AnalysisCriterion.query.filter_by(analysis_id=analysis_id).all()
        alternatives = AnalysisAlternative.query.filter_by(analysis_id=analysis_id).all()

        # Создаем матрицу весов [критерии x альтернативы]
        weight_matrix = np.zeros((len(criteria), len(alternatives)))

        # Заполняем матрицу
        for i, criterion in enumerate(criteria):
            evaluations = AlternativeEvaluation.query.filter_by(
                analysis_criterion_id=criterion.id
            ).order_by(AlternativeEvaluation.analysis_alternative_id).all()

            for j, eval in enumerate(evaluations):
                weight_matrix[i][j] = eval.subj_value_relative

        # Умножаем на веса критериев
        criteria_weights = np.array([c.subj_value_relative for c in criteria])
        final_scores = np.dot(criteria_weights, weight_matrix)

        # Сохраняем результаты
        for idx, alt in enumerate(alternatives):
            alt.final_value = final_scores[idx]

        db.session.commit()