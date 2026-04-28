import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

import { apiFetch, clearToken, getToken, setToken } from "../shared/api/client";
import type { User } from "../shared/types/api";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  async function refreshUser() {
    if (!getToken()) {
      setUser(null);
      return;
    }
    const current = await apiFetch<User>("/auth/me");
    setUser(current);
  }

  async function login(email: string, password: string) {
    setLoading(true);
    try {
      const token = await apiFetch<{ access_token: string }>("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password })
      });
      setToken(token.access_token);
      await refreshUser();
    } catch (err) {
      clearToken();
      setUser(null);
      throw err;
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    clearToken();
    setUser(null);
  }

  useEffect(() => {
    let active = true;
    const initialToken = getToken();

    if (!initialToken) {
      setUser(null);
      setLoading(false);
      return () => {
        active = false;
      };
    }

    apiFetch<User>("/auth/me")
      .then((current) => {
        if (active && getToken() === initialToken) {
          setUser(current);
        }
      })
      .catch(() => {
        if (active && getToken() === initialToken) {
          clearToken();
          setUser(null);
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
