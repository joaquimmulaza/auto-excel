"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { CurrentUser, UserRole } from "@/types";

interface AuthContextType {
  user: CurrentUser;
  setRole: (role: UserRole) => void;
  isOperador: boolean;
  isComercial: boolean;
  isAdmin: boolean;
  canApprove: boolean;
}

const PRESET_USERS: Record<UserRole, CurrentUser> = {
  COMERCIAL: {
    id: "00000000-0000-0000-0000-000000000001",
    name: "Joaquim Silva",
    email: "joaquim.silva@cotarco.ao",
    role: "COMERCIAL",
  },
  OPERADOR: {
    id: "00000000-0000-0000-0000-000000000002",
    name: "António Ferreira",
    email: "antonio.ferreira@cotarco.ao",
    role: "OPERADOR",
  },
  ADMIN: {
    id: "00000000-0000-0000-0000-000000000003",
    name: "Administrador Geral",
    email: "admin@cotarco.ao",
    role: "ADMIN",
  },
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [role, setRoleState] = useState<UserRole>("COMERCIAL");

  useEffect(() => {
    const saved = localStorage.getItem("ccm_active_role") as UserRole | null;
    if (saved && PRESET_USERS[saved]) {
      setRoleState(saved);
    }
  }, []);

  const setRole = (newRole: UserRole) => {
    setRoleState(newRole);
    localStorage.setItem("ccm_active_role", newRole);
  };

  const user = PRESET_USERS[role];
  const isOperador = role === "OPERADOR";
  const isComercial = role === "COMERCIAL";
  const isAdmin = role === "ADMIN";
  const canApprove = isOperador || isAdmin;

  return (
    <AuthContext.Provider
      value={{
        user,
        setRole,
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
