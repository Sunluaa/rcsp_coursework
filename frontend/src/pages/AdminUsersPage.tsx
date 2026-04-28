import { FormEvent, useEffect, useState } from "react";

import { apiFetch } from "../shared/api/client";
import type { RoleName, User } from "../shared/types/api";
import { EmptyState, ErrorState, LoadingState, StatusPill } from "../shared/ui/State";

const roleOptions: RoleName[] = ["admin", "editor", "employee"];

export function AdminUsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [roleName, setRoleName] = useState<RoleName>("employee");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadUsers() {
    setUsers(await apiFetch<User[]>("/users"));
  }

  useEffect(() => {
    loadUsers()
      .catch((err) => setError(err instanceof Error ? err.message : "Cannot load users"))
      .finally(() => setLoading(false));
  }, []);

  async function createUser(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await apiFetch<User>("/users", {
        method: "POST",
        body: JSON.stringify({
          email,
          password,
          full_name: fullName,
          role_name: roleName
        })
      });
      setEmail("");
      setFullName("");
      setPassword("");
      setRoleName("employee");
      await loadUsers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cannot create user");
    }
  }

  async function deactivate(userId: number) {
    setError("");
    try {
      await apiFetch<User>(`/users/${userId}`, { method: "DELETE" });
      await loadUsers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cannot deactivate user");
    }
  }

  if (loading) {
    return <LoadingState />;
  }

  return (
    <section className="page">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Administration</span>
          <h1>Users</h1>
        </div>
      </div>
      {error && <ErrorState message={error} />}
      <form className="panel form admin-form" onSubmit={createUser}>
        <div className="form-grid">
          <label>
            Email
            <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required />
          </label>
          <label>
            Full name
            <input value={fullName} onChange={(event) => setFullName(event.target.value)} required />
          </label>
          <label>
            Password
            <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" minLength={8} required />
          </label>
          <label>
            Role
            <select value={roleName} onChange={(event) => setRoleName(event.target.value as RoleName)}>
              {roleOptions.map((role) => (
                <option key={role} value={role}>
                  {role}
                </option>
              ))}
            </select>
          </label>
        </div>
        <button className="primary-button">Create user</button>
      </form>

      {users.length === 0 ? (
        <EmptyState message="Пользователей пока нет." />
      ) : (
        <div className="panel table-panel">
          {users.map((item) => (
            <div className="table-row" key={item.id}>
              <strong>{item.full_name}</strong>
              <span>{item.email}</span>
              <StatusPill value={item.role.name} />
              <StatusPill value={item.is_active ? "active" : "inactive"} />
              <button className="danger-button" disabled={!item.is_active} onClick={() => deactivate(item.id)}>
                Deactivate
              </button>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
