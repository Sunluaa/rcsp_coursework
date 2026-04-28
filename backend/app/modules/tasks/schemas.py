from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.common.schemas import TaskPriority, TaskStatus, UserSummary


class TaskCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    description: str | None = None
    status: TaskStatus = "todo"
    priority: TaskPriority = "medium"
    assignee_id: int
    related_article_id: int | None = None
    related_news_post_id: int | None = None
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assignee_id: int | None = None
    related_article_id: int | None = None
    related_news_post_id: int | None = None
    due_date: datetime | None = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = None
    status: TaskStatus
    priority: TaskPriority
    creator_id: int
    assignee_id: int
    related_article_id: int | None = None
    related_news_post_id: int | None = None
    due_date: datetime | None = None
    created_at: datetime
    updated_at: datetime
    creator: UserSummary
    assignee: UserSummary
