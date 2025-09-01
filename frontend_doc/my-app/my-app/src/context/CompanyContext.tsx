"use client";
import React, { createContext, useContext, useEffect, useState } from "react";
import type { Company } from "@/types";
import api from "@/service/api";

type CompanyState = {
  companies: Company[];
  refresh: () => Promise<void>;
};

const CompanyContext = createContext<CompanyState>({
  companies: [],
  refresh: async () => {},
});

export const CompanyProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const [companies, setCompanies] = useState<Company[]>([]);

  const refresh = async () => {
    try {
      const res = await api.get<Company[]>("/companies/");
      setCompanies(res.data as any);
    } catch (err) {
      console.error("Error fetching companies", err);
      setCompanies([]);
    }
  };

  useEffect(() => { refresh(); }, []);

  return (
    <CompanyContext.Provider value={{ companies, refresh }}>
      {children}
    </CompanyContext.Provider>
  );
};

export const useCompanies = () => useContext(CompanyContext);
