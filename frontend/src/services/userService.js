import { API_BASE_URL } from "./api";

export async function fetchPerfil() {
  const token = localStorage.getItem("accessToken");
  const res = await fetch(`${API_BASE_URL}auth/usuarios/me/`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  if (!res.ok) throw new Error("Erro ao buscar perfil");
  return await res.json();
}