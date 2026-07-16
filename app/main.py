from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app import storage
from app.business_rules import validate_status_transition
from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

app = FastAPI(title="Task Tracker API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict:
    """Return a liveness status payload for the API.

    Returns:
        dict: Contains "status" (always the literal "ok") and "timestamp"
            (current UTC time, ISO 8601 format).

    Example:
        GET /health
        -> 200 {"status": "ok", "timestamp": "2026-07-16T12:00:00+00:00"}
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    overdue: bool | None = None,
    tag: str | None = None,
) -> list[TaskResponse]:
    """List tasks, optionally filtered by status, priority, overdue state, and tag.

    Args:
        status (TaskStatus | None): Only return tasks with this status. No
            filter applied if None.
        priority (TaskPriority | None): Only return tasks with this priority.
            No filter applied if None.
        overdue (bool | None): Only return tasks whose computed is_overdue
            matches this value. No filter applied if None.
        tag (str | None): Only return tasks that have this tag. No filter
            applied if None.

    Returns:
        list[TaskResponse]: Matching tasks, or an empty list if none match.

    Raises:
        None directly. [VERIFY] FastAPI/Pydantic reject a status or priority
        value outside the respective enum with 422 before this function runs,
        based on the parameter type hints — not code in this function body.

    Example:
        GET /tasks?status=ToDo&tag=urgent
        -> 200 [TaskResponse, ...]
    """
    return storage.get_all_tasks(status=status, priority=priority, overdue=overdue, tag=tag)


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    """Retrieve a single task by ID.

    Args:
        task_id (str): ID of the task to retrieve.

    Returns:
        TaskResponse: The matching task.

    Raises:
        HTTPException: 404 if no task with the given ID exists.

    Example:
        GET /tasks/{task_id}
        -> 200 TaskResponse | 404 {"detail": "Task with id ... not found"}
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Apply a partial update to an existing task.

    If payload.status is set, validates the transition against the existing
    task's current status before applying any changes.

    Args:
        task_id (str): ID of the task to update.
        payload (TaskUpdate): Fields to update; unset fields are left
            unchanged.

    Returns:
        TaskResponse: The updated task.

    Raises:
        HTTPException: 404 if payload.status is set and no task with
            task_id exists (checked before transition validation).
        HTTPException: Raised by validate_status_transition (422) if the
            requested status change is not an allowed transition.
        HTTPException: 404 if the task does not exist at update time.
            [VERIFY] Whether this second check can trigger independently of
            the first, given the current single-request in-memory storage.

    Example:
        PATCH /tasks/{task_id} {"status": "InProgress"}
        -> 200 TaskResponse | 404 | 422
    """
    if payload.status is not None:
        existing = storage.get_task_by_id(task_id)
        if existing is None:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
        validate_status_transition(existing.status, payload.status)

    task = storage.update_task(task_id, payload)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: str) -> None:
    """Delete a task by ID.

    Args:
        task_id (str): ID of the task to delete.

    Returns:
        None.

    Raises:
        HTTPException: 404 if no task with the given ID exists.

    Example:
        DELETE /tasks/{task_id}
        -> 204 (no body) | 404
    """
    if not storage.delete_task(task_id):
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task.

    Args:
        payload (TaskCreate): Task fields for the new task.

    Returns:
        TaskResponse: The newly created task, including generated id and
            timestamps.

    Raises:
        None directly. [VERIFY] Invalid payload shape/values are rejected
        by FastAPI/Pydantic request validation (422) before this function
        runs — not code in this function body.

    Example:
        POST /tasks {"title": "Write docs"}
        -> 201 TaskResponse
    """
    return storage.add_task(payload)
