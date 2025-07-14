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