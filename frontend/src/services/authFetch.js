import { API_BASE_URL } from "./api";

export async function authFetch(endpoint, options = {}) {
  const accessToken = localStorage.getItem("accessToken");
  const headers = {
    ...(options.headers || {}),
    Authorization: accessToken ? `Bearer ${accessToken}` : undefined,
    "Content-Type": "application/json",
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  return response;
}