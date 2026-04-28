import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { useAuth } from "./AuthContext";
import { hasAnyRole } from "../shared/utils/roles";

export function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">KB</span>
          <div>
            <strong>KnowledgeBaZa</strong>
            <small>internal workspace</small>
          </div>
        </div>
        <nav className="nav">
          <NavLink to="/">Dashboard</NavLink>
          <NavLink to="/articles">Knowledge Base</NavLink>
          <NavLink to="/news">News</NavLink>
          <NavLink to="/tasks">Tasks</NavLink>
          <NavLink to="/search">Search</NavLink>
          <NavLink to="/taxonomy">Categories & Tags</NavLink>
          {hasAnyRole(user, ["admin"]) && <NavLink to="/admin/users">Admin Users</NavLink>}
          <NavLink to="/profile">Profile</NavLink>
        </nav>
        <div className="sidebar-footer">
          <span>{user?.full_name}</span>
          <small>{user?.role.name}</small>
          <button className="ghost-button" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
