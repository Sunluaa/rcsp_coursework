from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.modules.articles.router import router as articles_router
from app.modules.attachments.router import router as attachments_router
from app.modules.auth.router import router as auth_router
from app.modules.categories.router import router as categories_router
from app.modules.news.router import router as news_router
from app.modules.roles.router import router as roles_router
from app.modules.search.router import router as search_router
from app.modules.tags.router import router as tags_router
from app.modules.tasks.router import router as tasks_router
from app.modules.users.router import router as users_router


settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")
register_exception_handlers(app)

if settings.cors_origin_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(roles_router, prefix="/api")
app.include_router(articles_router, prefix="/api")
app.include_router(news_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
app.include_router(categories_router, prefix="/api")
app.include_router(tags_router, prefix="/api")
app.include_router(attachments_router, prefix="/api")
app.include_router(search_router, prefix="/api")


@app.get("/api/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
