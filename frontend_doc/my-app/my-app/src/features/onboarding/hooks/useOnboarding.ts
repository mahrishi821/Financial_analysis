"use client";
import { useState } from "react";
import { onboardingApi, type OnboardingPayload } from "../services/onboardingApi";

export function useOnboarding() {
  const [loading, setLoading] = useState(false);

  const submit = async (payload: OnboardingPayload) => {
    setLoading(true);
    try {
      const res = await onboardingApi.createCompany(payload);
      return res;
    } finally {
      setLoading(false);
    }
  };

  return { submit, loading };
}
