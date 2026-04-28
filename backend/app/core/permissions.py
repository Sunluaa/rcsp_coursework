from fastapi import HTTPException, status

from app.models import Article, Attachment, NewsPost, Task, User


def role_name(user: User) -> str:
    return user.role.name


def is_admin(user: User) -> bool:
    return role_name(user) == "admin"


def is_editor(user: User) -> bool:
    return role_name(user) == "editor"


def is_employee(user: User) -> bool:
    return role_name(user) == "employee"


def ensure_admin_or_editor(user: User) -> None:
    if not (is_admin(user) or is_editor(user)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or editor role required")


def can_view_content(user: User, item: Article | NewsPost) -> bool:
    if is_admin(user):
        return True
    if item.status == "published":
        return True
    return is_editor(user) and item.author_id == user.id


def can_manage_content(user: User, item: Article | NewsPost) -> bool:
    if is_admin(user):
        return True
    return is_editor(user) and item.author_id == user.id


def ensure_can_view_content(user: User, item: Article | NewsPost) -> None:
    if not can_view_content(user, item):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")


def ensure_can_manage_content(user: User, item: Article | NewsPost) -> None:
    if not can_manage_content(user, item):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot manage this content")


def can_view_task(user: User, task: Task) -> bool:
    return is_admin(user) or is_editor(user) or task.assignee_id == user.id


def can_manage_task(user: User, task: Task) -> bool:
    return is_admin(user) or is_editor(user)


def ensure_can_view_task(user: User, task: Task) -> None:
    if not can_view_task(user, task):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


def can_download_attachment(user: User, attachment: Attachment) -> bool:
    if is_admin(user):
        return True
    item = attachment.article or attachment.news_post
    if item is None:
        return False
    if item.status == "published":
        return True
    return is_editor(user) and item.author_id == user.id


def ensure_can_download_attachment(user: User, attachment: Attachment) -> None:
    if not can_download_attachment(user, attachment):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")
