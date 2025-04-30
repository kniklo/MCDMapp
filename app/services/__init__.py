# services/__init__.py
from .methods.ahp import AHP
from .methods.fuzzy_ahp import FuzzyAHP
from .utils.matrices import MatrixHelper  # Добавляем экспорт

__all__ = ['AHP', 'FuzzyAHP', 'MatrixHelper', 'MCDMService']  # Опционально, но рекомендуется


class MCDMService:
    def __init__(self, method='fahp'):
        self.method_name = method

    def calculate(self, analysis_id):
        if self.method_name == 'fahp':
            return FuzzyAHP().calculate(analysis_id)
        else:
            return AHP().calculate(analysis_id)
