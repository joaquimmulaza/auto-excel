"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { CurrentUser, UserRole } from "@/types";
import { fetchMe, login as apiLogin, setStoredToken, getStoredToken } from "@/lib/api";

interface AuthContextType {
  user: CurrentUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isOperador: boolean;
  isComercial: boolean;
  isAdmin: boolean;
  canApprove: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      setLoading(false);
      return;
    }
    fetchMe()
      .then(setUser)
      .catch((err) => {
        const status = (err as { status?: number })?.status;
        const code = (err as { code?: string })?.code;
        const isAuthFailure =
          status === 401 ||
          code === "INVALID_TOKEN" ||
          code === "NOT_AUTHENTICATED" ||
          code === "INVALID_CREDENTIALS";
        // Only wipe session on real auth failures — not network/5xx/DB blips.
        if (isAuthFailure) {
          setStoredToken(null);
          setUser(null);
        }
      })
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const result = await apiLogin(email, password);
    setUser(result.user);
  }, []);

  const logout = useCallback(() => {
    setStoredToken(null);
    setUser(null);
  }, []);

  const role = user?.role as UserRole | undefined;
  const isOperador = role === "OPERADOR";
  const isComercial = role === "COMERCIAL";
  const isAdmin = role === "ADMIN";
  const canApprove = isOperador || isAdmin;

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        isOperador,
        isComercial,
        isAdmin,
        canApprove,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
