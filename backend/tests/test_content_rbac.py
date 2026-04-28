from tests.conftest import auth_headers, create_category, create_tag


def test_article_crud_and_employee_visibility(client):
    editor_headers = auth_headers(client, "editor")
    employee_headers = auth_headers(client, "employee")
    category_id = create_category(client, editor_headers)
    tag_id = create_tag(client, editor_headers)

    create_response = client.post(
        "/api/articles",
        headers=editor_headers,
        json={
            "title": "Draft security policy",
            "content": "Only editors and admins should see this draft.",
            "category_id": category_id,
            "tag_ids": [tag_id],
        },
    )
    assert create_response.status_code == 201, create_response.text
    article_id = create_response.json()["id"]

    employee_list = client.get("/api/articles", headers=employee_headers)
    assert employee_list.status_code == 200
    assert employee_list.json() == []

    published = client.post(f"/api/articles/{article_id}/publish", headers=editor_headers)
    assert published.status_code == 200
    assert published.json()["status"] == "published"

    employee_list = client.get("/api/articles", headers=employee_headers)
    assert len(employee_list.json()) == 1

    update_response = client.patch(
        f"/api/articles/{article_id}",
        headers=editor_headers,
        json={"title": "Published security policy"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Published security policy"


def test_editor_cannot_update_another_editors_draft(client):
    admin_headers = auth_headers(client, "admin")
    editor_headers = auth_headers(client, "editor")
    second_editor = client.post(
        "/api/users",
        headers=admin_headers,
        json={
            "email": "editor2@example.com",
            "password": "Editor12345!",
            "full_name": "Second Editor",
            "role_name": "editor",
        },
    )
    assert second_editor.status_code == 201, second_editor.text
    token = client.post(
        "/api/auth/login", json={"email": "editor2@example.com", "password": "Editor12345!"}
    ).json()["access_token"]
    second_headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/articles",
        headers=editor_headers,
        json={"title": "Private draft", "content": "Draft content"},
    )
    assert response.status_code == 201
    article_id = response.json()["id"]

    forbidden = client.patch(
        f"/api/articles/{article_id}", headers=second_headers, json={"title": "Hijacked"}
    )
    assert forbidden.status_code == 403


def test_news_crud_and_employee_visibility(client):
    editor_headers = auth_headers(client, "editor")
    employee_headers = auth_headers(client, "employee")

    create_response = client.post(
        "/api/news",
        headers=editor_headers,
        json={"title": "Internal launch", "content": "Launch news draft"},
    )
    assert create_response.status_code == 201
    news_id = create_response.json()["id"]
    assert client.get("/api/news", headers=employee_headers).json() == []

    publish_response = client.post(f"/api/news/{news_id}/publish", headers=editor_headers)
    assert publish_response.status_code == 200

    employee_news = client.get("/api/news", headers=employee_headers)
    assert len(employee_news.json()) == 1

    patch_response = client.patch(
        f"/api/news/{news_id}", headers=editor_headers, json={"content": "Updated launch news"}
    )
    assert patch_response.status_code == 200

    delete_response = client.delete(f"/api/news/{news_id}", headers=editor_headers)
    assert delete_response.status_code == 204


def test_search_respects_published_visibility(client):
    editor_headers = auth_headers(client, "editor")
    employee_headers = auth_headers(client, "employee")
    client.post(
        "/api/articles",
        headers=editor_headers,
        json={"title": "Hidden runbook", "content": "secret-search-token"},
    )
    visible = client.post(
        "/api/articles",
        headers=editor_headers,
        json={"title": "Visible runbook", "content": "public-search-token", "status": "published"},
    )
    assert visible.status_code == 201

    search_response = client.get("/api/search?query=search-token", headers=employee_headers)
    assert search_response.status_code == 200
    titles = {item["title"] for item in search_response.json()["items"]}
    assert titles == {"Visible runbook"}
