import axios from "axios";

const api = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const raw = localStorage.getItem("auth-storage");
  if (raw) {
    try {
      const parsed = JSON.parse(raw);
      const token = parsed?.state?.token;
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch {
      // ignore
    }
  }
  return config;
});

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value: unknown) => void;
  reject: (reason?: unknown) => void;
}> = [];

function processQueue(error: unknown, token: string | null = null) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token);
    }
  });
  failedQueue = [];
}

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const originalRequest = err.config;

    if (err.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const raw = localStorage.getItem("auth-storage");
      let refreshToken: string | null = null;
      if (raw) {
        try {
          refreshToken = JSON.parse(raw)?.state?.refreshToken ?? null;
        } catch {
          // ignore
        }
      }

      if (!refreshToken) {
        localStorage.removeItem("auth-storage");
        window.location.href = "/login";
        return Promise.reject(err);
      }

      try {
        const refreshResp = await axios.post("/api/v1/auth/refresh", {
          refresh_token: refreshToken,
        });
        const newAccessToken: string = refreshResp.data.access_token;

        const raw2 = localStorage.getItem("auth-storage");
        if (raw2) {
          try {
            const parsed = JSON.parse(raw2);
            parsed.state.token = newAccessToken;
            localStorage.setItem("auth-storage", JSON.stringify(parsed));
          } catch {
            // ignore
          }
        }

        api.defaults.headers.common.Authorization = `Bearer ${newAccessToken}`;
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        processQueue(null, newAccessToken);
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        localStorage.removeItem("auth-storage");
        window.location.href = "/login";
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(err);
  }
);

export default api;
