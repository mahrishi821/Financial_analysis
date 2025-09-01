export type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(url: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE_URL}${url}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    const msg = await res.text().catch(() => res.statusText);
    throw new Error(`HTTP ${res.status}: ${msg}`);
  }
  return res.json() as Promise<T>;
}

export const http = {
  get: <T>(url: string) => request<T>(url),
  post: <TBody, TResp = any>(url: string, body: TBody) =>
    request<TResp>(url, { method: "POST", body: JSON.stringify(body) }),
  postForm: async <TResp = any>(url: string, form: FormData) => {
    const res = await fetch(`${BASE_URL}${url}`, { method: "POST", body: form });
    if (!res.ok) {
      const msg = await res.text().catch(() => res.statusText);
      throw new Error(`HTTP ${res.status}: ${msg}`);
    }
    return res.json() as Promise<TResp>;
  },
};
