from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.core.utils import slugify
from app.models import Article, Category, NewsPost, Role, Tag, Task, User


ROLE_DESCRIPTIONS = {
    "admin": "Full platform administration",
    "editor": "Content and task management",
    "employee": "Read published knowledge and work with assigned tasks",
}


def require_seed_password(value: str | None, env_name: str) -> str:
    if not value:
        raise RuntimeError(f"{env_name} must be set before running seed")
    return value


def get_or_create_role(db, name: str) -> Role:
    role = db.execute(select(Role).where(Role.name == name)).scalar_one_or_none()
    if role:
        return role
    role = Role(name=name, description=ROLE_DESCRIPTIONS[name])
    db.add(role)
    db.flush()
    return role


def get_or_create_user(db, *, email: str, password: str, full_name: str, role: Role) -> User:
    user = db.execute(select(User).where(User.email == email.lower())).scalar_one_or_none()
    if user:
        return user
    user = User(
        email=email.lower(),
        password_hash=get_password_hash(password),
        full_name=full_name,
        role=role,
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def get_or_create_category(db, name: str, description: str) -> Category:
    slug = slugify(name, "category")
    category = db.execute(select(Category).where(Category.slug == slug)).scalar_one_or_none()
    if category:
        return category
    category = Category(name=name, slug=slug, description=description)
    db.add(category)
    db.flush()
    return category


def get_or_create_tag(db, name: str) -> Tag:
    slug = slugify(name, "tag")
    tag = db.execute(select(Tag).where(Tag.slug == slug)).scalar_one_or_none()
    if tag:
        return tag
    tag = Tag(name=name, slug=slug)
    db.add(tag)
    db.flush()
    return tag


def create_article_if_missing(db, *, title: str, content: str, author: User, category: Category, tags: list[Tag], status: str) -> Article:
    slug = slugify(title, "article")
    article = db.execute(select(Article).where(Article.slug == slug)).scalar_one_or_none()
    if article:
        return article
    article = Article(
        title=title,
        slug=slug,
        content=content,
        status=status,
        author=author,
        category=category,
        published_at=datetime.now(UTC) if status == "published" else None,
    )
    article.tags = tags
    db.add(article)
    db.flush()
    return article


def create_news_if_missing(db, *, title: str, content: str, author: User, category: Category, tags: list[Tag], status: str) -> NewsPost:
    slug = slugify(title, "news")
    news_post = db.execute(select(NewsPost).where(NewsPost.slug == slug)).scalar_one_or_none()
    if news_post:
        return news_post
    news_post = NewsPost(
        title=title,
        slug=slug,
        content=content,
        status=status,
        author=author,
        category=category,
        published_at=datetime.now(UTC) if status == "published" else None,
    )
    news_post.tags = tags
    db.add(news_post)
    db.flush()
    return news_post


def create_task_if_missing(db, *, title: str, description: str, creator: User, assignee: User, priority: str, article: Article | None = None, news_post: NewsPost | None = None) -> Task:
    task = db.execute(select(Task).where(Task.title == title, Task.assignee_id == assignee.id)).scalar_one_or_none()
    if task:
        return task
    task = Task(
        title=title,
        description=description,
        status="todo",
        priority=priority,
        creator=creator,
        assignee=assignee,
        related_article=article,
        related_news_post=news_post,
        due_date=datetime.now(UTC) + timedelta(days=7),
    )
    db.add(task)
    db.flush()
    return task


def main() -> None:
    settings = get_settings()
    admin_password = require_seed_password(settings.seed_admin_password, "SEED_ADMIN_PASSWORD")
    editor_password = require_seed_password(settings.seed_editor_password, "SEED_EDITOR_PASSWORD")
    employee_password = require_seed_password(settings.seed_employee_password, "SEED_EMPLOYEE_PASSWORD")

    with SessionLocal() as db:
        admin_role = get_or_create_role(db, "admin")
        editor_role = get_or_create_role(db, "editor")
        employee_role = get_or_create_role(db, "employee")

        admin = get_or_create_user(
            db,
            email=settings.seed_admin_email,
            password=admin_password,
            full_name="Admin KnowledgeBaZa",
            role=admin_role,
        )
        editor = get_or_create_user(
            db,
            email=settings.seed_editor_email,
            password=editor_password,
            full_name="Editor KnowledgeBaZa",
            role=editor_role,
        )
        employee = get_or_create_user(
            db,
            email=settings.seed_employee_email,
            password=employee_password,
            full_name="Employee KnowledgeBaZa",
            role=employee_role,
        )

        onboarding = get_or_create_category(db, "Onboarding", "Materials for new employees")
        operations = get_or_create_category(db, "Operations", "Internal processes and regulations")
        product = get_or_create_category(db, "Product", "Product knowledge and release notes")

        tag_policy = get_or_create_tag(db, "Policy")
        tag_process = get_or_create_tag(db, "Process")
        tag_release = get_or_create_tag(db, "Release")
        tag_hr = get_or_create_tag(db, "HR")

        article_1 = create_article_if_missing(
            db,
            title="How to start with KnowledgeBaZa",
            content="This article explains how to use the internal knowledge base, search, news and tasks.",
            author=editor,
            category=onboarding,
            tags=[tag_process, tag_hr],
            status="published",
        )
        create_article_if_missing(
            db,
            title="Draft: incident response checklist",
            content="A draft checklist for handling internal incidents. Editors can refine it before publishing.",
            author=editor,
            category=operations,
            tags=[tag_policy, tag_process],
            status="draft",
        )

        news_1 = create_news_if_missing(
            db,
            title="KnowledgeBaZa MVP launched",
            content="The first MVP version is available for internal testing.",
            author=editor,
            category=product,
            tags=[tag_release],
            status="published",
        )
        create_news_if_missing(
            db,
            title="Draft: upcoming policy update",
            content="This draft news post will be published after review.",
            author=admin,
            category=operations,
            tags=[tag_policy],
            status="draft",
        )

        create_task_if_missing(
            db,
            title="Read onboarding article",
            description="Open the published onboarding article and confirm that the instructions are clear.",
            creator=editor,
            assignee=employee,
            priority="medium",
            article=article_1,
        )
        create_task_if_missing(
            db,
            title="Review MVP launch news",
            description="Check the launch news post before sharing feedback.",
            creator=admin,
            assignee=editor,
            priority="high",
            news_post=news_1,
        )

        db.commit()

    print("Seed completed")


if __name__ == "__main__":
    main()
