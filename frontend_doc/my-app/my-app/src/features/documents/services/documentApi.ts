import { http } from "@/lib/fetchClient";

export const documentApi = {
  uploadZip: (companyId: string, file: File) => {
    const form = new FormData();
    form.append("file", file);
    form.append("company", companyId);
    form.append("company_id", companyId);
    return http.postForm("/api/upload-zip/", form);
  },
};
