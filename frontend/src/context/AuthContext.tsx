"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { CurrentUser, UserRole } from "@/types";
import {
  fetchMe,
  login as apiLogin,
  setStoredToken,
  getStoredToken,
} from "@/lib/api";
import {
  getSupabaseBrowserClient,
  isSupabaseAuthConfigured,
} from "@/lib/supabase";

interface AuthContextType {
  user: CurrentUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
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
    let cancelled = false;
    let unsubscribe: (() => void) | undefined;

    async function boot() {
      try {
        if (isSupabaseAuthConfigured()) {
          const supabase = getSupabaseBrowserClient();
          const { data } = await supabase.auth.getSession();
          const token = data.session?.access_token;
          if (token) {
            setStoredToken(token);
            const me = await fetchMe();
            if (!cancelled) setUser(me);
          } else {
            setStoredToken(null);
            if (!cancelled) setUser(null);
          }

          const { data: sub } = supabase.auth.onAuthStateChange(
            async (_event, session) => {
              const access = session?.access_token ?? null;
              setStoredToken(access);
              if (!access) {
                if (!cancelled) setUser(null);
                return;
              }
              try {
                const me = await fetchMe();
                if (!cancelled) setUser(me);
              } catch {
                if (!cancelled) setUser(null);
              }
            }
          );
          unsubscribe = () => sub.subscription.unsubscribe();
          return;
        }

        const token = getStoredToken();
        if (!token) {
          if (!cancelled) setUser(null);
          return;
        }
        const me = await fetchMe();
        if (!cancelled) setUser(me);
      } catch {
        setStoredToken(null);
        if (!cancelled) setUser(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void boot();
    return () => {
      cancelled = true;
      unsubscribe?.();
    };
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    if (isSupabaseAuthConfigured()) {
      const supabase = getSupabaseBrowserClient();
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });
      if (error || !data.session?.access_token) {
        throw new Error(error?.message || "Falha no login");
      }
      setStoredToken(data.session.access_token);
      const me = await fetchMe();
      setUser(me);
      return;
    }

    const result = await apiLogin(email, password);
    setUser(result.user);
  }, []);

  const logout = useCallback(async () => {
    if (isSupabaseAuthConfigured()) {
      try {
        await getSupabaseBrowserClient().auth.signOut();
      } catch {
        /* ignore */
      }
    }
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
