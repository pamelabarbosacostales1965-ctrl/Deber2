from datetime import date
from app.domain.entities import Task
from app.domain.enums import TaskStatus
from app.domain.priority import BugPriority, FeaturePriority, ChorePriority
from app.repositories.base import TaskRepository, ProjectRepository

class TaskService:
    def __init__(self, projects: ProjectRepository, tasks: TaskRepository) -> None:
        self.projects = projects
        self.tasks = tasks

    def create_task(self, project_id: str, title: str, task_type: str, due_date: date | None) -> Task:
        self.projects.get(project_id)

        strategy = {
            'bug': BugPriority(),
            'feature': FeaturePriority(),
            'chore': ChorePriority()
        }.get(task_type)

        if strategy is None:
            raise ValueError('task_type invalida. Usar: bug, feature, chore')
        
        task = Task(
            title=title,
            project_id=project_id,
            strategy=strategy,
            due_date=due_date
        )

        self.tasks.add(task)

        return task

    def list_tasks(self, project_id: str) -> list[Task]:
        self.projects.get(project_id)

        return self.tasks.list_by_project(project_id)
    
    def update_task(self, task_id: str, title: str | None, due_date: date | None, status: TaskStatus | None) -> Task:

        task = self.tasks.get(task_id)

        if title is not None:
            task.update_title(title)
        
        task.update_due_date(due_date)

        if status is not None:
            task.transtition_to(status)
        
        return task

    def delete_task(self, task_id: str) -> None:
        self.tasks.delete(task_id)
    
    def get_task(self, task_id: str) -> Task:
        return self.tasks.get(task_id)
        