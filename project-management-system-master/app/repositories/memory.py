from __future__ import annotations
from app.domain.entities import Project, Task
from app.domain.exceptions import NotFoundError

class InMemoryProjectRepo:

    def __init__(self) -> None:
        self._data: dict[str, Project] = {}
    
    def add(self, project: Project) -> None:
        self._data[project.id] = project
    
    def get(self, project_id: str) -> Project:
        if project_id not in self._data:
            raise NotFoundError('Proyecto no encontrado!')
        
        return self._data[project_id]
    
    def list(self) -> list[Project]:
        return list(self._data.values())

class InMemoryTaskRepo:

    def __init__(self) -> None:
        self._data: dict[str, Task] = {}
    
    def add(self, task: Task) -> None:
        self._data[task.id] = task
    
    def get(self, task_id: str) -> Task:
        if task_id not in self._data:
            raise NotFoundError('Tarea no encontrada!')

        return self._data[task_id]

    def delete(self, task_id: str) -> None:
        if task_id not in self._data:
            raise NotFoundError('Tarea no encontrada!')

        del self._data[task_id]
    
    def list_by_project(self, project_id: str) -> list[Task]:
        return [task for task in self._data.values() if task.project_id == project_id]