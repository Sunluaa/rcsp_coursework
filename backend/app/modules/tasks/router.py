from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.core.permissions import can_manage_task, ensure_can_view_task, is_admin, is_editor
from app.models import Article, NewsPost, Task, User
from app.modules.tasks.schemas import TaskCreate, TaskResponse, TaskUpdate


router = APIRouter(prefix="/tasks", tags=["tasks"])


def _task_options():
    return (
        joinedload(Task.creator).joinedload(User.role),
        joinedload(Task.assignee).joinedload(User.role),
    )


def _get_task_or_404(db: Session, task_id: int) -> Task:
    task = db.execute(select(Task).options(*_task_options()).where(Task.id == task_id)).scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


def _get_assignee(db: Session, assignee_id: int, current_user: User) -> User:
    assignee = db.execute(
        select(User).options(joinedload(User.role)).where(User.id == assignee_id)
    ).scalar_one_or_none()
    if assignee is None or not assignee.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignee not found")
    if is_editor(current_user) and assignee.role.name == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Editors cannot assign admins")
    return assignee


def _validate_related_entities(
    db: Session, article_id: int | None, news_post_id: int | None
) -> None:
    if article_id is not None and db.get(Article, article_id) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related article not found")
    if news_post_id is not None and db.get(NewsPost, news_post_id) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related news post not found")


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[Task]:
    statement = select(Task).options(*_task_options()).order_by(desc(Task.updated_at))
    if not (is_admin(current_user) or is_editor(current_user)):
        statement = statement.where(Task.assignee_id == current_user.id)
    return list(db.execute(statement).scalars().all())


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "editor")),
) -> Task:
    assignee = _get_assignee(db, payload.assignee_id, current_user)
    _validate_related_entities(db, payload.related_article_id, payload.related_news_post_id)
    task = Task(
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        creator_id=current_user.id,
        assignee_id=assignee.id,
        related_article_id=payload.related_article_id,
        related_news_post_id=payload.related_news_post_id,
        due_date=payload.due_date,
    )
    db.add(task)
    db.commit()
    return _get_task_or_404(db, task.id)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Task:
    task = _get_task_or_404(db, task_id)
    ensure_can_view_task(current_user, task)
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Task:
    task = _get_task_or_404(db, task_id)
    ensure_can_view_task(current_user, task)
    data = payload.model_dump(exclude_unset=True)

    if not can_manage_task(current_user, task):
        if set(data.keys()) != {"status"}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Employees can update only status")
        if data.get("status") == "cancelled":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Employees cannot cancel tasks")
        task.status = data["status"]
        db.commit()
        return _get_task_or_404(db, task.id)

    if "assignee_id" in data and data["assignee_id"] is not None:
        task.assignee_id = _get_assignee(db, data["assignee_id"], current_user).id
    if "related_article_id" in data or "related_news_post_id" in data:
        _validate_related_entities(
            db,
            data.get("related_article_id", task.related_article_id),
            data.get("related_news_post_id", task.related_news_post_id),
        )
    for field in ("title", "description", "status", "priority", "related_article_id", "related_news_post_id", "due_date"):
        if field in data:
            setattr(task, field, data[field])
    db.commit()
    return _get_task_or_404(db, task.id)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "editor")),
) -> None:
    task = _get_task_or_404(db, task_id)
    db.delete(task)
    db.commit()
