import axios from "axios";
import { getTokens, setTokens, clearTokens } from "@/service/storage";

const API_URL = "http://localhost:8000/api";

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  withCredentials: true, // allow sending/receiving cookies (CORS must allow credentials)
});

// Attach access token to requests
api.interceptors.request.use(
  (config) => {
    const tokens = getTokens();
    if (tokens?.access) {
      config.headers["Authorization"] = `Bearer ${tokens.access}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

let isRefreshing = false;
let failedQueue: any[] = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers["Authorization"] = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const tokens = getTokens();
        if (!tokens?.refresh) throw new Error("No refresh token available");

        // Call your refresh endpoint
        const res = await axios.post(`${API_URL}/token/refresh/`, {
          refresh: tokens.refresh,
        });

        const newTokens = {
          access: res.data.access,
          refresh: res.data.refresh,
        };

        setTokens(newTokens);
        api.defaults.headers.common["Authorization"] = `Bearer ${newTokens.access}`;
        processQueue(null, newTokens.access);

        return api(originalRequest);
      } catch (err) {
        processQueue(err, null);
        clearTokens();
        window.location.href = "/auth/login"; // Force logout
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
