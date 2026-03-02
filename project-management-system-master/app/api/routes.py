from fastapi import APIRouter, Depends, HTTPException

from app.domain.exceptions import DomainError, NotFoundError, InvalidStatusTransition, ValidationError
from app.repositories.memory import InMemoryProjectRepo, InMemoryTaskRepo
from app.services.project_service import ProjectService
from app.services.task_service import TaskService
from app.schemas.dto import ProjectCreate, ProjectOut, TaskCreate, TaskOut, TaskUpdate

router = APIRouter()

project_repo = InMemoryProjectRepo()
task_repo = InMemoryTaskRepo()

def get_project_service() -> ProjectService:
    return ProjectService(project_repo)

def get_task_service() -> TaskService:
    return TaskService(project_repo, task_repo)

def to_http(e: Exception) -> HTTPException:
    if isinstance(e, NotFoundError):
        return HTTPException(status_code = 404, detail=str(e))
    if isinstance(e, InvalidStatusTransition, ValidationError, ValueError):
        return HTTPException(status_code = 400, detail=str(e))
    if isinstance(e, DomainError):
        return HTTPException(status_code=500, detail='Internal Server Error')

@router.post('/projects',response_model = ProjectOut ,status_code = 201)
def create_project(body: ProjectCreate, service: ProjectService = Depends(get_project_service)):
    try:
        project = service.create(body.name)
        return ProjectOut(id = project.id, name = project.name)
    except Exception as e:
        raise to_http(e)
    
# TO-DO: GET /projects
@router.get('/projects', response_model=list[ProjectOut])
def get_projects(service: ProjectService = Depends(get_project_service)):
    try:
        projects = service.list()
        return [ProjectOut(id=project.id, name=project.name) for project in projects]
    except Exception as e:
        raise to_http(e)    
    

# TO-DO: GET /projects/{project_id}
@router.get('/projects/{project_id}', response_model=ProjectOut)
def get_project(project_id: str, service: ProjectService = Depends(get_project_service)):
    try:
        project = service.get(project_id)
        return ProjectOut(id=project.id, name=project.name)
    except Exception as e:
        raise to_http(e)


# @router.get('/projects/{project_id}', response_model=ProjectOut)
@router.delete('/projects/{project_id}', status_code=204)
def delete_project(project_id: str, service: ProjectService = Depends(get_project_service)):
    try:
        service.delete(project_id)
    except Exception as e:
        raise to_http(e)
    

# TO-DO POST /projects/{project_id}/tasks
@router.post('/projects/{project_id}/tasks', response_model=TaskOut, status_code = 201)
def create_task(project_id: str, body: TaskCreate, service: TaskService = Depends(get_task_service)):
    try: 
        task = service.create(project_id = project_id, title = body.title)
        return TaskOut(id = task.id, project_id = task.project_id, title= task.title, status = task.status)
    except Exception as e:
        raise to_http(e)
    
# TO-DO GET /projects/{project_id}/tasks
@router.get('/projects/{project_id}/tasks', response_model = list [TaskOut])
def get_project_tasks(project_id: str, service: TaskService = Depends(get_task_service)):
    try:
        tasks = service.list_by_project(project_id)
        return [TaskOut(id=task.id, project_id=task.project_id, title=task.title, status=task.status) for task in tasks]
    except Exception as e:
        raise to_http(e)

# TO-DO DELETE /tasks/{task_id}
@router.delete('/tasks/{task_id}', status_code=204)
def delete_task(task_id: str, service: TaskService = Depends(get_task_service)):
    try:
        service.delete(task_id)
        return None
    except Exception as e:
        raise to_http(e)