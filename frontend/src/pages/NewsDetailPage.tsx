import { FormEvent, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { useAuth } from "../app/AuthContext";
import { apiFetch, apiUrl, getToken } from "../shared/api/client";
import type { Attachment, NewsPost } from "../shared/types/api";
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

export function NewsDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const [post, setPost] = useState<NewsPost | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadPost() {
    if (!id) {
      return;
    }
    setPost(await apiFetch<NewsPost>(`/news/${id}`));
  }

  useEffect(() => {
    loadPost()
      .catch((err) => setError(err instanceof Error ? err.message : "Cannot load news"))
      .finally(() => setLoading(false));
  }, [id]);

  async function changeStatus(action: "publish" | "archive") {
    if (!post) {
      return;
    }
    try {
      setPost(await apiFetch<NewsPost>(`/news/${post.id}/${action}`, { method: "POST" }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cannot change status");
    }
  }

  async function handleUpload(event: FormEvent) {
    event.preventDefault();
    if (!post || !file) {
      return;
    }
    const form = new FormData();
    form.append("file", file);
    try {
      await apiFetch(`/attachments/news/${post.id}`, { method: "POST", body: form });
      setFile(null);
      await loadPost();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cannot upload file");
    }
  }

  if (loading) {
    return <LoadingState />;
  }
  if (!post) {
    return <ErrorState message={error || "News post not found"} />;
  }

  const manageable = canManageContent(user, post);

  return (
    <section className="page narrow">
      {error && <ErrorState message={error} />}
      <div className="article-header">
        <div>
          <StatusPill value={post.status} />
          <h1>{post.title}</h1>
          <p>
            {post.category?.name ?? "No category"} · by {post.author.full_name}
          </p>
        </div>
        {manageable && (
          <div className="action-row">
            <Link className="secondary-button" to={`/news/${post.id}/edit`}>
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
      <article className="panel prose">{post.content}</article>
      <section className="panel">
        <h2>Attachments</h2>
        {post.attachments.length === 0 ? (
          <p className="muted">Нет вложений.</p>
        ) : (
          <div className="list">
            {post.attachments.map((attachment) => (
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
