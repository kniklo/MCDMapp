# services/utils/matrices.py вспомогательный для работы с матрицами

import numpy as np
from typing import List
from app.models import AnalysisCriterion, AlternativeEvaluation


class MatrixHelper:
    @staticmethod
    def _build_matrix_from_importances(importances: List[float]) -> List[List[float]]:
        """Общая логика построения матрицы из списка важностей"""
        size = len(importances)
        matrix = np.ones((size, size))

        base = 1.2
        for i in range(size):
            for j in range(size):
                if i != j:
                    # matrix[i][j] = round(importances[i] / importances[j], 2)
                    matrix[i][j] = round(np.power(base, importances[i]) / np.power(base, importances[j]), 2)

        return matrix.tolist()

    @staticmethod
    def build_criteria_comparison_matrix(analysis_id: int) -> List[List[float]]:
        """
        Строит матрицу парных сравнений критериев на основе subj_value
        :param analysis_id: ID анализа
        :return: Матрица NxN, где N — количество критериев
        """
        criteria = AnalysisCriterion.query.filter_by(analysis_id=analysis_id) \
            .order_by(AnalysisCriterion.criterion_id) \
            .all()

        importances = [c.subj_value for c in criteria]
        return MatrixHelper._build_matrix_from_importances(importances)

    @staticmethod
    def build_alternative_comparison_matrix(criterion_id: int) -> List[List[float]]:
        """
        Строит матрицу парных сравнений альтернатив для конкретного критерия
        :param criterion_id: ID критерия
        :return: Матрица MxM, где M — количество альтернатив
        """
        evaluations = AlternativeEvaluation.query.filter_by(
            analysis_criterion_id=criterion_id
        ).order_by(AlternativeEvaluation.analysis_alternative_id).all()

        importances = [e.subj_value for e in evaluations]
        return MatrixHelper._build_matrix_from_importances(importances)

    @staticmethod
    def calculate_consistency_ratio(matrix: List[List[float]]) -> float:
        """Рассчитывает коэффициент согласованности матрицы"""
        n = len(matrix)
        if n <= 2:  # Для матриц 1x1 и 2x2 согласованность идеальная
            return 0.0

        # Вычисляем максимальное собственное значение
        eigenvalues = np.linalg.eigvals(matrix)
        max_eigenvalue = max(eigenvalues.real)

        # Индекс согласованности
        CI = (max_eigenvalue - n) / (n - 1)

        # Случайный индекс (RI)
        RI_TABLE = {3: 0.58, 4: 0.9, 5: 1.12, 6: 1.24, 7: 1.32,
                    8: 1.41, 9: 1.45, 10: 1.49}
        RI = RI_TABLE.get(n, 1.98 * (n - 2) / n) # Для больших матриц в литературе предлагают Формулу Саати (для n ≥ 11)

        return CI / RI


