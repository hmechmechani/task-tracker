from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _validate_tags(value: object) -> object:
    if value is None:
        return value
    if not isinstance(value, list):
        raise TypeError("tags must be a list of strings")
    if len(value) > 5:
        raise ValueError("tags must contain at most 5 tags")

    cleaned_tags = []
    for tag in value:
        if not isinstance(tag, str):
            raise TypeError("tags must be a list of strings")

        cleaned_tag = tag.strip()
        if not cleaned_tag:
            raise ValueError("tags cannot contain blank values")
        if len(cleaned_tag) > 30:
            raise ValueError("tags must be 30 characters or fewer")
        cleaned_tags.append(cleaned_tag)

    return cleaned_tags


class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    due_date: Optional[date] = None
    tags: list[str] = Field(default_factory=list)

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, value: object) -> object:
        if value is None:
            return value
        if not isinstance(value, str):
            raise TypeError("title must be a string")

        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("title cannot be blank")
        if len(cleaned_value) > 200:
            raise ValueError("title must be 200 characters or fewer")
        return cleaned_value

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, value: object) -> object:
        return _validate_tags(value)


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None
    due_date: Optional[date] = None
    tags: Optional[list[str]] = None

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, value: object) -> object:
        if value is None:
            return value
        if not isinstance(value, str):
            raise TypeError("title must be a string")

        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("title cannot be blank")
        if len(cleaned_value) > 200:
            raise ValueError("title must be 200 characters or fewer")
        return cleaned_value

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, value: object) -> object:
        return _validate_tags(value)


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str]
    due_date: Optional[date] = None
    tags: list[str] = Field(default_factory=list)
    is_overdue: bool = False
    created_at: datetime
    updated_at: datetime