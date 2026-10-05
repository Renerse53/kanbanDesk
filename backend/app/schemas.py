from datetime import date
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from .models import Role, Priority

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    role: Role = Role.developer

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    role: Role

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str = ""

class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None

class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str

class BoardUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=150)

class ColumnCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    position: int = 0
    wip_limit: int | None = Field(default=None, ge=1)

class ColumnUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    position: int | None = None
    wip_limit: int | None = Field(default=None, ge=1)

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    priority: Priority = Priority.medium
    due_date: date | None = None
    assignee_id: int | None = None
    position: int = 0

class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    priority: Priority | None = None
    due_date: date | None = None
    assignee_id: int | None = None
    column_id: int | None = None
    position: int | None = None

class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    priority: Priority
    due_date: date | None
    position: int
    column_id: int
    assignee_id: int | None

class ColumnOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    position: int
    wip_limit: int | None
    tasks: list[TaskOut]

class BoardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    project_id: int
    columns: list[ColumnOut]
