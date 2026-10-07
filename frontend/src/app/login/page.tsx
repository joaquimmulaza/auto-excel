"use client";

import React, { useState } from "react";
import Image from "next/image";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertCircle, LogIn } from "lucide-react";

/** Local AUTH_MODE fixtures (FastAPI). Supabase seeds use *@cotarco.ao below when configured. */
const LOCAL_DEMO_ACCOUNTS = [
  { email: "joaquim.silva@cotarco.ao", password: "comercial123", label: "Comercial" },
  { email: "antonio.ferreira@cotarco.ao", password: "operador123", label: "Operador" },
  { email: "admin@cotarco.ao", password: "admin123", label: "Admin" },
];

const SUPABASE_DEMO_ACCOUNTS = [
  { email: "comercial@cotarco.ao", password: "ComercialTest123!", label: "Comercial" },
  { email: "operador@cotarco.ao", password: "OperadorTest123!", label: "Operador" },
  { email: "admin@cotarco.ao", password: "AdminTest123!", label: "Admin" },
];

const DEMO_ACCOUNTS =
  typeof process !== "undefined" &&
  process.env.NEXT_PUBLIC_SUPABASE_URL &&
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
    ? SUPABASE_DEMO_ACCOUNTS
    : LOCAL_DEMO_ACCOUNTS;

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState(DEMO_ACCOUNTS[0].email);
  const [password, setPassword] = useState(DEMO_ACCOUNTS[0].password);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setPending(true);
    setError(null);
    try {
      await login(email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha no login");
      setPending(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-3.5rem)] flex items-center justify-center px-4 py-12 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-brand-subtle via-canvas to-canvas">
      <Card className="w-full max-w-md shadow-sm">
        <CardHeader className="space-y-4 text-center">
          <div className="flex justify-center">
            <Image
              src="/cotarco-logo.png"
              alt="Cotarco"
              width={140}
              height={42}
              className="h-10 w-auto object-contain"
              priority
              unoptimized
            />
          </div>
          <CardTitle className="text-lg">Commercial Manager</CardTitle>
          <p className="text-xs text-slateSecondary">
            Autentique-se para validar e aprovar tabelas de preços e stock.
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-ink">Email</label>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="username"
                required
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-ink">Password</label>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                required
              />
            </div>
            {error && (
              <div className="flex items-center gap-2 text-xs text-error bg-red-50 border border-red-200 rounded p-2">
                <AlertCircle className="h-3.5 w-3.5 shrink-0" />
                {error}
              </div>
            )}
            <Button type="submit" disabled={pending} className="w-full gap-2 font-bold">
              {pending ? (
                <span className="h-4 w-4 rounded-full border-2 border-white border-t-transparent animate-spin" />
              ) : (
                <LogIn className="h-4 w-4" />
              )}
              Entrar
            </Button>
          </form>

          <div className="mt-6 pt-4 border-t border-border space-y-2">
            <p className="text-[11px] font-semibold text-slateSecondary uppercase tracking-wider">
              Contas de demonstração
            </p>
            <div className="flex flex-wrap gap-2">
              {DEMO_ACCOUNTS.map((acc) => (
                <button
                  key={acc.email}
                  type="button"
                  className="text-[11px] px-2 py-1 rounded border border-border bg-canvas hover:bg-surface text-ink"
                  onClick={() => {
                    setEmail(acc.email);
                    setPassword(acc.password);
                  }}
                >
                  {acc.label}
                </button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
