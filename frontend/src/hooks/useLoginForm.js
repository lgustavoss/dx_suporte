import { API_BASE_URL } from "../services/api";
import { useState } from "react";
import { validateEmail } from "../utils/validators";
import { useNavigate } from "react-router-dom";
import { useErrorHandler } from "../hooks/useErrorHandler";

export function useLoginForm() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [emailValid, setEmailValid] = useState(true);
  const [emailTouched, setEmailTouched] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { showError } = useErrorHandler();

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
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}auth/login/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      if (!response.ok) {
        throw new Error("Usuário ou senha inválidos.");
      }

      const data = await response.json();
      localStorage.setItem("accessToken", data.access);
      localStorage.setItem("refreshToken", data.refresh);
      localStorage.setItem("user", JSON.stringify(data.user));
      navigate("/dashboard");
    } catch (err) {
      showError(err);
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
  };
}