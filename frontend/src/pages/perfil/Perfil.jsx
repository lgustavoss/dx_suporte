import React, { useState } from "react";
import PageContainer from "../../components/ui/PageContainer";
import Loading from "../../components/ui/Loading";
import ErrorMessage from "../../components/ui/ErrorMessage";
import { usePerfil } from "../../hooks/usePerfil";
import { Button } from "../../components/ui/Button";
import Input from "../../components/form/Input";
import { toast } from "react-toastify";
import BadgeStatus from "../../components/ui/BadgeStatus";
import { updatePerfil } from "../../services/userService";
import { maskTelefone } from "../../utils/mask";

export default function Perfil() {
  const { user, loading } = usePerfil();
  const [edit, setEdit] = useState(false);
  const [form, setForm] = useState(user || {});
  const [saving, setSaving] = useState(false);

  // Atualiza form ao carregar user
  React.useEffect(() => {
    setForm(user || {});
  }, [user]);

  if (loading) return <Loading message="Carregando perfil..." />;
  if (!user) return <ErrorMessage message="Não foi possível carregar o perfil." />;

  function handleChange(e) {
    const { name, value } = e.target;
    let newValue = value;
    if (name === "telefone") {
      newValue = maskTelefone(value);
    }
    setForm((prev) => ({ ...prev, [name]: newValue }));
  }

  async function handleSave(e) {
    e.preventDefault();
    console.log("Chamou handleSave");
    setSaving(true);
    try {
      const payload = {
        first_name: form.first_name,
        last_name: form.last_name,
        email: form.email,
        telefone: form.telefone,
        username: form.username,
      };
      console.log("ID do usuário:", user.id);
      console.log("Payload:", payload);
      await updatePerfil(user.id, payload);
      toast.success("Perfil atualizado com sucesso!");
      setEdit(false);
    } catch (err) {
      toast.error("Erro ao atualizar perfil.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <PageContainer>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-primary">Perfil do Usuário</h2>
          <div className="flex gap-2 mt-2">
            <BadgeStatus value={form.is_active} activeLabel="Ativo" inactiveLabel="Inativo" />
            <BadgeStatus value={form.is_online} activeLabel="Online" inactiveLabel="Offline" />
          </div>
        </div>
        {!edit ? (
          <Button variant="outline" onClick={() => setEdit(true)}>
            Editar
          </Button>
        ) : (
          <div className="flex gap-2">
            <Button variant="success" onClick={handleSave} disabled={saving}>
              {saving ? "Salvando..." : "Salvar"}
            </Button>
            <Button variant="secondary" onClick={() => { setEdit(false); setForm(user); }}>
              Cancelar
            </Button>
          </div>
        )}
      </div>
      <form className="flex flex-col gap-4" onSubmit={handleSave}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Primeiro nome"
            name="first_name"
            value={form.first_name || ""}
            onChange={handleChange}
            disabled={!edit}
            className="rounded-lg"
          />
          <Input
            label="Sobrenome"
            name="last_name"
            value={form.last_name || ""}
            onChange={handleChange}
            disabled={!edit}
            className="rounded-lg"
          />
          <Input
            label="E-mail"
            name="email"
            type="email"
            value={form.email || ""}
            onChange={handleChange}
            disabled={!edit}
            className="rounded-lg"
          />
          <Input
            label="Telefone"
            name="telefone"
            value={form.telefone || ""}
            onChange={handleChange}
            disabled={!edit}
            className="rounded-lg"
          />
          <Input
            label="Usuário"
            name="username"
            value={form.username || ""}
            onChange={handleChange}
            disabled={!edit}
            className="rounded-lg"
          />
          <Input
            label="Grupos"
            name="grupos_nomes"
            value={Array.isArray(form.grupos_nomes) ? form.grupos_nomes.join(", ") : ""}
            disabled
            className="rounded-lg"
          />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <Input
            label="Cadastrado em"
            value={form.date_joined ? new Date(form.date_joined).toLocaleString() : ""}
            disabled
            className="rounded-lg"
          />
          <Input
            label="Último login"
            value={form.last_login ? new Date(form.last_login).toLocaleString() : "-"}
            disabled
            className="rounded-lg"
          />
        </div>
      </form>
    </PageContainer>
  );
}