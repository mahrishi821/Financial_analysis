import api from "@/service/api";

export const documentApi = {
  uploadZip: async (companyId: string, file: File) => {
    const form = new FormData();
    form.append("file", file);
    form.append("company", companyId);
    form.append("company_id", companyId);
    const res = await api.post("/upload-zip/", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
  },
};
