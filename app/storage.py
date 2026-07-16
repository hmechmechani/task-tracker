from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.business_rules import is_task_overdue
from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

_tasks: dict[str, TaskResponse] = {}


def _hydrate_task(task: TaskResponse) -> TaskResponse:
    return task.model_copy(update={"is_overdue": is_task_overdue(task.due_date, task.status)})


def add_task(payload: TaskCreate) -> TaskResponse:
    """Create and persist a new task from validated input.

    Generates the task's id and created_at/updated_at timestamps.

    Args:
        payload (TaskCreate): Validated fields for the new task.

    Returns:
        TaskResponse: The stored task, with is_overdue computed at
            creation time.

    Raises:
        None.
    """
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
    """Return all stored tasks, optionally filtered.

    Each returned task has is_overdue freshly recomputed against the
    current date before filtering.

    Args:
        status (TaskStatus | None): Only include tasks with this status.
        priority (TaskPriority | None): Only include tasks with this
            priority.
        overdue (bool | None): Only include tasks whose recomputed
            is_overdue matches this value.
        tag (str | None): Only include tasks that have this tag.

    Returns:
        list[TaskResponse]: Matching tasks, or an empty list if none match.

    Raises:
        None.
    """
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
    """Look up a single task by ID.

    Args:
        task_id (str): ID of the task to look up.

    Returns:
        TaskResponse | None: The task with is_overdue freshly recomputed,
            or None if no task with that ID exists.

    Raises:
        None.
    """
    task = _tasks.get(task_id)
    if task is None:
        return None
    return _hydrate_task(task)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    """Apply a partial update to a stored task.

    Only fields explicitly set on payload are applied (exclude_unset).
    updated_at is refreshed and is_overdue is recomputed after the update.
    Status-transition validation happens in the caller (app/main.py), not
    in this function.

    Args:
        task_id (str): ID of the task to update.
        payload (TaskUpdate): Fields to update; unset fields are ignored.

    Returns:
        TaskResponse | None: The updated task, or the unchanged task
            (still hydrated) if payload had no fields set, or None if no
            task with task_id exists.

    Raises:
        None.
    """
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
    """Delete a task by ID if it exists.

    Args:
        task_id (str): ID of the task to delete.

    Returns:
        bool: True if a task was deleted, False if no task with that ID
            existed.

    Raises:
        None.
    """
    if task_id in _tasks:
        del _tasks[task_id]
        return True
    return False


def _reset() -> None:
    _tasks.clear()