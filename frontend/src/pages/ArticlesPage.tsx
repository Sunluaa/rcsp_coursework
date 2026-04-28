import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../app/AuthContext";
import { apiFetch } from "../shared/api/client";
import type { Article } from "../shared/types/api";
import { hasAnyRole } from "../shared/utils/roles";
import { EmptyState, ErrorState, LoadingState, StatusPill } from "../shared/ui/State";

export function ArticlesPage() {
  const { user } = useAuth();
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch<Article[]>("/articles")
      .then(setArticles)
      .catch((err) => setError(err instanceof Error ? err.message : "Cannot load articles"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <LoadingState />;
  }

  return (
    <section className="page">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Knowledge Base</span>
          <h1>Articles</h1>
        </div>
        {hasAnyRole(user, ["admin", "editor"]) && (
          <Link className="primary-button" to="/articles/new">
            New article
          </Link>
        )}
      </div>
      {error && <ErrorState message={error} />}
      {articles.length === 0 ? (
        <EmptyState message="Статей пока нет." />
      ) : (
        <div className="cards-grid">
          {articles.map((article) => (
            <Link className="content-card" key={article.id} to={`/articles/${article.id}`}>
              <div className="card-topline">
                <StatusPill value={article.status} />
                <span>{article.category?.name ?? "No category"}</span>
              </div>
              <h2>{article.title}</h2>
              <p>{article.content.slice(0, 150)}</p>
              <div className="tag-row">
                {article.tags.map((tag) => (
                  <span key={tag.id}>#{tag.slug}</span>
                ))}
              </div>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
