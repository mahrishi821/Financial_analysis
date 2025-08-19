"use client";
import { useState } from "react";
import { documentApi } from "../services/documentApi";

export function useFileUpload() {
  const [loading, setLoading] = useState(false);

  const uploadZip = async (companyId: string, file: File) => {
    setLoading(true);
    try {
      const res = await documentApi.uploadZip(companyId, file);
      return res;
    } finally {
      setLoading(false);
    }
  };

  return { uploadZip, loading };
}
