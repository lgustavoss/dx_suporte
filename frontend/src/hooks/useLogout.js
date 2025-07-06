import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authFetch } from "../services/authFetch";

export function useLogout() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function logout() {
    setLoading(true);
    try {
      await authFetch("auth/logout/", { method: "POST" });
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
      localStorage.removeItem("user");
      navigate("/");
    } catch (err) {
      alert("Erro ao fazer logout.");
    } finally {
      setLoading(false);
    }
  }

  return { logout, loading };
}