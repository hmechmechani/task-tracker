from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.business_rules import is_task_overdue
from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

_tasks: dict[str, TaskResponse] = {}


def _hydrate_task(task: TaskResponse) -> TaskResponse:
    return task.model_copy(update={"is_overdue": is_task_overdue(task.due_date, task.status)})


def add_task(payload: TaskCreate) -> TaskResponse:
    task_id = str(uuid4())
    now = datetime.now(timezone.utc)
    task = TaskResponse(
        id=task_id,
        title=payload.title,
        description=payload.description or "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        due_date=payload.due_date,
        tags=payload.tags,
        is_overdue=is_task_overdue(payload.due_date, payload.status),
        created_at=now,
        updated_at=now,
    )
    _tasks[task_id] = task
    return task


def get_all_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    overdue: Optional[bool] = None,
    tag: Optional[str] = None,
) -> list[TaskResponse]:
    tasks = [_hydrate_task(task) for task in _tasks.values()]
    if status is not None:
        tasks = [task for task in tasks if task.status == status]
    if priority is not None:
        tasks = [task for task in tasks if task.priority == priority]
    if overdue is not None:
        tasks = [task for task in tasks if task.is_overdue is overdue]
    if tag is not None:
        tasks = [task for task in tasks if tag in task.tags]
    return tasks


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    task = _tasks.get(task_id)
    if task is None:
        return None
    return _hydrate_task(task)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    task = _tasks.get(task_id)
    if task is None:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        return _hydrate_task(task)



    updated_task = task.model_copy(update={**update_data, "updated_at": datetime.now(timezone.utc)})
    _tasks[task_id] = updated_task
    return _hydrate_task(updated_task)


def delete_task(task_id: str) -> bool:
    if task_id in _tasks:
        del _tasks[task_id]
        return True
    return False


def _reset() -> None:
    _tasks.clear()