from datetime import date

from app.business_rules import is_task_overdue
from app.models import TaskStatus


def test_create_task_valid_returns_201_with_full_body(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Full task",
            "description": "A description",
            "status": "ToDo",
            "priority": "High",
            "assignee": "Alice",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Full task"
    assert body["description"] == "A description"
    assert body["status"] == "ToDo"
    assert body["priority"] == "High"
    assert body["assignee"] == "Alice"
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_is_task_overdue_recomputes_based_on_current_date():
    due_date = date(2020, 1, 1)

    assert is_task_overdue(due_date, TaskStatus.TODO, today=date(2019, 12, 31)) is False
    assert is_task_overdue(due_date, TaskStatus.TODO, today=date(2020, 1, 2)) is True


def test_create_task_invalid_due_date_returns_422(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Bad due date",
            "due_date": "not-a-date",
        },
    )

    assert response.status_code == 422


def test_create_task_missing_title_returns_422(client):
    response = client.post("/tasks", json={"description": "no title"})

    assert response.status_code == 422


def test_create_task_blank_title_returns_422(client):
    response = client.post("/tasks", json={"title": "   "})

    assert response.status_code == 422


def test_create_task_invalid_priority_returns_422(client):
    response = client.post("/tasks", json={"title": "Valid title", "priority": "Urgent"})

    assert response.status_code == 422


def test_create_task_unknown_field_returns_422(client):
    response = client.post("/tasks", json={"title": "Valid title", "unknown": "field"})

    assert response.status_code == 422


def test_create_task_with_tags_returns_201_and_trims_tags(client):
    response = client.post(
        "/tasks",
        json={"title": "Tagged task", "tags": ["  urgent ", "review", " urgent "]},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["tags"] == ["urgent", "review", "urgent"]


def test_create_task_with_empty_tag_returns_422(client):
    response = client.post("/tasks", json={"title": "Bad tag task", "tags": ["alpha", "   "]})

    assert response.status_code == 422


def test_create_task_non_string_title_returns_422(client):
    response = client.post("/tasks", json={"title": 123, "tags": ["ok"]})

    assert response.status_code == 422


def test_create_task_non_list_tags_returns_422(client):
    response = client.post("/tasks", json={"title": "test", "tags": "urgent"})

    assert response.status_code == 422


def test_list_tasks_filter_by_tag_returns_only_matches(client):
    client.post("/tasks", json={"title": "Urgent task", "tags": ["urgent"]})
    client.post("/tasks", json={"title": "Also urgent", "tags": ["review", "urgent"]})
    client.post("/tasks", json={"title": "Review task", "tags": ["review"]})

    response = client.get("/tasks", params={"tag": "urgent"})

    assert response.status_code == 200
    body = response.json()
    assert [task["title"] for task in body] == ["Urgent task", "Also urgent"]


def test_list_tasks_empty_returns_200_and_empty_list(client):
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(client, created_task):
    response = client.get("/tasks", params={"status": "Done"})

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client):
    client.post("/tasks", json={"title": "Low task", "priority": "Low"})
    client.post("/tasks", json={"title": "High task", "priority": "High"})
    client.post("/tasks", json={"title": "Another high", "priority": "High"})

    response = client.get("/tasks", params={"priority": "High"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert all(task["priority"] == "High" for task in body)


def test_get_task_by_id_returns_task(client, created_task):
    response = client.get(f"/tasks/{created_task['id']}")

    assert response.status_code == 200
    assert response.json() == created_task


def test_get_task_by_id_not_found_returns_404_with_detail(client):
    missing_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/tasks/{missing_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == f"Task with id {missing_id} not found"


def test_patch_partial_update_keeps_other_fields(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"title": "updated title"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "updated title"
    assert body["description"] == created_task["description"]
    assert body["status"] == created_task["status"]
    assert body["priority"] == created_task["priority"]
    assert body["assignee"] == created_task["assignee"]
    assert body["id"] == created_task["id"]


def test_patch_title_null_returns_422(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"title": None},
    )

    assert response.status_code == 422


def test_patch_not_found_returns_404(client):
    missing_id = "00000000-0000-0000-0000-000000000000"
    response = client.patch(f"/tasks/{missing_id}", json={"title": "nope"})

    assert response.status_code == 404
    assert response.json()["detail"] == f"Task with id {missing_id} not found"


def test_patch_valid_transition_todo_to_inprogress_returns_200(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"status": "InProgress"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "InProgress"


def test_patch_invalid_transition_todo_to_done_returns_422(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"status": "Done"},
    )

    assert response.status_code == 422


def test_patch_same_status_returns_422(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"status": "ToDo"},
    )

    assert response.status_code == 422


def test_patch_update_due_date_recomputes_is_overdue(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"due_date": "2099-01-01"},
    )

    assert response.status_code == 200
    assert response.json()["due_date"] == "2099-01-01"
    assert response.json()["is_overdue"] is False

    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"due_date": "2000-01-01"},
    )

    assert response.status_code == 200
    assert response.json()["due_date"] == "2000-01-01"
    assert response.json()["is_overdue"] is True


def test_patch_update_tags_returns_200(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"tags": ["urgent", "review"]},
    )

    assert response.status_code == 200
    assert response.json()["tags"] == ["urgent", "review"]


def test_patch_unrelated_field_preserves_tags(client):
    created = client.post(
        "/tasks",
        json={"title": "Tagged task", "tags": ["urgent", "review"]},
    )

    response = client.patch(
        f"/tasks/{created.json()['id']}",
        json={"title": "Updated title"},
    )

    assert response.status_code == 200
    assert response.json()["tags"] == ["urgent", "review"]


def test_create_task_with_due_date_returns_201_and_computes_overdue(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Due soon",
            "status": "ToDo",
            "due_date": "2020-01-01",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["due_date"] == "2020-01-01"
    assert body["is_overdue"] is True


def test_list_tasks_overdue_filter_returns_only_overdue_tasks(client):
    client.post(
        "/tasks",
        json={
            "title": "Overdue task",
            "status": "ToDo",
            "due_date": "2020-01-01",
        },
    )
    client.post(
        "/tasks",
        json={
            "title": "Not overdue task",
            "status": "ToDo",
            "due_date": "2099-01-01",
        },
    )

    response = client.get("/tasks", params={"overdue": True})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Overdue task"


def test_delete_existing_returns_204_no_body(client, created_task):
    response = client.delete(f"/tasks/{created_task['id']}")

    assert response.status_code == 204
    assert response.content == b""


def test_delete_missing_returns_404(client):
    missing_id = "00000000-0000-0000-0000-000000000000"
    response = client.delete(f"/tasks/{missing_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == f"Task with id {missing_id} not found"

def test_patch_invalid_transition_inprogress_to_todo_returns_422(client):
    created_task = client.post(
        "/tasks",
        json={
            "title": "In progress task",
            "description": "A task that should not move backwards",
            "status": "InProgress",
            "priority": "Medium",
            "assignee": "Bob",
        },
    )
    response = client.patch(
        f"/tasks/{created_task.json()['id']}",
        json={"status": "ToDo"},
    )
    assert response.status_code == 422
    assert "Invalid status transition" in response.json()["detail"]

def test_patch_description_null_returns_422(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"description": None},
    )

    assert response.status_code == 422


def test_patch_priority_null_returns_422(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"priority": None},
    )

    assert response.status_code == 422


def test_patch_status_null_returns_422_and_does_not_corrupt_task(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"status": None},
    )
    assert response.status_code == 422

    # A rejected update must not leave the stored task corrupted in a way
    # that breaks a later request.
    follow_up = client.get(f"/tasks/{created_task['id']}")
    assert follow_up.status_code == 200
    assert follow_up.json()["status"] == created_task["status"]


def test_patch_tags_null_returns_422_and_does_not_corrupt_task(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"tags": None},
    )
    assert response.status_code == 422

    follow_up = client.get(f"/tasks/{created_task['id']}")
    assert follow_up.status_code == 200
    assert follow_up.json()["tags"] == created_task["tags"]