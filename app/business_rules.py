from datetime import date

from fastapi import HTTPException, status

from app.models import TaskStatus

VALID_TRANSITIONS: frozenset[tuple[TaskStatus, TaskStatus]] = frozenset({
    (TaskStatus.TODO, TaskStatus.IN_PROGRESS),
    (TaskStatus.IN_PROGRESS, TaskStatus.DONE),
    (TaskStatus.DONE, TaskStatus.IN_PROGRESS),
})


def validate_status_transition(current: TaskStatus, new: TaskStatus) -> None:
    """Validate that a task status transition is allowed.

    Args:
        current (TaskStatus): The task's current status.
        new (TaskStatus): The status being transitioned to.

    Returns:
        None. Returns silently if the transition is allowed.

    Raises:
        HTTPException: 422 if (current, new) is not in VALID_TRANSITIONS,
            with a detail message listing the allowed transitions.
    """
    if (current, new) not in VALID_TRANSITIONS:
        allowed = sorted({f"{f.value}->{t.value}" for f, t in VALID_TRANSITIONS})
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid status transition from {current.value} to {new.value}. Allowed transitions: {allowed}",
        )


def is_task_overdue(due_date: date | None, status: TaskStatus, today: date | None = None) -> bool:
    """Determine whether a task is overdue.

    Args:
        due_date (date | None): The task's due date, or None if unset.
        status (TaskStatus): The task's current status.
        today (date | None): The date to compare due_date against. Defaults
            to date.today() when not provided; overridable for testing.

    Returns:
        bool: True if due_date is before today and status is not Done.
            False if due_date is None, due_date is today or later, or
            status is Done.

    Raises:
        None.
    """
    if due_date is None:
        return False
    current_date = today if today is not None else date.today()
    return due_date < current_date and status != TaskStatus.DONE
