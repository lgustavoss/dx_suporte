import { API_BASE_URL } from "../services/api";
import { useState } from "react";
import { validateEmail } from "../utils/validators";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

export function useLoginForm() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [emailValid, setEmailValid] = useState(true);
  const [emailTouched, setEmailTouched] = useState(false); // novo estado
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));

    if (name === "email") {
      setEmailValid(validateEmail(value) || value === "");
    }
  }

  function handleBlur(e) {
    if (e.target.name === "email") {
      setEmailTouched(true);
      setEmailValid(validateEmail(form.email) || form.email === "");
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}auth/login/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || data.message || "Usuário ou senha inválidos.");
      }

      const data = await response.json();
      localStorage.setItem("accessToken", data.access);
      localStorage.setItem("refreshToken", data.refresh);
      localStorage.setItem("user", JSON.stringify(data.user));
      navigate("/dashboard");
      // toast.success("Login realizado com sucesso!"); // opcional
    } catch (err) {
      setError(err.message || "Erro ao realizar login.");
      toast.error(err.message || "Erro ao realizar login.");
    } finally {
      setLoading(false);
    }
  }

  return {
    form,
    emailValid,
    emailTouched,
    handleChange,
    handleBlur,
    handleSubmit,
    loading,
    error,
  };
}