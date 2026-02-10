from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from uuid import uuid4

from app.domain.enums import TaskStatus
from app.domain.exceptions import InvalidStatusTransition, ValidationError, NotFoundError
from app.domain.priority import PriorityStrategy, PriorityContext

@dataclass
class Project:
    name: str
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if not self.name or len(self.name.strip()) < 5:
            raise ValidationError('Project.name debe tener como minimo 5 caracteres')

@dataclass
class Task:
    title: str
    project_id: str
    strategy: PriorityStrategy
    due_date: date | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    _status: TaskStatus = field(default_factory=TaskStatus.TODO)

    def __post_init__(self) -> None:
        if not self.title or len(self.title.strip()) < 5:
            raise ValidationError('Task.title debe tener como minimo 5 caracteres')
    
    @property
    def status(self) -> TaskStatus:
        return self._status
    
    @property
    def priority_score(self) -> int:
        return self.strategy.compute(
            PriorityContext(due_date=self.due_date)
        )
    
    def update_due_date(self, new_due_date: date | None) -> None:
        self.due_date = new_due_date

    def update_title(self, new_title: str) -> None:
        if not new_title or len(new_title) < 5:
            raise ValidationError('El nuevo titulo debe tener como minimo 5 caracteres')
        self.title = new_title

    def transtition_to(self, new_status: TaskStatus) -> None:
        allowed = {
            TaskStatus.TODO: {TaskStatus.DOING},
            TaskStatus.DOING: {TaskStatus.DONE},
            TaskStatus.DONE: set()
        }

        if new_status == self._status:
            return

        if new_status not in allowed[self._status]:
            raise InvalidStatusTransition(f'Transicion invalida de {self._status} -> {new_status}')
        
        self._status = new_status