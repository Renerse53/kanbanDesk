from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Task, BoardColumn, User, Project, Role
from ..schemas import TaskCreate, TaskUpdate, TaskOut
from ..auth import current_user

router = APIRouter(prefix="/api", tags=["tasks"])

def get_col(db: Session, column_id: int) -> BoardColumn:
    col = db.get(BoardColumn, column_id)
    if not col:
        raise HTTPException(404, "Column not found")
    return col

def can_access_column(col: BoardColumn, user: User) -> bool:
    project = col.board.project
    return user.role == Role.admin or user in project.members

@router.post("/columns/{column_id}/tasks", response_model=TaskOut, status_code=201)
def create_task(column_id: int, data: TaskCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    col = get_col(db, column_id)
    if not can_access_column(col, user):
        raise HTTPException(403, "No access to project")
    count = db.scalar(select(func.count(Task.id)).where(Task.column_id == column_id)) or 0
    if col.wip_limit is not None and count >= col.wip_limit:
        raise HTTPException(409, "WIP limit reached")
    task = Task(column_id=column_id, **data.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    if not can_access_column(task.column, user):
        raise HTTPException(403, "No access to project")
    values = data.model_dump(exclude_unset=True)
    if "column_id" in values and values["column_id"] != task.column_id:
        target = get_col(db, values["column_id"])
        if not can_access_column(target, user):
            raise HTTPException(403, "No access to target column")
        count = db.scalar(select(func.count(Task.id)).where(Task.column_id == target.id)) or 0
        if target.wip_limit is not None and count >= target.wip_limit:
            raise HTTPException(409, "WIP limit reached")
    for key, value in values.items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task

@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    if not can_access_column(task.column, user):
        raise HTTPException(403, "No access to project")
    db.delete(task)
    db.commit()

@router.get("/tasks/search", response_model=list[TaskOut])
def search_tasks(q: str = "", priority: str | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    tasks = db.scalars(select(Task).join(BoardColumn)).all()
    result = []
    for task in tasks:
        if not can_access_column(task.column, user):
            continue
        if q.lower() not in task.title.lower():
            continue
        if priority and task.priority.value != priority:
            continue
        result.append(task)
    return result
