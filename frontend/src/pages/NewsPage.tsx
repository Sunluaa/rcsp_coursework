import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../app/AuthContext";
import { apiFetch } from "../shared/api/client";
import type { NewsPost } from "../shared/types/api";
import { hasAnyRole } from "../shared/utils/roles";
import { EmptyState, ErrorState, LoadingState, StatusPill } from "../shared/ui/State";

export function NewsPage() {
  const { user } = useAuth();
  const [news, setNews] = useState<NewsPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch<NewsPost[]>("/news")
      .then(setNews)
      .catch((err) => setError(err instanceof Error ? err.message : "Cannot load news"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <LoadingState />;
  }

  return (
    <section className="page">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Company Feed</span>
          <h1>News</h1>
        </div>
        {hasAnyRole(user, ["admin", "editor"]) && (
          <Link className="primary-button" to="/news/new">
            New post
          </Link>
        )}
      </div>
      {error && <ErrorState message={error} />}
      {news.length === 0 ? (
        <EmptyState message="Новостей пока нет." />
      ) : (
        <div className="cards-grid">
          {news.map((post) => (
            <Link className="content-card" key={post.id} to={`/news/${post.id}`}>
              <div className="card-topline">
                <StatusPill value={post.status} />
                <span>{post.category?.name ?? "No category"}</span>
              </div>
              <h2>{post.title}</h2>
              <p>{post.content.slice(0, 150)}</p>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
