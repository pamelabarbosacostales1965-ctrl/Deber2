from abc import ABC, abstractmethod

class FeeStrategy(ABC):
    @abstractmethod
    def calculate(self, amount: float) -> float:
        pass

class NoFee(FeeStrategy):
    def calculate(self, amount: float) -> float:
        return 0.0

class FlatFee(FeeStrategy):
    def calculate(self, amount: float) -> float:
        return 5.0

class PercentFee(FeeStrategy):
    def __init__(self, percentage: float = 0.02):
        self.percentage = percentage
    def calculate(self, amount: float) -> float:
        return amount * self.percentage

class TieredFee(FeeStrategy):
    def calculate(self, amount: float) -> float:
        if amount < 100:
            return 1.0
        elif amount < 1000:
            return 10.0
        else:
            return amount * 0.05