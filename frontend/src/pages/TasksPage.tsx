import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../app/AuthContext";
import { apiFetch } from "../shared/api/client";
import type { KnowledgeTask } from "../shared/types/api";
import { hasAnyRole } from "../shared/utils/roles";
import { EmptyState, ErrorState, LoadingState, StatusPill } from "../shared/ui/State";

export function TasksPage() {
  const { user } = useAuth();
  const [tasks, setTasks] = useState<KnowledgeTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch<KnowledgeTask[]>("/tasks")
      .then(setTasks)
      .catch((err) => setError(err instanceof Error ? err.message : "Cannot load tasks"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <LoadingState />;
  }

  return (
    <section className="page">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Workflow</span>
          <h1>Tasks</h1>
        </div>
        {hasAnyRole(user, ["admin", "editor"]) && (
          <Link className="primary-button" to="/tasks/new">
            New task
          </Link>
        )}
      </div>
      {error && <ErrorState message={error} />}
      {tasks.length === 0 ? (
        <EmptyState message="Задач пока нет." />
      ) : (
        <div className="panel table-panel">
          {tasks.map((task) => (
            <Link className="table-row" key={task.id} to={`/tasks/${task.id}`}>
              <strong>{task.title}</strong>
              <span>{task.assignee.full_name}</span>
              <StatusPill value={task.priority} />
              <StatusPill value={task.status} />
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
