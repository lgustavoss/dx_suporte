import React, { useEffect, useState } from "react";
import PageContainer from "../../components/ui/PageContainer";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { maskTelefone } from "../../utils/mask";
import { useErrorHandler } from "../../hooks/useErrorHandler";
import { useNavigate, useParams } from "react-router-dom";
import { updateUsuario, fetchUsuario } from "../../services/userService";

export default function UsuarioEditar() {
  const { id } = useParams();
  const { showError } = useErrorHandler();
  const [form, setForm] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    async function load() {
      try {
        const usuario = await fetchUsuario(id);
        setForm({ ...usuario });
      } catch (err) {
        showError(err);
        navigate("/usuarios");
      }
    }
    load();
  }, [id]);

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    let newValue = value;
    if (name === "telefone") newValue = maskTelefone(value);
    if (type === "checkbox") newValue = checked;
    setForm((prev) => {
      const updated = { ...prev, [name]: newValue };
      console.log("form", updated);
      return updated;
    });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    try {
      // Só envia ao backend ao clicar em salvar
      await updateUsuario(id, form);
      navigate("/usuarios");
    } catch (err) {
      showError(err);
    } finally {
      setLoading(false);
    }
  }

  if (!form) return <PageContainer>Carregando...</PageContainer>;

  return (
    <PageContainer>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4 max-w-xl mx-auto">
        <h2 className="text-2xl font-bold text-primary mb-4">Editar Usuário</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="first_name" className="block mb-1 font-heading text-primary">Primeiro nome</label>
            <input
              id="first_name"
              name="first_name"
              value={String(form.first_name || "")}
              onChange={handleChange}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-base ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            />
          </div>
          <div>
            <label htmlFor="last_name" className="block mb-1 font-heading text-primary">Sobrenome</label>
            <Input id="last_name" name="last_name" value={String(form.last_name || "")} onChange={handleChange} />
          </div>
          <div>
            <label htmlFor="email" className="block mb-1 font-heading text-primary">E-mail</label>
            <Input id="email" name="email" value={String(form.email || "")} onChange={handleChange} type="email" />
          </div>
          <div>
            <label htmlFor="username" className="block mb-1 font-heading text-primary">Usuário</label>
            <Input id="username" name="username" value={String(form.username || "")} onChange={handleChange} />
          </div>
          <div>
            <label htmlFor="telefone" className="block mb-1 font-heading text-primary">Telefone</label>
            <Input id="telefone" name="telefone" value={String(form.telefone || "")} onChange={handleChange} />
          </div>
          <div className="flex items-center gap-2 mt-2">
            <input type="checkbox" id="is_active" name="is_active" checked={form.is_active} onChange={handleChange} />
            <label htmlFor="is_active" className="font-heading text-primary">Ativo</label>
          </div>
        </div>
        <div className="flex gap-2 mt-4">
          <Button type="submit" variant="success" loading={loading}>Salvar</Button>
          <Button type="button" variant="secondary" onClick={() => navigate("/usuarios")}>Cancelar</Button>
        </div>
      </form>
    </PageContainer>
  );
}
