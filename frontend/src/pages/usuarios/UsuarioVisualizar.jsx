import React, { useEffect, useState } from "react";
import PageContainer from "../../components/ui/PageContainer";
import { useParams, useNavigate } from "react-router-dom";
import { fetchUsuario } from "../../services/userService";
import { useErrorHandler } from "../../hooks/useErrorHandler";
import BadgeStatus from "../../components/ui/BadgeStatus";

export default function UsuarioVisualizar() {
  const { id } = useParams();
  const { showError } = useErrorHandler();
  const [usuario, setUsuario] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchUsuario(id);
        setUsuario(data);
      } catch (err) {
        showError(err);
        navigate("/usuarios");
      }
    }
    load();
  }, [id]);

  if (!usuario) return <PageContainer>Carregando...</PageContainer>;

  return (
    <PageContainer>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-primary">Usuário</h2>
          <div className="flex gap-2 mt-2">
            <BadgeStatus value={usuario.is_active} activeLabel="Ativo" inactiveLabel="Inativo" />
            <BadgeStatus value={usuario.is_online} activeLabel="Online" inactiveLabel="Offline" />
          </div>
        </div>
        <div className="flex gap-2">
          <button
            className="px-4 py-2 rounded bg-success text-white hover:bg-success/90 transition-colors"
            onClick={() => navigate(`/usuarios/${usuario.id}/editar`)}
          >Editar</button>
          <button
            className="px-4 py-2 rounded bg-secondary text-foreground hover:bg-secondary/80 border border-border transition-colors"
            onClick={() => navigate("/usuarios")}
          >Voltar</button>
        </div>
      </div>
      <div className="flex flex-col gap-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <span className="font-heading text-primary">Primeiro nome</span>
            <div className="font-semibold">{usuario.first_name}</div>
          </div>
          <div>
            <span className="font-heading text-primary">Sobrenome</span>
            <div className="font-semibold">{usuario.last_name}</div>
          </div>
          <div>
            <span className="font-heading text-primary">E-mail</span>
            <div className="font-semibold">{usuario.email}</div>
          </div>
          <div>
            <span className="font-heading text-primary">Usuário</span>
            <div className="font-semibold">{usuario.username}</div>
          </div>
          <div>
            <span className="font-heading text-primary">Telefone</span>
            <div className="font-semibold">{usuario.telefone}</div>
          </div>
          <div>
            <span className="font-heading text-primary">Grupos</span>
            <div className="font-semibold">{Array.isArray(usuario.grupos_nomes) ? usuario.grupos_nomes.join(", ") : ""}</div>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div>
            <span className="font-heading text-primary">Cadastrado em</span>
            <div className="font-semibold">{usuario.date_joined ? new Date(usuario.date_joined).toLocaleString() : ""}</div>
          </div>
          <div>
            <span className="font-heading text-primary">Último login</span>
            <div className="font-semibold">{usuario.last_login ? new Date(usuario.last_login).toLocaleString() : "-"}</div>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
