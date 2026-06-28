import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = typeof window !== "undefined"
    ? localStorage.getItem("access_token")
    : null;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refreshToken = localStorage.getItem("refresh_token");
      if (refreshToken) {
        try {
          const { data } = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          localStorage.setItem("access_token", data.access_token);
          original.headers.Authorization = `Bearer ${data.access_token}`;
          return api(original);
        } catch {
          localStorage.clear();
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  register: (email: string, password: string) =>
    api.post("/auth/register", { email, password }),
  login: (email: string, password: string) =>
    api.post("/auth/login", { email, password }),
  refresh: (refresh_token: string) =>
    api.post("/auth/refresh", { refresh_token }),
  me: () => api.get("/auth/me"),
  exportWallet: (password: string) =>
    api.post("/auth/wallet/export", { password }),
};

export const investigationsApi = {
  create: (protocol_name: string) =>
    api.post("/investigations", { protocol_name }),
  list: () => api.get("/investigations"),
  get: (id: string) => api.get(`/investigations/${id}`),
  getReport: (id: string) => api.get(`/reports/${id}`),
};

export function createSSEConnection(investigationId: string): EventSource {
  const token = localStorage.getItem("access_token");
  return new EventSource(
    `${API_URL}/investigations/${investigationId}/stream?token=${token}`
  );
}
