import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../app/AuthContext";
import { apiFetch } from "../shared/api/client";
import type { Article, KnowledgeTask, NewsPost } from "../shared/types/api";
import { EmptyState, ErrorState, LoadingState, StatusPill } from "../shared/ui/State";

export function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [articles, setArticles] = useState<Article[]>([]);
  const [news, setNews] = useState<NewsPost[]>([]);
  const [tasks, setTasks] = useState<KnowledgeTask[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([apiFetch<Article[]>("/articles"), apiFetch<NewsPost[]>("/news"), apiFetch<KnowledgeTask[]>("/tasks")])
      .then(([articleData, newsData, taskData]) => {
        setArticles(articleData);
        setNews(newsData);
        setTasks(taskData);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Cannot load dashboard"))
      .finally(() => setLoading(false));
  }, []);

  function handleSearch(event: FormEvent) {
    event.preventDefault();
    navigate(`/search?query=${encodeURIComponent(query)}`);
  }

  if (loading) {
    return <LoadingState />;
  }

  return (
    <section className="page">
      <div className="hero-panel">
        <div>
          <span className="eyebrow">Welcome, {user?.full_name}</span>
          <h1>База знаний, новости и задачи в одном рабочем пространстве</h1>
          <p>Ищите инструкции, читайте опубликованные материалы и держите рабочие задачи под рукой.</p>
        </div>
        <form className="search-box" onSubmit={handleSearch}>
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search knowledge..." />
          <button className="primary-button">Search</button>
        </form>
      </div>

      {error && <ErrorState message={error} />}

      <div className="stats-grid">
        <div className="stat-card">
          <span>Articles</span>
          <strong>{articles.length}</strong>
        </div>
        <div className="stat-card">
          <span>News</span>
          <strong>{news.length}</strong>
        </div>
        <div className="stat-card">
          <span>Tasks</span>
          <strong>{tasks.length}</strong>
        </div>
      </div>

      <div className="grid-two">
        <section className="panel">
          <div className="section-heading">
            <h2>Recent articles</h2>
            <Link to="/articles">All articles</Link>
          </div>
          {articles.length === 0 ? (
            <EmptyState message="Материалов пока нет." />
          ) : (
            <div className="list">
              {articles.slice(0, 5).map((article) => (
                <Link className="list-row" key={article.id} to={`/articles/${article.id}`}>
                  <span>{article.title}</span>
                  <StatusPill value={article.status} />
                </Link>
              ))}
            </div>
          )}
        </section>

        <section className="panel">
          <div className="section-heading">
            <h2>My task stream</h2>
            <Link to="/tasks">All tasks</Link>
          </div>
          {tasks.length === 0 ? (
            <EmptyState message="Задач пока нет." />
          ) : (
            <div className="list">
              {tasks.slice(0, 5).map((task) => (
                <Link className="list-row" key={task.id} to={`/tasks/${task.id}`}>
                  <span>{task.title}</span>
                  <StatusPill value={task.status} />
                </Link>
              ))}
            </div>
          )}
        </section>
      </div>
    </section>
  );
}
