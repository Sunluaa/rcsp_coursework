import { useAuth } from "../app/AuthContext";

export function ProfilePage() {
  const { user } = useAuth();

  return (
    <section className="page narrow">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Current user</span>
          <h1>Profile</h1>
        </div>
      </div>
      <div className="panel profile-card">
        <div className="avatar">{user?.full_name.slice(0, 2).toUpperCase()}</div>
        <div>
          <h2>{user?.full_name}</h2>
          <p>{user?.email}</p>
          <p>
            Role: <strong>{user?.role.name}</strong>
          </p>
          <p>Status: {user?.is_active ? "active" : "inactive"}</p>
        </div>
      </div>
    </section>
  );
}
