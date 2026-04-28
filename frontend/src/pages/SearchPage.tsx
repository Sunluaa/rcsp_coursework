import { FormEvent, useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { apiFetch } from "../shared/api/client";
import type { SearchItem } from "../shared/types/api";
import { EmptyState, ErrorState, LoadingState, StatusPill } from "../shared/ui/State";

export function SearchPage() {
  const [params, setParams] = useSearchParams();
  const [query, setQuery] = useState(params.get("query") ?? "");
  const [type, setType] = useState(params.get("type") ?? "all");
  const [items, setItems] = useState<SearchItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function runSearch(searchQuery: string, searchType: string) {
    setLoading(true);
    setError("");
    try {
      const response = await apiFetch<{ items: SearchItem[] }>(
        `/search?query=${encodeURIComponent(searchQuery)}&type=${encodeURIComponent(searchType)}`
      );
      setItems(response.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    runSearch(params.get("query") ?? "", params.get("type") ?? "all");
  }, [params]);

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setParams({ query, type });
  }

  return (
    <section className="page">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Find fast</span>
          <h1>Search</h1>
        </div>
      </div>
      <form className="panel search-form" onSubmit={handleSubmit}>
        <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search by title or content" />
        <select value={type} onChange={(event) => setType(event.target.value)}>
          <option value="all">All</option>
          <option value="articles">Articles</option>
          <option value="news">News</option>
        </select>
        <button className="primary-button">Search</button>
      </form>
      {error && <ErrorState message={error} />}
      {loading ? (
        <LoadingState />
      ) : items.length === 0 ? (
        <EmptyState message="Ничего не найдено." />
      ) : (
        <div className="cards-grid">
          {items.map((item) => (
            <Link
              className="content-card"
              key={`${item.type}-${item.id}`}
              to={item.type === "article" ? `/articles/${item.id}` : `/news/${item.id}`}
            >
              <div className="card-topline">
                <StatusPill value={item.type} />
                <StatusPill value={item.status} />
              </div>
              <h2>{item.title}</h2>
              <p>{item.snippet}</p>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
