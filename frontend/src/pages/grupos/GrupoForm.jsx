import React, { useState } from "react";
import { Button } from "../../components/ui/Button";
import Input from "../../components/form/Input";
import { useErrorHandler } from "../../hooks/useErrorHandler";

export default function GrupoForm({ onSave, onCancel, loading }) {
  const [form, setForm] = useState({
    nome: "",
    descricao: "",
    ativo: true,
  });
  const { showError } = useErrorHandler();

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({ ...prev, [name]: type === "checkbox" ? checked : value }));
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
    <form onSubmit={handleSubmit} className="flex flex-col gap-4 min-w-[300px]">
      <Input
        label="Nome do grupo"
        name="nome"
        value={form.nome}
        onChange={handleChange}
        required
      />
      <Input
        label="Descrição"
        name="descricao"
        value={form.descricao}
        onChange={handleChange}
      />
      <label className="flex items-center gap-2">
        <input
          type="checkbox"
          name="ativo"
          checked={form.ativo}
          onChange={handleChange}
        />
        Ativo
      </label>
      <div className="flex gap-2 mt-2">
        <Button type="submit" variant="success" disabled={loading}>Salvar</Button>
        <Button type="button" variant="secondary" onClick={onCancel}>Cancelar</Button>
      </div>
    </form>
  );
}
