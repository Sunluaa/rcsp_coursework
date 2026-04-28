import { FormEvent, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { useAuth } from "../app/AuthContext";
import { apiFetch, apiUrl, getToken } from "../shared/api/client";
import type { Article, Attachment } from "../shared/types/api";
import { canManageContent } from "../shared/utils/roles";
import { ErrorState, LoadingState, StatusPill } from "../shared/ui/State";

async function downloadAttachment(attachment: Attachment) {
  const response = await fetch(apiUrl(`/attachments/${attachment.id}/download`), {
    headers: { Authorization: `Bearer ${getToken()}` }
  });
  if (!response.ok) {
    throw new Error("Cannot download attachment");
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = attachment.original_filename;
  link.click();
  URL.revokeObjectURL(url);
}

export function ArticleDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const [article, setArticle] = useState<Article | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadArticle() {
    if (!id) {
      return;
    }
    const data = await apiFetch<Article>(`/articles/${id}`);
    setArticle(data);
  }

  useEffect(() => {
    loadArticle()
      .catch((err) => setError(err instanceof Error ? err.message : "Cannot load article"))
      .finally(() => setLoading(false));
  }, [id]);

  async function changeStatus(action: "publish" | "archive") {
    if (!article) {
      return;
    }
    try {
      const updated = await apiFetch<Article>(`/articles/${article.id}/${action}`, { method: "POST" });
      setArticle(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cannot change status");
    }
  }

  async function handleUpload(event: FormEvent) {
    event.preventDefault();
    if (!article || !file) {
      return;
    }
    const form = new FormData();
    form.append("file", file);
    try {
      await apiFetch(`/attachments/articles/${article.id}`, { method: "POST", body: form });
      setFile(null);
      await loadArticle();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cannot upload file");
    }
  }

  if (loading) {
    return <LoadingState />;
  }
  if (!article) {
    return <ErrorState message={error || "Article not found"} />;
  }

  const manageable = canManageContent(user, article);

  return (
    <section className="page narrow">
      {error && <ErrorState message={error} />}
      <div className="article-header">
        <div>
          <StatusPill value={article.status} />
          <h1>{article.title}</h1>
          <p>
            {article.category?.name ?? "No category"} · by {article.author.full_name}
          </p>
        </div>
        {manageable && (
          <div className="action-row">
            <Link className="secondary-button" to={`/articles/${article.id}/edit`}>
              Edit
            </Link>
            <button className="secondary-button" onClick={() => changeStatus("publish")}>
              Publish
            </button>
            <button className="secondary-button" onClick={() => changeStatus("archive")}>
              Archive
            </button>
          </div>
        )}
      </div>
      <article className="panel prose">{article.content}</article>
      <div className="tag-row">
        {article.tags.map((tag) => (
          <span key={tag.id}>#{tag.slug}</span>
        ))}
      </div>

      <section className="panel">
        <h2>Attachments</h2>
        {article.attachments.length === 0 ? (
          <p className="muted">Нет вложений.</p>
        ) : (
          <div className="list">
            {article.attachments.map((attachment) => (
              <button
                key={attachment.id}
                className="list-row button-row"
                onClick={() => downloadAttachment(attachment).catch((err) => setError(err.message))}
              >
                <span>{attachment.original_filename}</span>
                <small>{Math.ceil(attachment.size / 1024)} KB</small>
              </button>
            ))}
          </div>
        )}
        {manageable && (
          <form className="upload-form" onSubmit={handleUpload}>
            <input
              type="file"
              accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            />
            <button className="secondary-button" disabled={!file}>
              Upload PDF/DOCX
            </button>
          </form>
        )}
      </section>
    </section>
  );
}
