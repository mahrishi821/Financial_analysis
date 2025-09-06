"use client";

import { useEffect, useState } from "react";
import { dashboardApi, type DashboardMetrics } from "../services/dashboardApi";

export function useDashboardMetrics() {
  const [data, setData] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let canceled = false;
    (async () => {
      try {
        const metrics = await dashboardApi.getAllMetrics();
        if (!canceled) setData(metrics);
      } catch (e: any) {
        if (!canceled) setError(e?.message || "Failed to load dashboard metrics");
      } finally {
        if (!canceled) setLoading(false);
      }
    })();
    return () => {
      canceled = true;
    };
  }, []);

  return { data, loading, error };
}

