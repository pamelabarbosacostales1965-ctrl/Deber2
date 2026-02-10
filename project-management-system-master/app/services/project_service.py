from app.domain.entities import Project
from app.repositories.base import ProjectRepository

class ProjectService:
    def __init__(self, repo: ProjectRepository) -> None:
        self.repo = repo
    
    def create(self, name: str) -> Project:
        project = Project(name=name)
        self.repo.add(project)
        return project

    def get(self, project_id: str) -> Project:
        return self.repo.get(project_id)

    def list(self) -> list[Project]:
        return self.repo.list()