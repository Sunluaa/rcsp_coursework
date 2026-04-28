import { FormEvent, useEffect, useState } from "react";

import { useAuth } from "../app/AuthContext";
import { apiFetch } from "../shared/api/client";
import type { Category, Tag } from "../shared/types/api";
import { hasAnyRole } from "../shared/utils/roles";
import { EmptyState, ErrorState, LoadingState } from "../shared/ui/State";

export function TaxonomyPage() {
  const { user } = useAuth();
  const canManage = hasAnyRole(user, ["admin", "editor"]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [categoryName, setCategoryName] = useState("");
  const [tagName, setTagName] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadData() {
    const [categoryData, tagData] = await Promise.all([apiFetch<Category[]>("/categories"), apiFetch<Tag[]>("/tags")]);
    setCategories(categoryData);
    setTags(tagData);
  }

  useEffect(() => {
    loadData()
      .catch((err) => setError(err instanceof Error ? err.message : "Cannot load taxonomy"))
      .finally(() => setLoading(false));
  }, []);

  async function createCategory(event: FormEvent) {
    event.preventDefault();
    await apiFetch("/categories", { method: "POST", body: JSON.stringify({ name: categoryName }) });
    setCategoryName("");
    await loadData();
  }

  async function createTag(event: FormEvent) {
    event.preventDefault();
    await apiFetch("/tags", { method: "POST", body: JSON.stringify({ name: tagName }) });
    setTagName("");
    await loadData();
  }

  async function remove(path: string) {
    await apiFetch(path, { method: "DELETE" });
    await loadData();
  }

  if (loading) {
    return <LoadingState />;
  }

  return (
    <section className="page">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Classification</span>
          <h1>Categories & Tags</h1>
        </div>
      </div>
      {error && <ErrorState message={error} />}
      <div className="grid-two">
        <section className="panel">
          <h2>Categories</h2>
          {canManage && (
            <form className="inline-form" onSubmit={createCategory}>
              <input value={categoryName} onChange={(event) => setCategoryName(event.target.value)} placeholder="Category name" required />
              <button className="secondary-button">Add</button>
            </form>
          )}
          {categories.length === 0 ? (
            <EmptyState message="Категорий пока нет." />
          ) : (
            <div className="list">
              {categories.map((category) => (
                <div className="list-row" key={category.id}>
                  <span>{category.name}</span>
                  {canManage && (
                    <button className="danger-button" onClick={() => remove(`/categories/${category.id}`)}>
                      Delete
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
        <section className="panel">
          <h2>Tags</h2>
          {canManage && (
            <form className="inline-form" onSubmit={createTag}>
              <input value={tagName} onChange={(event) => setTagName(event.target.value)} placeholder="Tag name" required />
              <button className="secondary-button">Add</button>
            </form>
          )}
          {tags.length === 0 ? (
            <EmptyState message="Тегов пока нет." />
          ) : (
            <div className="list">
              {tags.map((tag) => (
                <div className="list-row" key={tag.id}>
                  <span>#{tag.slug}</span>
                  {canManage && (
                    <button className="danger-button" onClick={() => remove(`/tags/${tag.id}`)}>
                      Delete
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </section>
  );
}
