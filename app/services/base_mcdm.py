# services/base_mcdm.py абстрактный базовый класс для всех MCDM-методов
from abc import ABC, abstractmethod
from typing import List


class MCDMMethod(ABC):
    @abstractmethod
    def calculate(self, analysis_id: int) -> List[float]:
        """Основной метод расчета весов"""
        pass


