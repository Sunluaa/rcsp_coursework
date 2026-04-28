from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from tests.conftest import auth_headers


FUZZ_SETTINGS = settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])


@FUZZ_SETTINGS
@given(email=st.text(min_size=0, max_size=80), password=st.text(min_size=0, max_size=140))
def test_user_create_fuzz_never_returns_500(client, email, password):
    headers = auth_headers(client, "admin")
    response = client.post(
        "/api/users",
        headers=headers,
        json={
            "email": email,
            "password": password,
            "full_name": "Fuzz User",
            "role_name": "employee",
        },
    )

    assert response.status_code < 500


@FUZZ_SETTINGS
@given(title=st.text(min_size=0, max_size=260), content=st.text(min_size=0, max_size=500))
def test_article_random_title_content_never_returns_500(client, title, content):
    headers = auth_headers(client, "editor")
    response = client.post(
        "/api/articles",
        headers=headers,
        json={"title": title, "content": content, "status": "draft"},
    )

    assert response.status_code < 500


@FUZZ_SETTINGS
@given(status_value=st.text(min_size=1, max_size=30))
def test_invalid_article_status_returns_4xx(client, status_value):
    assume(status_value not in {"draft", "published", "archived"})
    headers = auth_headers(client, "editor")
    response = client.post(
        "/api/articles",
        headers=headers,
        json={"title": "Fuzz status article", "content": "content", "status": status_value},
    )

    assert 400 <= response.status_code < 500


@FUZZ_SETTINGS
@given(status_value=st.text(min_size=1, max_size=30))
def test_invalid_news_status_returns_4xx(client, status_value):
    assume(status_value not in {"draft", "published", "archived"})
    headers = auth_headers(client, "editor")
    response = client.post(
        "/api/news",
        headers=headers,
        json={"title": "Fuzz status news", "content": "content", "status": status_value},
    )

    assert 400 <= response.status_code < 500


@FUZZ_SETTINGS
@given(status_value=st.text(min_size=1, max_size=30))
def test_invalid_task_status_returns_4xx(client, status_value):
    assume(status_value not in {"todo", "in_progress", "done", "cancelled"})
    headers = auth_headers(client, "editor")
    users_response = client.get("/api/users", headers=auth_headers(client, "admin"))
    employee_id = next(user["id"] for user in users_response.json() if user["role"]["name"] == "employee")
    response = client.post(
        "/api/tasks",
        headers=headers,
        json={"title": "Fuzz task", "assignee_id": employee_id, "status": status_value},
    )

    assert 400 <= response.status_code < 500


@FUZZ_SETTINGS
@given(priority=st.text(min_size=1, max_size=30))
def test_invalid_task_priority_returns_4xx(client, priority):
    assume(priority not in {"low", "medium", "high"})
    headers = auth_headers(client, "editor")
    users_response = client.get("/api/users", headers=auth_headers(client, "admin"))
    employee_id = next(user["id"] for user in users_response.json() if user["role"]["name"] == "employee")
    response = client.post(
        "/api/tasks",
        headers=headers,
        json={"title": "Fuzz task priority", "assignee_id": employee_id, "priority": priority},
    )

    assert 400 <= response.status_code < 500
