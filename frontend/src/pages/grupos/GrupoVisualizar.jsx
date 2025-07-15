import React, { useEffect, useState } from "react";
import BadgeStatus from "../../components/ui/BadgeStatus";
import PageContainer from "../../components/ui/PageContainer";
import { useParams, useNavigate } from "react-router-dom";
import { useErrorHandler } from "../../hooks/useErrorHandler";
import { API_BASE_URL } from "../../services/api";
import { Button } from "../../components/ui/Button";
import { fetchPermissoesGrupo, fetchPermissoes } from "../../services/groupService";

export default function GrupoVisualizar() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { showError } = useErrorHandler();
  const [grupo, setGrupo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [aba, setAba] = useState("permissoes");
  const [permissoes, setPermissoes] = useState([]); // todas as permissões possíveis
  const [permsByModulo, setPermsByModulo] = useState({}); // agrupamento de todas as permissões
  const [openModulo, setOpenModulo] = useState({});

  useEffect(() => {
    async function fetchGrupoEPermissoes() {
      setLoading(true);
      try {
        const token = localStorage.getItem("accessToken");
        // Busca dados do grupo
        const res = await fetch(`${API_BASE_URL}controle-acesso/grupos/${id}/`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error("Erro ao buscar grupo");
        const data = await res.json();
        setGrupo(data);
        // Busca todas as permissões possíveis
        const todasPerms = await fetchPermissoes();
        const perms = Array.isArray(todasPerms) ? todasPerms : todasPerms.results || [];
        setPermissoes(perms);
        // Busca permissões ativas do grupo
        const permsData = await fetchPermissoesGrupo(id);
        const ativas = Array.isArray(permsData.permissions) ? permsData.permissions.map(p => p.id) : [];
        // Agrupa todas as permissões por módulo
        const agrupado = {};
        perms.forEach((p) => {
          const modulo = p.modulo_display || p.modulo || 'Outros';
          if (!agrupado[modulo]) agrupado[modulo] = [];
          agrupado[modulo].push({ ...p, ativa: ativas.includes(p.id) });
        });
        setPermsByModulo(agrupado);
        // Abre todos os módulos por padrão (fechado)
        const openDefault = {};
        Object.keys(agrupado).forEach((m) => (openDefault[m] = false));
        setOpenModulo(openDefault);
      } catch (err) {
        showError(err);
      } finally {
        setLoading(false);
      }
    }
    fetchGrupoEPermissoes();
  }, [id]);

  if (loading) return <PageContainer>Carregando...</PageContainer>;
  if (!grupo) return <PageContainer>Grupo não encontrado.</PageContainer>;

  return (
    <PageContainer>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-primary mb-1">Detalhes do Grupo {grupo.name || grupo.nome}</h2>
          {grupo.descricao && (
            <div className="text-base text-muted-foreground mb-2">{grupo.descricao}</div>
          )}
          <BadgeStatus value={grupo.ativo ?? grupo.group?.ativo} activeLabel="Ativo" inactiveLabel="Inativo" />
        </div>
        <div className="flex gap-2 h-fit">
          <Button variant="success" onClick={() => navigate(`/grupos/${grupo.id}/editar`)}>Editar</Button>
          <Button variant="secondary" onClick={() => navigate("/grupos")}>Voltar</Button>
        </div>
      </div>

      <div className="flex gap-4 border-b border-border mb-6">
        <button
          type="button"
          className={`py-2 px-4 -mb-px border-b-2 transition-colors ${aba === "permissoes" ? "border-primary text-primary font-bold" : "border-transparent text-muted-foreground"}`}
          onClick={() => setAba("permissoes")}
        >Permissões</button>
        <button
          type="button"
          className={`py-2 px-4 -mb-px border-b-2 transition-colors ${aba === "usuarios" ? "border-primary text-primary font-bold" : "border-transparent text-muted-foreground"}`}
          onClick={() => setAba("usuarios")}
        >Usuários</button>
      </div>

      {aba === "permissoes" && (
        <div className="mb-6">
          <h3 className="text-lg font-bold text-primary mb-4">Permissões</h3>
          {Object.keys(permsByModulo).length > 0 ? (
            Object.keys(permsByModulo).sort().map((modulo) => {
              let moduloLabel = modulo;
              if (modulo.toLowerCase().includes("account")) moduloLabel = "Usuários";
              if (modulo.toLowerCase().includes("controle")) moduloLabel = "Controle de Acesso";
              // Oculta permissão redundante de gerenciar usuários
              const permsModulo = permsByModulo[modulo].filter((p) => p.label !== 'Permite gerenciar usuários.' && p.label !== 'Permite gerenciar grupos.');
              return (
                <div key={modulo} className="mb-3 border-b last:border-b-0 pb-2">
                  <button
                    type="button"
                    className="flex items-center gap-2 font-bold text-primary mb-1 hover:underline"
                    onClick={() => setOpenModulo((prev) => ({ ...prev, [modulo]: !prev[modulo] }))}
                  >
                    <span>{openModulo[modulo] ? "▼" : "►"}</span>
                    {moduloLabel}
                    <span className="ml-2 text-xs font-normal text-muted-foreground">({permsModulo.length})</span>
                  </button>
                  {openModulo[modulo] && (
                    <div className="pl-6 flex flex-col gap-2">
                      {permsModulo.map((p) => (
                        <div key={p.id} className="flex items-center gap-3 p-2 rounded bg-muted/50 transition select-none border border-transparent">
                          <span className="switch">
                            <input
                              type="checkbox"
                              checked={!!p.ativa}
                              disabled
                              readOnly
                            />
                            <span className="slider round"></span>
                          </span>
                          <div className="flex flex-col">
                            <span className="font-medium text-base text-primary">{p.label}</span>
                            <span className="text-xs text-muted-foreground font-mono mt-1">{p.codename}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })
          ) : (
            <div className="text-muted-foreground">Nenhuma permissão encontrada.</div>
          )}
        </div>
      )}

      {aba === "usuarios" && (
        <div>
          <h3 className="text-lg font-bold text-primary mb-2">Usuários</h3>
          {Array.isArray(grupo.usuarios) && grupo.usuarios.length > 0 ? (
            <ul className="list-disc ml-6">
              {grupo.usuarios.map((u) => (
                <li key={u.id}>
                  <span className="font-medium">{u.full_name || `${u.first_name} ${u.last_name}` || u.username}</span>
                  {u.email && <span className="text-xs text-muted-foreground ml-2">({u.email})</span>}
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-muted-foreground">Nenhum usuário neste grupo.</div>
          )}
        </div>
      )}
    </PageContainer>
  );
}
