from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.config import get_settings
from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.core.permissions import ensure_can_download_attachment, ensure_can_manage_content
from app.models import Article, Attachment, NewsPost, User
from app.modules.common.schemas import AttachmentRead
from app.storage.factory import get_storage_service


router = APIRouter(prefix="/attachments", tags=["attachments"])

ALLOWED_MIME_TYPES = {
    ".pdf": {"application/pdf"},
    ".docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
}


def _article_options():
    return joinedload(Article.author).joinedload(User.role), selectinload(Article.attachments)


def _news_options():
    return joinedload(NewsPost.author).joinedload(User.role), selectinload(NewsPost.attachments)


def _get_attachment_or_404(db: Session, attachment_id: int) -> Attachment:
    attachment = db.execute(
        select(Attachment)
        .options(
            joinedload(Attachment.article).joinedload(Article.author).joinedload(User.role),
            joinedload(Attachment.news_post).joinedload(NewsPost.author).joinedload(User.role),
        )
        .where(Attachment.id == attachment_id)
    ).scalar_one_or_none()
    if attachment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")
    return attachment


async def _validate_upload(file: UploadFile) -> tuple[bytes, str]:
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF and DOCX files are allowed")
    if file.content_type not in ALLOWED_MIME_TYPES[extension]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file MIME type")
    content = await file.read()
    max_size = get_settings().max_upload_size_bytes
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty files are not allowed")
    if len(content) > max_size:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is too large")
    return content, extension


@router.post("/articles/{article_id}", response_model=AttachmentRead, status_code=status.HTTP_201_CREATED)
async def upload_article_attachment(
    article_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "editor")),
) -> Attachment:
    article = db.execute(select(Article).options(*_article_options()).where(Article.id == article_id)).scalar_one_or_none()
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    ensure_can_manage_content(current_user, article)
    content, extension = await _validate_upload(file)
    storage = get_storage_service()
    object_key = f"articles/{article_id}/{uuid4().hex}{extension}"
    await storage.save(object_key, content, file.content_type or "application/octet-stream")
    attachment = Attachment(
        original_filename=file.filename or f"attachment{extension}",
        object_key=object_key,
        content_type=file.content_type or "application/octet-stream",
        size=len(content),
        storage_provider=storage.provider_name,
        article_id=article_id,
        uploaded_by=current_user.id,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


@router.post("/news/{news_post_id}", response_model=AttachmentRead, status_code=status.HTTP_201_CREATED)
async def upload_news_attachment(
    news_post_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "editor")),
) -> Attachment:
    news_post = db.execute(
        select(NewsPost).options(*_news_options()).where(NewsPost.id == news_post_id)
    ).scalar_one_or_none()
    if news_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News post not found")
    ensure_can_manage_content(current_user, news_post)
    content, extension = await _validate_upload(file)
    storage = get_storage_service()
    object_key = f"news/{news_post_id}/{uuid4().hex}{extension}"
    await storage.save(object_key, content, file.content_type or "application/octet-stream")
    attachment = Attachment(
        original_filename=file.filename or f"attachment{extension}",
        object_key=object_key,
        content_type=file.content_type or "application/octet-stream",
        size=len(content),
        storage_provider=storage.provider_name,
        news_post_id=news_post_id,
        uploaded_by=current_user.id,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


@router.get("/{attachment_id}/download")
async def download_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    attachment = _get_attachment_or_404(db, attachment_id)
    ensure_can_download_attachment(current_user, attachment)
    content = await get_storage_service().read(attachment.object_key)
    headers = {"Content-Disposition": f'attachment; filename="{attachment.original_filename}"'}
    return StreamingResponse(BytesIO(content), media_type=attachment.content_type, headers=headers)


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "editor")),
) -> None:
    attachment = _get_attachment_or_404(db, attachment_id)
    item = attachment.article or attachment.news_post
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment owner not found")
    ensure_can_manage_content(current_user, item)
    await get_storage_service().delete(attachment.object_key)
    db.delete(attachment)
    db.commit()
