import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage import _storage

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def clear_storage():
    _storage.clear()
    yield

def test_create_task_success(client):
    response = client.post(
        "/tasks/",
        json={
            "title": "Тестовая задача",
            "description": "Описание",
            "status": "todo",
            "priority": 3
        },
        headers={"X-User-Id": "10"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Тестовая задача"
    assert data["description"] == "Описание"
    assert data["status"] == "todo"
    assert data["priority"] == 3
    assert data["owner_id"] == 10

def test_create_task_title_too_short(client):
    response = client.post(
        "/tasks/",
        json={
            "title": "ab",
            "description": "Описание",
            "status": "todo",
            "priority": 3
        },
        headers={"X-User-Id": "10"}
    )
    assert response.status_code == 422

def test_create_task_missing_user_id(client):
    response = client.post(
        "/tasks/",
        json={
            "title": "Задача",
            "description": "Описание",
            "status": "todo",
            "priority": 3
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "X-User-Id header missing"

def test_user_sees_only_own_tasks(client):
    client.post("/tasks/", json={"title": "Задача 10", "status": "todo", "priority": 2}, headers={"X-User-Id": "10"})
    client.post("/tasks/", json={"title": "Задача 20", "status": "todo", "priority": 2}, headers={"X-User-Id": "20"})

    response = client.get("/tasks/", headers={"X-User-Id": "10"})
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Задача 10"
    assert tasks[0]["owner_id"] == 10

def test_filter_tasks_by_status_and_min_priority(client):
    client.post("/tasks/", json={"title": "Task A", "status": "todo", "priority": 1}, headers={"X-User-Id": "10"})
    client.post("/tasks/", json={"title": "Task B", "status": "in_progress", "priority": 3}, headers={"X-User-Id": "10"})
    client.post("/tasks/", json={"title": "Task C", "status": "done", "priority": 5}, headers={"X-User-Id": "10"})

    response = client.get("/tasks/?status=in_progress", headers={"X-User-Id": "10"})
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["status"] == "in_progress"

    response = client.get("/tasks/?min_priority=4", headers={"X-User-Id": "10"})
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["priority"] == 5

    response = client.get("/tasks/?status=todo&min_priority=1", headers={"X-User-Id": "10"})
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["status"] == "todo"

def test_update_task_status_success(client):
    create_resp = client.post("/tasks/", json={"title": "Изменить статус", "status": "todo", "priority": 2}, headers={"X-User-Id": "10"})
    task_id = create_resp.json()["id"]

    patch_resp = client.patch(f"/tasks/{task_id}/status", json={"status": "done"}, headers={"X-User-Id": "10"})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "done"

    get_resp = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert get_resp.json()["status"] == "done"

def test_access_foreign_or_nonexistent_task_returns_404(client):
    create_resp = client.post("/tasks/", json={"title": "Чужая задача", "status": "todo", "priority": 2}, headers={"X-User-Id": "10"})
    task_id = create_resp.json()["id"]

    resp = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "20"})
    assert resp.status_code == 404

    resp = client.get("/tasks/9999", headers={"X-User-Id": "10"})
    assert resp.status_code == 404

def test_delete_task_success(client):
    create_resp = client.post("/tasks/", json={"title": "Удалить меня", "status": "todo", "priority": 2}, headers={"X-User-Id": "10"})
    task_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert get_resp.status_code == 404