import React, { useState } from "react";
import PageContainer from "../../components/ui/PageContainer";
import { Button } from "../../components/ui/Button";
import Input from "../../components/form/Input";
import { maskTelefone } from "../../utils/mask";
import { useErrorHandler } from "../../hooks/useErrorHandler";
import { createUsuario } from "../../services/userService";
import { useNavigate } from "react-router-dom";

export default function UsuarioNovo() {
  const { showError } = useErrorHandler();
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    telefone: "",
    username: "",
    password: "",
    is_active: true,
  });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    let newValue = value;
    if (name === "telefone") newValue = maskTelefone(value);
    if (type === "checkbox") newValue = checked;
    setForm((prev) => ({ ...prev, [name]: newValue }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    try {
      await createUsuario(form);
      navigate("/usuarios");
    } catch (err) {
      showError(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <PageContainer>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4 max-w-xl mx-auto">
        <h2 className="text-2xl font-bold text-primary mb-4">Novo Usuário</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input label="Primeiro nome" name="first_name" value={form.first_name} onChange={handleChange} required />
          <Input label="Sobrenome" name="last_name" value={form.last_name} onChange={handleChange} required />
          <Input label="E-mail" name="email" value={form.email} onChange={handleChange} type="email" required />
          <Input label="Usuário" name="username" value={form.username} onChange={handleChange} required />
          <Input label="Telefone" name="telefone" value={form.telefone} onChange={handleChange} />
          <Input label="Senha" name="password" value={form.password} onChange={handleChange} type="password" required />
          <label className="flex items-center gap-2 mt-2">
            <input type="checkbox" name="is_active" checked={form.is_active} onChange={handleChange} /> Ativo
          </label>
        </div>
        <div className="flex gap-2 mt-4">
          <Button type="submit" variant="success" loading={loading}>Salvar</Button>
          <Button type="button" variant="secondary" onClick={() => navigate("/usuarios")}>Cancelar</Button>
        </div>
      </form>
    </PageContainer>
  );
}
