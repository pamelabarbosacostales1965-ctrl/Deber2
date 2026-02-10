from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date

@dataclass
class PriorityContext:
    due_date: date | None

class PriorityStrategy(ABC):
    @abstractmethod
    def base_score(self) -> int:
        raise NotImplementedError

    def compute(self, ctx: PriorityContext) -> int:
        score = self.base_score()

        if ctx.due_date is None:
            return score
        
        days_left = (ctx.due_date - date.today()).days

        if days_left <= 0:
            score += 50
        elif days_left <= 2:
            score += 30
        elif days_left <= 7:
            score += 10
        
        return score

class BugPriority(PriorityStrategy):
    def base_score(self) -> int:
        return 80

class FeaturePriority(PriorityStrategy):
    def base_score(self) -> int:
        return 50

class ChorePriority(PriorityStrategy):
    def base_score(self) -> int:
        return 20