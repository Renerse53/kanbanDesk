from datetime import datetime, date
from sqlalchemy import String, Text, ForeignKey, DateTime, Date, Integer, Enum as SAEnum, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base
import enum

class Role(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    developer = "developer"

class Priority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

project_members = Table(
    "project_members", Base.metadata,
    Column("project_id", ForeignKey("projects.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(SAEnum(Role), default=Role.developer)
    projects: Mapped[list["Project"]] = relationship(secondary=project_members, back_populates="members")

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    members: Mapped[list[User]] = relationship(secondary=project_members, back_populates="projects")
    board: Mapped["Board"] = relationship(back_populates="project", uselist=False, cascade="all, delete-orphan")

class Board(Base):
    __tablename__ = "boards"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), default="Kanban Board")
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), unique=True)
    project: Mapped[Project] = relationship(back_populates="board")
    columns: Mapped[list["BoardColumn"]] = relationship(back_populates="board", cascade="all, delete-orphan", order_by="BoardColumn.position")

class BoardColumn(Base):
    __tablename__ = "board_columns"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    position: Mapped[int] = mapped_column(Integer, default=0)
    wip_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    board_id: Mapped[int] = mapped_column(ForeignKey("boards.id"))
    board: Mapped[Board] = relationship(back_populates="columns")
    tasks: Mapped[list["Task"]] = relationship(back_populates="column", cascade="all, delete-orphan", order_by="Task.position")

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    priority: Mapped[Priority] = mapped_column(SAEnum(Priority), default=Priority.medium)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    position: Mapped[int] = mapped_column(Integer, default=0)
    column_id: Mapped[int] = mapped_column(ForeignKey("board_columns.id"))
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    column: Mapped[BoardColumn] = relationship(back_populates="tasks")
    assignee: Mapped[User | None] = relationship()
