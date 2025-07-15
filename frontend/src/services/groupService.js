export async function fetchPermissoes() {
  const token = localStorage.getItem("accessToken");
  const res = await fetch(`${API_BASE_URL}controle-acesso/permissoes/`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  if (!res.ok) throw new Error("Erro ao buscar permissões");
  return await res.json();
}
import { API_BASE_URL } from "./api";

export async function fetchGrupos() {
  const token = localStorage.getItem("accessToken");
  const res = await fetch(`${API_BASE_URL}controle-acesso/grupos/`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  if (!res.ok) throw new Error("Erro ao buscar grupos");
  return await res.json();
}

export async function createGrupo(data) {
  const token = localStorage.getItem("accessToken");
  const res = await fetch(`${API_BASE_URL}controle-acesso/grupos/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Erro ao criar grupo");
  return await res.json();
}

export async function updateGrupo(id, data) {
  const token = localStorage.getItem("accessToken");
  const res = await fetch(`${API_BASE_URL}controle-acesso/grupos/${id}/`, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Erro ao atualizar grupo");
  return await res.json();
}

export async function deleteGrupo(id) {
  const token = localStorage.getItem("accessToken");
  const res = await fetch(`${API_BASE_URL}controle-acesso/grupos/${id}/`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  if (!res.ok) throw new Error("Erro ao excluir grupo");
  return true;
}
