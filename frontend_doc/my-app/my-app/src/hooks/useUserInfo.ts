"use client";

import { useEffect, useMemo, useState } from "react";
import { userApi, type UserInfo } from "@/service/api/user";

export function useUserInfo() {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let canceled = false;
    (async () => {
      try {
        const info = await userApi.getUserInfo();
        if (!canceled) setUser(info);
      } catch (e: any) {
        if (!canceled) setError(e?.message || "Failed to fetch user info");
      } finally {
        if (!canceled) setLoading(false);
      }
    })();
    return () => { canceled = true; };
  }, []);

  const initials = useMemo(() => {
    const name = user?.name?.trim() || "";
    if (!name) return "";
    const parts = name.split(/\s+/);
    const first = parts[0]?.[0];
    const second = parts.length > 1 ? parts[1]?.[0] : "";
    return (first || "" ) + (second || "");
  }, [user]);

  return { user, loading, error, initials };
}

