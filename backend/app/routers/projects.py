from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from ..database import get_db
from ..models import Project, Board, BoardColumn, User, Role
from ..schemas import ProjectCreate, ProjectUpdate, ProjectOut, BoardUpdate, BoardOut, ColumnCreate, ColumnUpdate
from ..auth import current_user, require_roles

router = APIRouter(prefix="/api", tags=["projects"])


def get_project_or_404(project_id: int, db: Session) -> Project:
    project = db.scalar(select(Project).where(Project.id == project_id))
    if not project:
        raise HTTPException(404, "Project not found")
    return project


def can_access(project: Project, user: User) -> bool:
    return user.role == Role.admin or user in project.members


def load_board(project_id: int, db: Session) -> Board:
    project = db.scalar(
        select(Project)
        .options(
            selectinload(Project.board)
            .selectinload(Board.columns)
            .selectinload(BoardColumn.tasks)
        )
        .where(Project.id == project_id)
    )
    if not project or not project.board:
        raise HTTPException(404, "Board not found")
    return project.board


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), user: User = Depends(current_user)):
    if user.role == Role.admin:
        return db.scalars(select(Project).order_by(Project.id.desc())).all()
    return user.projects


@router.post("/projects", response_model=ProjectOut, status_code=201)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.admin, Role.manager)),
):
    project = Project(name=data.name, description=data.description, members=[user])
    project.board = Board(
        name=f"{data.name} — Kanban",
        columns=[
            BoardColumn(name="To Do", position=0),
            BoardColumn(name="In Progress", position=1),
            BoardColumn(name="Done", position=2),
        ],
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.patch("/projects/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.admin, Role.manager)),
):
    project = get_project_or_404(project_id, db)
    if not can_access(project, user):
        raise HTTPException(403, "No access to project")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/projects/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.admin, Role.manager)),
):
    project = get_project_or_404(project_id, db)
    if user.role != Role.admin and user not in project.members:
        raise HTTPException(403, "No access to project")
    db.delete(project)
    db.commit()


@router.get("/projects/{project_id}/board", response_model=BoardOut)
def get_board(project_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    project = get_project_or_404(project_id, db)
    if not can_access(project, user):
        raise HTTPException(403, "No access to project")
    return load_board(project_id, db)


@router.patch("/boards/{board_id}", response_model=BoardOut)
def update_board(
    board_id: int,
    data: BoardUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.admin, Role.manager)),
):
    board = db.get(Board, board_id)
    if not board:
        raise HTTPException(404, "Board not found")
    project = get_project_or_404(board.project_id, db)
    if not can_access(project, user):
        raise HTTPException(403, "No access to project")
    board.name = data.name
    db.commit()
    return load_board(project.id, db)


@router.post("/boards/{board_id}/columns", response_model=BoardOut)
def add_column(
    board_id: int,
    data: ColumnCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.admin, Role.manager)),
):
    board = db.get(Board, board_id)
    if not board:
        raise HTTPException(404, "Board not found")
    project = get_project_or_404(board.project_id, db)
    if not can_access(project, user):
        raise HTTPException(403, "No access to project")
    col = BoardColumn(board_id=board_id, **data.model_dump())
    db.add(col)
    db.commit()
    return load_board(project.id, db)


@router.patch("/columns/{column_id}", response_model=BoardOut)
def update_column(
    column_id: int,
    data: ColumnUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.admin, Role.manager)),
):
    col = db.get(BoardColumn, column_id)
    if not col:
        raise HTTPException(404, "Column not found")
    project = get_project_or_404(col.board.project_id, db)
    if not can_access(project, user):
        raise HTTPException(403, "No access to project")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(col, key, value)
    db.commit()
    return load_board(project.id, db)


@router.delete("/columns/{column_id}", status_code=204)
def delete_column(
    column_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.admin, Role.manager)),
):
    col = db.get(BoardColumn, column_id)
    if not col:
        raise HTTPException(404, "Column not found")
    project = get_project_or_404(col.board.project_id, db)
    if not can_access(project, user):
        raise HTTPException(403, "No access to project")
    if len(col.board.columns) <= 1:
        raise HTTPException(400, "Board must contain at least one column")
    db.delete(col)
    db.commit()
