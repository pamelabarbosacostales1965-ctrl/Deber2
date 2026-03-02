from enum import Enum

class TaskStatus(str, Enum):
    TODO = 'todo'
    DOING = 'doing'
    DONE = 'done'