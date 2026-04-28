import { FormEvent, useState } from "react";
import { Navigate } from "react-router-dom";

import { useAuth } from "../app/AuthContext";

export function LoginPage() {
  const { user, loading, login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setSubmitting(false);
    }
  }

  if (!loading && user) {
    return <Navigate to="/" replace />;
  }

  return (
    <main className="login-page">
      <section className="login-card">
        <div className="brand login-brand">
          <span className="brand-mark">KB</span>
          <div>
            <strong>KnowledgeBaZa</strong>
            <small>company knowledge hub</small>
          </div>
        </div>
        <h1>Вход во внутреннюю базу знаний</h1>
        <p>Используйте seed-аккаунты из README или учетную запись, созданную администратором.</p>
        <form onSubmit={handleSubmit} className="form">
          <label>
            Email
            <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required />
          </label>
          <label>
            Password
            <input
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              type="password"
              minLength={8}
              required
            />
          </label>
          {error && <div className="state state-error">{error}</div>}
          <button className="primary-button" disabled={submitting}>
            {submitting ? "Входим..." : "Login"}
          </button>
        </form>
      </section>
    </main>
  );
}
