import React, { useState } from "react";
import PageContainer from "../../components/ui/PageContainer";
import { Button } from "../../components/ui/Button";
import Input from "../../components/form/Input";
import { maskTelefone } from "../../utils/mask";
import { useErrorHandler } from "../../hooks/useErrorHandler";

export default function UsuarioForm({ initialData = {}, onSave, onCancel, loading }) {
  const [form, setForm] = useState({
    first_name: initialData.first_name || "",
    last_name: initialData.last_name || "",
    email: initialData.email || "",
    telefone: initialData.telefone || "",
    username: initialData.username || "",
    is_active: initialData.is_active ?? true,
  });
  const { showError } = useErrorHandler();

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    let newValue = value;
    if (name === "telefone") newValue = maskTelefone(value);
    if (type === "checkbox") newValue = checked;
    setForm((prev) => ({ ...prev, [name]: newValue }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      await onSave(form);
    } catch (err) {
      showError(err);
    }
  }

  return (
    <PageContainer>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input label="Primeiro nome" name="first_name" value={form.first_name} onChange={handleChange} required />
          <Input label="Sobrenome" name="last_name" value={form.last_name} onChange={handleChange} required />
          <Input label="E-mail" name="email" value={form.email} onChange={handleChange} type="email" required />
          <Input label="Usuário" name="username" value={form.username} onChange={handleChange} required />
          <Input label="Telefone" name="telefone" value={form.telefone} onChange={handleChange} />
          <label className="flex items-center gap-2 mt-2">
            <input type="checkbox" name="is_active" checked={form.is_active} onChange={handleChange} /> Ativo
          </label>
        </div>
        <div className="flex gap-2 mt-4">
          <Button type="submit" variant="success" disabled={loading}>Salvar</Button>
          <Button type="button" variant="secondary" onClick={onCancel}>Cancelar</Button>
        </div>
      </form>
    </PageContainer>
  );
}
