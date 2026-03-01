from abc import ABC, abstractmethod
from typing import List

class RiskStrategy(ABC):
    @abstractmethod
    def validate(self, amount: float, history: List[float] = None) -> bool:
        pass

class MaxAmountStrategy(RiskStrategy):
    def __init__(self, limit: float = 10000.0):
        self.limit = limit
    def validate(self, amount: float, history: List[float] = None) -> bool:
        return amount <= self.limit

class DailyLimitStrategy(RiskStrategy):
    def __init__(self, daily_limit: float = 5000.0):
        self.daily_limit = daily_limit
    def validate(self, amount: float, history: List[float] = None) -> bool:
        current_total = sum(history) if history else 0
        return (current_total + amount) <= self.daily_limit