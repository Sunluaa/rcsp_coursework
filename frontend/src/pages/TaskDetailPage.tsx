import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { useAuth } from "../app/AuthContext";
import { apiFetch } from "../shared/api/client";
import type { KnowledgeTask, TaskStatus } from "../shared/types/api";
import { hasAnyRole } from "../shared/utils/roles";
import { ErrorState, LoadingState, StatusPill } from "../shared/ui/State";

export function TaskDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const [task, setTask] = useState<KnowledgeTask | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch<KnowledgeTask>(`/tasks/${id}`)
      .then(setTask)
      .catch((err) => setError(err instanceof Error ? err.message : "Cannot load task"))
      .finally(() => setLoading(false));
  }, [id]);

  async function changeStatus(status: TaskStatus) {
    if (!task) {
      return;
    }
    try {
      setTask(await apiFetch<KnowledgeTask>(`/tasks/${task.id}`, { method: "PATCH", body: JSON.stringify({ status }) }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cannot update task");
    }
  }

  if (loading) {
    return <LoadingState />;
  }
  if (!task) {
    return <ErrorState message={error || "Task not found"} />;
  }

  return (
    <section className="page narrow">
      {error && <ErrorState message={error} />}
      <div className="article-header">
        <div>
          <StatusPill value={task.status} />
          <h1>{task.title}</h1>
          <p>
            Assignee: {task.assignee.full_name} · Creator: {task.creator.full_name}
          </p>
        </div>
        {hasAnyRole(user, ["admin", "editor"]) && (
          <Link className="secondary-button" to={`/tasks/${task.id}/edit`}>
            Edit
          </Link>
        )}
      </div>
      <section className="panel prose">
        <p>{task.description || "No description"}</p>
        <p>
          Priority: <StatusPill value={task.priority} />
        </p>
        {task.due_date && <p>Due date: {new Date(task.due_date).toLocaleString()}</p>}
      </section>
      {user?.id === task.assignee_id && (
        <div className="panel action-row">
          <button className="secondary-button" onClick={() => changeStatus("todo")}>
            Todo
          </button>
          <button className="secondary-button" onClick={() => changeStatus("in_progress")}>
            In progress
          </button>
          <button className="secondary-button" onClick={() => changeStatus("done")}>
            Done
          </button>
        </div>
      )}
    </section>
  );
}
