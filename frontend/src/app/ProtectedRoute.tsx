import { Navigate, Outlet } from "react-router-dom";

import { useAuth } from "./AuthContext";
import { LoadingState } from "../shared/ui/State";
import type { RoleName } from "../shared/types/api";

export function ProtectedRoute({ roles }: { roles?: RoleName[] }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingState label="Проверяем сессию..." />;
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if (roles && !roles.includes(user.role.name)) {
    return <Navigate to="/" replace />;
  }
  return <Outlet />;
}
