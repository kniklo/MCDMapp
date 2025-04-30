# services/methods/fahp.py
import numpy as np
from app.models import db, AnalysisCriterion, AlternativeEvaluation, AnalysisAlternative
from typing import List, Tuple
from ..base_mcdm import MCDMMethod
from ..utils.matrices import MatrixHelper
# from services.base_mcdm import MCDMMethod
# from services.utils.matrices import MatrixHelper


class TriangularFuzzyNumber:
    __slots__ = ('l', 'm', 'u')  # Оптимизация памяти

    def __init__(self, l: float, m: float, u: float):
        self.l = l  # Нижняя граница
        self.m = m  # Основное значение
        self.u = u  # Верхняя граница

    @classmethod
    def from_crisp(cls, value: float, variation: float = 0.2):
        """Создаёт TFN из чёткого значения с вариацией"""
        delta = value * variation
        return cls(
            l=max(1 / 9, value - delta),
            m=value,
            u=min(9, value + delta)
        )

    def defuzzify(self) -> float:
        """Дефаззификация методом центра тяжести"""
        return (self.l + 2 * self.m + self.u) / 4


class FuzzyAHP(MCDMMethod):
    def calculate(self, analysis_id: int):
        # 1. Получаем и фаззифицируем матрицу критериев
        crisp_matrix = MatrixHelper.build_criteria_comparison_matrix(analysis_id)
        fuzzy_matrix = self._build_fuzzy_matrix(crisp_matrix)

        # 2. Проверяем согласованность
        if not self._check_consistency(fuzzy_matrix):
            raise ValueError("Матрица не согласована")

        # 3. Рассчитываем и сохраняем веса критериев
        criteria_weights = self._calculate_weights(fuzzy_matrix)
        self._save_weights(analysis_id, criteria_weights, is_criteria=True)

        # 4. Обрабатываем альтернативы
        criteria = AnalysisCriterion.query.filter_by(analysis_id=analysis_id).all()
        for criterion in criteria:
            alt_matrix = MatrixHelper.build_alternative_comparison_matrix(criterion.id)
            fuzzy_alt_matrix = self._build_fuzzy_matrix(alt_matrix)
            alt_weights = self._calculate_weights(fuzzy_alt_matrix)
            self._save_weights(criterion.id, alt_weights, is_criteria=False)

        # 5. Рассчитываем финальные оценки
        self._calculate_final_scores(analysis_id)

    def _build_fuzzy_matrix(self, crisp_matrix: List[List[float]]) -> List[List[TriangularFuzzyNumber]]:
        """Строит нечеткую матрицу из четкой"""
        return [
            [TriangularFuzzyNumber.from_crisp(value) if i != j else TriangularFuzzyNumber(1, 1, 1)
             for j, value in enumerate(row)]
            for i, row in enumerate(crisp_matrix)
        ]

    def _calculate_weights(self, matrix: List[List[TriangularFuzzyNumber]]) -> List[float]:
        """Вычисляет дефаззифицированные веса"""
        n = len(matrix)
        weights = []

        for i in range(n):
            product = TriangularFuzzyNumber(1, 1, 1)
            for j in range(n):
                product = self._multiply_tfn(product, matrix[i][j])

            geo_mean = TriangularFuzzyNumber(
                product.l ** (1 / n),
                product.m ** (1 / n),
                product.u ** (1 / n)
            )
            weights.append(geo_mean)

        # Нормализация
        total = sum(w.defuzzify() for w in weights)
        return [w.defuzzify() / total for w in weights]

    def _multiply_tfn(self, a: TriangularFuzzyNumber, b: TriangularFuzzyNumber) -> TriangularFuzzyNumber:
        """Умножение треугольных чисел"""
        return TriangularFuzzyNumber(a.l * b.l, a.m * b.m, a.u * b.u)

    def _check_consistency(self, matrix: List[List[TriangularFuzzyNumber]]) -> bool:
        """Проверка согласованности"""
        crisp_matrix = [[tfn.defuzzify() for tfn in row] for row in matrix]
        cr = MatrixHelper.calculate_consistency_ratio(crisp_matrix)
        return cr <= 0.1

    def _save_weights(self, entity_id: int, weights: List[float], is_criteria: bool):
        """Сохраняет дефаззифицированные веса"""
        if is_criteria:
            entities = AnalysisCriterion.query.filter_by(analysis_id=entity_id).all()
            for entity, weight in zip(entities, weights):
                entity.subj_value_relative = weight
        else:
            evaluations = AlternativeEvaluation.query.filter_by(
                analysis_criterion_id=entity_id
            ).order_by(AlternativeEvaluation.analysis_alternative_id).all()
            for eval, weight in zip(evaluations, weights):
                eval.subj_value_relative = weight
        db.session.commit()

    def _calculate_final_scores(self, analysis_id: int):
        """Расчет финальных оценок"""
        criteria = AnalysisCriterion.query.filter_by(analysis_id=analysis_id).all()
        alternatives = AnalysisAlternative.query.filter_by(analysis_id=analysis_id).all()

        # Матрица весов критериев x альтернатив
        score_matrix = np.array([
            [eval.subj_value_relative for eval in
             AlternativeEvaluation.query.filter_by(analysis_criterion_id=criterion.id)
             .order_by(AlternativeEvaluation.analysis_alternative_id).all()]
            for criterion in criteria
        ])

        # Умножаем веса критериев на оценки альтернатив
        criteria_weights = np.array([c.subj_value_relative for c in criteria])
        final_scores = criteria_weights @ score_matrix

        # Сохраняем результаты
        for alt, score in zip(alternatives, final_scores):
            alt.final_value = score
        db.session.commit()