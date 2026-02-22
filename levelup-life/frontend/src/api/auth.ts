import api from "./client";

interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: unknown;
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  const res = await api.post<AuthResponse>("/auth/login", { email, password });
  return res.data;
}

export async function register(
  email: string,
  username: string,
  password: string
): Promise<AuthResponse> {
  const res = await api.post<AuthResponse>("/auth/register", { email, username, password });
  return res.data;
}
