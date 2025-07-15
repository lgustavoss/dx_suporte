import React, { useState, useEffect } from "react";
import PageContainer from "../../components/ui/PageContainer";
import { Button } from "../../components/ui/Button";
import Input from "../../components/form/Input";
import "../../styles/Switch.css";
import { useErrorHandler } from "../../hooks/useErrorHandler";
import { createGrupo, fetchPermissoes } from "../../services/groupService";
import { useNavigate } from "react-router-dom";

export default function GrupoNovo() {
  const { showError } = useErrorHandler();
  const [form, setForm] = useState({ nome: "", descricao: "", ativo: true, permissoes: [] });
  const [permissoes, setPermissoes] = useState([]);
  const [permsByModulo, setPermsByModulo] = useState({});
  const [openModulo, setOpenModulo] = useState({});
  const [search, setSearch] = useState("");
  const [aba, setAba] = useState("dados");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    async function loadPerms() {
      try {
        const data = await fetchPermissoes();
        const perms = Array.isArray(data) ? data : data.results || [];
        setPermissoes(perms);
        // Agrupa por módulo/content_type/modulo_display
        const agrupado = {};
        perms.forEach((p) => {
          // Agrupa por 'modulo' (backend customizado), se não existir, usa 'Outros'
          const modulo = p.modulo_display || p.modulo || 'Outros';
          if (!agrupado[modulo]) agrupado[modulo] = [];
          agrupado[modulo].push(p);
        });
        setPermsByModulo(agrupado);
        // Abre todos os módulos por padrão
        const openDefault = {};
        Object.keys(agrupado).forEach((m) => (openDefault[m] = false));
        setOpenModulo(openDefault);
      } catch (err) {
        showError(err);
      }
    }
    loadPerms();
  }, []);

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    if (name === "permissoes") {
      const id = parseInt(value);
      setForm((prev) => ({
        ...prev,
        permissoes: checked
          ? [...prev.permissoes, id]
          : prev.permissoes.filter((pid) => pid !== id),
      }));
    } else {
      setForm((prev) => ({ ...prev, [name]: type === "checkbox" ? checked : value }));
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    try {
      const grupo = await createGrupo({
        group_data: { name: form.nome },
        descricao: form.descricao,
        ativo: form.ativo,
      });
      // Adiciona permissões ao grupo
      for (const permId of form.permissoes) {
        await fetch(`/api/v1/controle-acesso/grupos/${grupo.id}/permissoes/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
          },
          body: JSON.stringify({ permission_id: permId }),
        });
      }
      navigate("/grupos");
    } catch (err) {
      showError(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <PageContainer>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4 max-w-xl mx-auto">
        <h2 className="text-2xl font-bold text-primary mb-4">Novo Grupo</h2>
        <div className="flex gap-4 border-b border-border mb-4">
          <button
            type="button"
            className={`py-2 px-4 -mb-px border-b-2 transition-colors ${aba === "dados" ? "border-primary text-primary font-bold" : "border-transparent text-muted-foreground"}`}
            onClick={() => setAba("dados")}
          >Dados</button>
          <button
            type="button"
            className={`py-2 px-4 -mb-px border-b-2 transition-colors ${aba === "permissoes" ? "border-primary text-primary font-bold" : "border-transparent text-muted-foreground"}`}
            onClick={() => setAba("permissoes")}
          >Permissões</button>
        </div>
        {aba === "dados" && (
          <>
            <Input label="Nome do grupo" name="nome" value={form.nome} onChange={handleChange} required />
            <Input label="Descrição" name="descricao" value={form.descricao} onChange={handleChange} />
            <div className="flex items-center gap-3 mb-2">
              <span className="font-medium">Ativo</span>
              <label className="switch">
                <input
                  type="checkbox"
                  name="ativo"
                  checked={form.ativo}
                  onChange={handleChange}
                />
                <span className="slider round"></span>
              </label>
            </div>
          </>
        )}
        {aba === "permissoes" && (
          <div>
            <div className="font-semibold mb-2">Permissões do grupo</div>
            <input
              type="text"
              placeholder="Buscar permissão..."
              className="mb-3 w-full border rounded px-3 py-2 text-base"
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
            <div className="border rounded p-2 bg-muted/30">
              {Object.keys(permsByModulo).sort().map((modulo) => {
                // Exibe nome amigável do módulo
                let moduloLabel = modulo;
                if (modulo.toLowerCase().includes("account")) moduloLabel = "Usuários";
                if (modulo.toLowerCase().includes("controle")) moduloLabel = "Controle de Acesso";
                const permsModulo = permsByModulo[modulo].filter((p) => {
                  const termo = search.toLowerCase();
                  return (
                    (p.name || p.nome || "").toLowerCase().includes(termo) ||
                    (p.codename || "").toLowerCase().includes(termo)
                  );
                });
                if (permsModulo.length === 0) return null;
                const allChecked = permsModulo.every((p) => form.permissoes.includes(p.id));
                const someChecked = permsModulo.some((p) => form.permissoes.includes(p.id));
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
                      <div className="pl-6">
                        <label className="flex items-center gap-3 mb-2 cursor-pointer select-none">
                          <span className="switch">
                            <input
                              type="checkbox"
                              checked={allChecked}
                              onChange={e => {
                                if (e.target.checked) {
                                  setForm((prev) => ({
                                    ...prev,
                                    permissoes: [
                                      ...prev.permissoes,
                                      ...permsModulo.filter((p) => !prev.permissoes.includes(p.id)).map((p) => p.id)
                                    ]
                                  }));
                                } else {
                                  setForm((prev) => ({
                                    ...prev,
                                    permissoes: prev.permissoes.filter((pid) => !permsModulo.map((p) => p.id).includes(pid))
                                  }));
                                }
                              }}
                            />
                            <span className="slider round"></span>
                          </span>
                          <span className="font-medium text-sm">Selecionar todos</span>
                        </label>
                        <div className="flex flex-col gap-2">
                          {permsModulo.map((p) => (
                            <label key={p.id} className="flex items-center gap-3 p-2 rounded hover:bg-muted/50 transition cursor-pointer select-none border border-transparent">
                              <span className="switch">
                                <input
                                  type="checkbox"
                                  name="permissoes"
                                  value={p.id}
                                  checked={form.permissoes.includes(p.id)}
                                  onChange={handleChange}
                                />
                                <span className="slider round"></span>
                              </span>
                              <div className="flex flex-col">
                                <span className="font-medium text-base text-primary">
                                  {p.label}
                                </span>
                                {p.descricao && (
                                  <span className="text-xs text-muted-foreground">{p.descricao}</span>
                                )}
                                <span className="text-xs text-muted-foreground font-mono mt-1">{p.codename}</span>
                              </div>
                            </label>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
              {Object.keys(permsByModulo).length === 0 && (
                <div className="text-muted-foreground text-center py-8">Nenhuma permissão encontrada.</div>
              )}
            </div>
          </div>
        )}
        <div className="flex gap-2 mt-4">
          <Button type="submit" variant="success" disabled={loading}>Salvar</Button>
          <Button type="button" variant="secondary" onClick={() => navigate("/grupos")}>Cancelar</Button>
        </div>
      </form>
    </PageContainer>
  );
}
