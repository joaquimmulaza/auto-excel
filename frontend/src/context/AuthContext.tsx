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
        // #region agent log
        try {
          const base =
            typeof window !== "undefined" &&
            window.location.hostname !== "localhost" &&
            window.location.hostname !== "127.0.0.1"
              ? `${window.location.origin}/api/v1`
              : process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ||
                "http://localhost:8000/api/v1";
          fetch(`${base}/__debug/agent-log`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              hypothesisId: "C",
              location: "AuthContext.tsx:fetchMe:catch",
              message: isAuthFailure
                ? "clearing token after auth failure"
                : "keeping token after non-auth fetchMe failure",
              data: {
                errMessage: err instanceof Error ? err.message : String(err),
                errCode: code,
                errStatus: status,
                isAuthFailure,
                hadToken: !!getStoredToken(),
                tokenLen: getStoredToken()?.length ?? 0,
                runId: "post-fix",
              },
              timestamp: Date.now(),
            }),
            keepalive: true,
          }).catch(() => {});
        } catch {
          /* ignore */
        }
        // #endregion
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
