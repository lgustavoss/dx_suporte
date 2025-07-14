// Função GET para buscar usuário por ID
export async function fetchUsuario(id) {
  const token = localStorage.getItem("accessToken");
  const res = await fetch(`${API_BASE_URL}auth/usuarios/${id}/`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  if (!res.ok) throw new Error("Erro ao buscar usuário");
  return await res.json();
}
// Função POST para criar usuário
export async function createUsuario(data) {
  const token = localStorage.getItem("accessToken");
  const res = await fetch(`${API_BASE_URL}auth/usuarios/`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Erro ao criar usuário");
  return await res.json();
}

// Função PATCH para editar usuário
export async function updateUsuario(id, data) {
  const token = localStorage.getItem("accessToken");
  const res = await fetch(`${API_BASE_URL}auth/usuarios/${id}/`, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    let msg = "Erro ao atualizar usuário";
    try {
      const errData = await res.json();
      if (typeof errData === "object" && errData !== null) {
        // Pega a primeira mensagem de erro do backend
        const firstKey = Object.keys(errData)[0];
        if (firstKey && Array.isArray(errData[firstKey])) {
          msg = `${firstKey}: ${errData[firstKey][0]}`;
        } else if (typeof errData[firstKey] === "string") {
          msg = `${firstKey}: ${errData[firstKey]}`;
        }
      }
    } catch {}
    throw new Error(msg);
  }
  return await res.json();
}

// Função DELETE para excluir usuário
export async function deleteUsuario(id) {
  const token = localStorage.getItem("accessToken");
  const res = await fetch(`${API_BASE_URL}auth/usuarios/${id}/`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  if (!res.ok) throw new Error("Erro ao excluir usuário");
  return true;
}
// Função GET para listar usuários (ativos ou todos)
export async function fetchUsuarios({ includeInactive = false } = {}) {
  const token = localStorage.getItem("accessToken");
  let url = `${API_BASE_URL}auth/usuarios/`;
  if (includeInactive) {
    url += "?include_inactive=true";
  }
  const res = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  if (!res.ok) throw new Error("Erro ao buscar usuários");
  return await res.json();
}
import { API_BASE_URL } from "./api";


// Função POST para login
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

// Função PATCH para atualizar perfil
export async function updatePerfil(id, data) {
  const token = localStorage.getItem("accessToken");
  console.log("API_BASE_URL:", API_BASE_URL);
  console.log("URL:", `${API_BASE_URL}auth/usuarios/${id}/`);
  console.log("Token:", token);
  console.log("Token antes do PATCH:", token);
  if (!token) {
    // Retorna um erro se o token não estiver presente
    throw new Error("Você não está autenticado. Faça login novamente.");
  }
  try {
    const res = await fetch(`${API_BASE_URL}auth/usuarios/${id}/`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const errorText = await res.text();
      console.error("Erro na resposta:", errorText);
      throw new Error("Erro ao atualizar perfil");
    }
    return await res.json();
  } catch (err) {
    console.error("Erro no fetch:", err);
    throw err;
  }
}