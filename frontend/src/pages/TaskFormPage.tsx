import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { apiFetch } from "../shared/api/client";
import type { KnowledgeTask, TaskPriority, TaskStatus, User } from "../shared/types/api";
import { ErrorState, LoadingState } from "../shared/ui/State";

const statuses: TaskStatus[] = ["todo", "in_progress", "done", "cancelled"];
const priorities: TaskPriority[] = ["low", "medium", "high"];

export function TaskFormPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditing = Boolean(id);
  const [users, setUsers] = useState<User[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState<TaskStatus>("todo");
  const [priority, setPriority] = useState<TaskPriority>("medium");
  const [assigneeId, setAssigneeId] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const requests: Promise<unknown>[] = [apiFetch<User[]>("/users/assignable").then(setUsers)];
    if (id) {
      requests.push(
        apiFetch<KnowledgeTask>(`/tasks/${id}`).then((task) => {
          setTitle(task.title);
          setDescription(task.description ?? "");
          setStatus(task.status);
          setPriority(task.priority);
          setAssigneeId(String(task.assignee_id));
          setDueDate(task.due_date ? task.due_date.slice(0, 16) : "");
        })
      );
    }
    Promise.all(requests)
      .catch((err) => setError(err instanceof Error ? err.message : "Cannot load task form"))
      .finally(() => setLoading(false));
  }, [id]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    const payload = {
      title,
      description,
      status,
      priority,
      assignee_id: Number(assigneeId),
      due_date: dueDate ? new Date(dueDate).toISOString() : null
    };
    try {
      const task = await apiFetch<KnowledgeTask>(isEditing ? `/tasks/${id}` : "/tasks", {
        method: isEditing ? "PATCH" : "POST",
        body: JSON.stringify(payload)
      });
      navigate(`/tasks/${task.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cannot save task");
    }
  }

  if (loading) {
    return <LoadingState />;
  }

  return (
    <section className="page narrow">
      <h1>{isEditing ? "Edit task" : "Create task"}</h1>
      {error && <ErrorState message={error} />}
      <form className="form panel" onSubmit={handleSubmit}>
        <label>
          Title
          <input value={title} onChange={(event) => setTitle(event.target.value)} required />
        </label>
        <label>
          Assignee
          <select value={assigneeId} onChange={(event) => setAssigneeId(event.target.value)} required>
            <option value="">Choose user</option>
            {users.map((item) => (
              <option key={item.id} value={item.id}>
                {item.full_name} · {item.role.name}
              </option>
            ))}
          </select>
        </label>
        <div className="form-grid">
          <label>
            Status
            <select value={status} onChange={(event) => setStatus(event.target.value as TaskStatus)}>
              {statuses.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
          <label>
            Priority
            <select value={priority} onChange={(event) => setPriority(event.target.value as TaskPriority)}>
              {priorities.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
        </div>
        <label>
          Due date
          <input type="datetime-local" value={dueDate} onChange={(event) => setDueDate(event.target.value)} />
        </label>
        <label>
          Description
          <textarea value={description} onChange={(event) => setDescription(event.target.value)} rows={8} />
        </label>
        <button className="primary-button">Save task</button>
      </form>
    </section>
  );
}
