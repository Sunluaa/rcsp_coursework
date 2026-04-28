from tests.conftest import auth_headers


def test_task_crud_and_employee_status_update(client):
    editor_headers = auth_headers(client, "editor")
    employee_headers = auth_headers(client, "employee")

    users_response = client.get("/api/users", headers=auth_headers(client, "admin"))
    employee_id = next(user["id"] for user in users_response.json() if user["role"]["name"] == "employee")

    create_response = client.post(
        "/api/tasks",
        headers=editor_headers,
        json={
            "title": "Read article",
            "description": "Please read the new article",
            "assignee_id": employee_id,
            "priority": "high",
        },
    )
    assert create_response.status_code == 201, create_response.text
    task_id = create_response.json()["id"]

    employee_tasks = client.get("/api/tasks", headers=employee_headers)
    assert len(employee_tasks.json()) == 1

    status_update = client.patch(
        f"/api/tasks/{task_id}", headers=employee_headers, json={"status": "in_progress"}
    )
    assert status_update.status_code == 200
    assert status_update.json()["status"] == "in_progress"

    forbidden = client.patch(
        f"/api/tasks/{task_id}", headers=employee_headers, json={"title": "Changed by employee"}
    )
    assert forbidden.status_code == 403

    editor_update = client.patch(
        f"/api/tasks/{task_id}", headers=editor_headers, json={"status": "done", "priority": "medium"}
    )
    assert editor_update.status_code == 200

    delete_response = client.delete(f"/api/tasks/{task_id}", headers=editor_headers)
    assert delete_response.status_code == 204


def test_attachment_upload_download_and_validation(client):
    editor_headers = auth_headers(client, "editor")
    employee_headers = auth_headers(client, "employee")
    article = client.post(
        "/api/articles",
        headers=editor_headers,
        json={"title": "Public article with file", "content": "content", "status": "published"},
    )
    assert article.status_code == 201
    article_id = article.json()["id"]

    upload = client.post(
        f"/api/attachments/articles/{article_id}",
        headers=editor_headers,
        files={"file": ("guide.pdf", b"%PDF-1.4 test", "application/pdf")},
    )
    assert upload.status_code == 201, upload.text
    attachment_id = upload.json()["id"]

    download = client.get(f"/api/attachments/{attachment_id}/download", headers=employee_headers)
    assert download.status_code == 200
    assert download.content == b"%PDF-1.4 test"

    invalid_type = client.post(
        f"/api/attachments/articles/{article_id}",
        headers=editor_headers,
        files={"file": ("image.png", b"png", "image/png")},
    )
    assert invalid_type.status_code == 400

    too_large = client.post(
        f"/api/attachments/articles/{article_id}",
        headers=editor_headers,
        files={"file": ("large.pdf", b"x" * 1025, "application/pdf")},
    )
    assert too_large.status_code == 400
