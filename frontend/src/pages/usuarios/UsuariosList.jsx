import React, { useState } from "react";
import PageContainer from "../../components/ui/PageContainer";
import { Button } from "../../components/ui/Button";
import BadgeStatus from "../../components/ui/BadgeStatus";
import { useUsuarios } from "../../hooks/useUsuarios";
import { useNavigate } from "react-router-dom";
import { useErrorHandler } from "../../hooks/useErrorHandler";

export default function UsuariosList() {
  const { usuarios, loading, error, fetchUsuarios, showAll, setShowAll } = useUsuarios();
  const { showError } = useErrorHandler();

  const navigate = useNavigate();

  React.useEffect(() => {
    fetchUsuarios({ includeInactive: showAll });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showAll]);



  if (loading) return <PageContainer>Carregando usuários...</PageContainer>;
  if (error) {
    showError(error);
    return <PageContainer>Erro ao carregar usuários.</PageContainer>;
  }

  return (
    <PageContainer>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-primary">Usuários</h2>
        <Button variant="outline" onClick={() => navigate("/usuarios/novo")}>Novo Usuário</Button>
      </div>
      <div className="mb-4 border-b border-border flex gap-4">
        <button
          className={`py-2 px-4 -mb-px border-b-2 transition-colors ${!showAll ? 'border-primary text-primary font-bold' : 'border-transparent text-muted-foreground'}`}
          onClick={() => setShowAll(false)}
        >Ativos</button>
        <button
          className={`py-2 px-4 -mb-px border-b-2 transition-colors ${showAll ? 'border-primary text-primary font-bold' : 'border-transparent text-muted-foreground'}`}
          onClick={() => setShowAll(true)}
        >Todos</button>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full bg-background rounded-xl shadow">
          <thead>
            <tr>
              <th className="px-4 py-2 text-left">Nome</th>
              <th className="px-4 py-2 text-left">E-mail</th>
              <th className="px-4 py-2 text-left">Online</th>
              <th className="px-4 py-2 text-left">Status</th>
              <th className="px-4 py-2 text-left">Ações</th>
            </tr>
          </thead>
          <tbody>
            {usuarios.map((u) => (
              <tr key={u.id} className="border-b">
                <td className="px-4 py-2">{u.first_name} {u.last_name}</td>
                <td className="px-4 py-2">{u.email}</td>
                <td className="px-4 py-2 flex items-center justify-center">
                  {u.is_online ? (
                    <span title="Online" className="text-green-500">
                      <svg width="18" height="18" fill="currentColor" viewBox="0 0 20 20"><circle cx="10" cy="10" r="8" /></svg>
                    </span>
                  ) : (
                    <span title="Offline" className="text-gray-400">
                      <svg width="18" height="18" fill="currentColor" viewBox="0 0 20 20"><circle cx="10" cy="10" r="8" /></svg>
                    </span>
                  )}
                </td>
                <td className="px-4 py-2"><BadgeStatus value={u.is_active} /></td>
                <td className="px-4 py-2 flex gap-2">
                  <button
                    onClick={() => navigate(`/usuarios/${u.id}/visualizar`)}
                    className="p-2 rounded hover:bg-blue-100 transition-colors"
                    title="Visualizar usuário"
                  >
                    <svg width="20" height="20" fill="none" viewBox="0 0 20 20">
                      <path d="M10 4.5c-4.5 0-7.5 4.5-7.5 5.5s3 5.5 7.5 5.5 7.5-4.5 7.5-5.5-3-5.5-7.5-5.5Zm0 9c-2 0-3.5-1.5-3.5-3.5S8 6.5 10 6.5s3.5 1.5 3.5 3.5S12 13.5 10 13.5Zm0-5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3Z" fill="currentColor"/>
                    </svg>
                  </button>
                  <button
                    onClick={() => navigate(`/usuarios/${u.id}/editar`)}
                    className="p-2 rounded hover:bg-primary/10 transition-colors"
                    title="Editar usuário"
                  >
                    <svg width="20" height="20" fill="none" viewBox="0 0 20 20">
                      <path d="M14.85 3.85a1.2 1.2 0 0 1 1.7 1.7l-8.2 8.2-2.1.4.4-2.1 8.2-8.2Zm-9.1 9.1-.6 3a.5.5 0 0 0 .6.6l3-.6 8.2-8.2a2.7 2.7 0 0 0-3.8-3.8l-8.2 8.2Z" fill="currentColor"/>
                    </svg>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </PageContainer>
  );
}
