"use client";
import React, { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getTokens, setTokens, clearTokens } from "@/service/storage";
import Cookies from "js-cookie";

type AuthContextType = {
  access: string | null;
  refresh: string | null;
  login: (tokens: { access: string; refresh: string }) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [access, setAccess] = useState<string | null>(null);
  const [refresh, setRefresh] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const saved = getTokens();
    if (saved) {
      setAccess(saved.access);
      setRefresh(saved.refresh);
    }
  }, []);

  const login = (tokens: { access: string; refresh: string }) => {
    setTokens(tokens);
    setAccess(tokens.access);

    const isProd = process.env.NODE_ENV === "production";
    Cookies.set("access_token", tokens.access, {
      secure: isProd,
      sameSite: isProd ? "strict" : "lax",
      path: "/",
    });
    Cookies.set("refresh_token", tokens.refresh, {
      secure: isProd,
      sameSite: isProd ? "strict" : "lax",
      path: "/",
    });

    setRefresh(tokens.refresh);
    router.push("/dashboard");
  };

  const logout = () => {
    clearTokens();
    Cookies.remove("access_token");
    Cookies.remove("refresh_token");
    setAccess(null);
    setRefresh(null);
    router.push("/auth/login");
  };

  return (
    <AuthContext.Provider value={{ access, refresh, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuthContext = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuthContext must be used within AuthProvider");
  return context;
};
