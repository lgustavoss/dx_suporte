import React from "react";
import PageContainer from "../../components/ui/PageContainer";
import { Button } from "../../components/ui/Button";
import { useGrupos } from "../../hooks/useGrupos";
import { useErrorHandler } from "../../hooks/useErrorHandler";

export default function GruposList() {
  const { grupos, loading, error, fetchGrupos } = useGrupos();
  const { showError } = useErrorHandler();

  React.useEffect(() => {
    fetchGrupos();
  }, []);

  if (loading) return <PageContainer>Carregando grupos...</PageContainer>;
  if (error) {
    showError(error);
    return <PageContainer>Erro ao carregar grupos.</PageContainer>;
  }

  return (
    <PageContainer>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-primary">Grupos</h2>
        <Button variant="success">Novo Grupo</Button>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full bg-background rounded-xl shadow">
          <thead>
            <tr>
              <th className="px-4 py-2 text-left">Nome</th>
              <th className="px-4 py-2 text-left">Ações</th>
            </tr>
          </thead>
          <tbody>
            {grupos.map((g) => (
              <tr key={g.id} className="border-b">
                <td className="px-4 py-2">{g.name}</td>
                <td className="px-4 py-2 flex gap-2">
                  <Button size="sm" variant="outline">Editar</Button>
                  <Button size="sm" variant="danger">Excluir</Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </PageContainer>
  );
}
