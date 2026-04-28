import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { apiFetch } from "../shared/api/client";
import type { Category, ContentStatus, NewsPost, Tag } from "../shared/types/api";
import { ErrorState, LoadingState } from "../shared/ui/State";

const statuses: ContentStatus[] = ["draft", "published", "archived"];

export function NewsFormPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditing = Boolean(id);
  const [categories, setCategories] = useState<Category[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [status, setStatus] = useState<ContentStatus>("draft");
  const [categoryId, setCategoryId] = useState("");
  const [tagIds, setTagIds] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const requests: Promise<unknown>[] = [
      apiFetch<Category[]>("/categories").then(setCategories),
      apiFetch<Tag[]>("/tags").then(setTags)
    ];
    if (id) {
      requests.push(
        apiFetch<NewsPost>(`/news/${id}`).then((post) => {
          setTitle(post.title);
          setContent(post.content);
          setStatus(post.status);
          setCategoryId(post.category_id ? String(post.category_id) : "");
          setTagIds(post.tags.map((tag) => tag.id));
        })
      );
    }
    Promise.all(requests)
      .catch((err) => setError(err instanceof Error ? err.message : "Cannot load form"))
      .finally(() => setLoading(false));
  }, [id]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    const payload = {
      title,
      content,
      status,
      category_id: categoryId ? Number(categoryId) : null,
      tag_ids: tagIds
    };
    try {
      const post = await apiFetch<NewsPost>(isEditing ? `/news/${id}` : "/news", {
        method: isEditing ? "PATCH" : "POST",
        body: JSON.stringify(payload)
      });
      navigate(`/news/${post.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cannot save news post");
    }
  }

  if (loading) {
    return <LoadingState />;
  }

  return (
    <section className="page narrow">
      <h1>{isEditing ? "Edit news" : "Create news"}</h1>
      {error && <ErrorState message={error} />}
      <form className="form panel" onSubmit={handleSubmit}>
        <label>
          Title
          <input value={title} onChange={(event) => setTitle(event.target.value)} required />
        </label>
        <label>
          Status
          <select value={status} onChange={(event) => setStatus(event.target.value as ContentStatus)}>
            {statuses.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </label>
        <label>
          Category
          <select value={categoryId} onChange={(event) => setCategoryId(event.target.value)}>
            <option value="">No category</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </label>
        <fieldset>
          <legend>Tags</legend>
          <div className="checkbox-grid">
            {tags.map((tag) => (
              <label key={tag.id} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={tagIds.includes(tag.id)}
                  onChange={(event) =>
                    setTagIds((current) =>
                      event.target.checked ? [...current, tag.id] : current.filter((tagId) => tagId !== tag.id)
                    )
                  }
                />
                {tag.name}
              </label>
            ))}
          </div>
        </fieldset>
        <label>
          Content
          <textarea value={content} onChange={(event) => setContent(event.target.value)} rows={12} required />
        </label>
        <button className="primary-button">Save news</button>
      </form>
    </section>
  );
}
