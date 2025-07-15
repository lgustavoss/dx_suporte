import React from "react";
import PageContainer from "../../components/ui/PageContainer";
import { Button } from "../../components/ui/Button";
import { FiEye, FiEdit2, FiTrash2 } from "react-icons/fi";
import GrupoForm from "./GrupoForm";
import { createGrupo } from "../../services/groupService";
import { useGrupos } from "../../hooks/useGrupos";
import { useErrorHandler } from "../../hooks/useErrorHandler";
import { useNavigate } from "react-router-dom";

export default function GruposList() {
  const { grupos, loading, error, fetchGrupos } = useGrupos();
  const { showError } = useErrorHandler();
  const navigate = useNavigate();
  const [showModal, setShowModal] = React.useState(false);
  const [saving, setSaving] = React.useState(false);

  React.useEffect(() => {
    fetchGrupos();
  }, []);

  async function handleSaveGrupo(form) {
    setSaving(true);
    try {
      // O backend espera: { group_data: { name }, descricao, ativo }
      await createGrupo({
        group_data: { name: form.nome },
        descricao: form.descricao,
        ativo: form.ativo,
      });
      setShowModal(false);
      fetchGrupos();
    } catch (err) {
      showError(err);
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <PageContainer>Carregando grupos...</PageContainer>;
  if (error) {
    showError(error);
    return <PageContainer>Erro ao carregar grupos.</PageContainer>;
  }

  // Suporte a resposta paginada do DRF
  const gruposArray = Array.isArray(grupos)
    ? grupos
    : (grupos && Array.isArray(grupos.results))
      ? grupos.results
      : [];

  return (
    <PageContainer>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-primary">Grupos</h2>
        <Button variant="outline" onClick={() => navigate("/grupos/novo")}>Novo Grupo</Button>
      </div>
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-background rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-bold mb-4">Novo Grupo</h3>
            <GrupoForm
              onSave={handleSaveGrupo}
              onCancel={() => setShowModal(false)}
              loading={saving}
            />
          </div>
        </div>
      )}
      <div className="overflow-x-auto">
        <table className="min-w-full bg-background rounded-xl shadow">
          <thead>
            <tr>
              <th className="px-4 py-2 text-left">Nome</th>
              <th className="px-4 py-2 text-right align-middle" style={{ verticalAlign: 'middle', textAlign: 'right', height: '48px' }}>Ações</th>
            </tr>
          </thead>
          <tbody>
            {gruposArray.map((g) => (
              <tr key={g.id} className="border-b">
                <td className="px-4 py-2">{g.nome || g.name}</td>
                <td className="px-4 py-2 flex items-center justify-end gap-2" style={{ height: '48px' }}>
                  <Button size="sm" variant="outline" title="Visualizar" onClick={() => navigate(`/grupos/${g.id}/visualizar`)}>
                    <FiEye size={18} className="text-gray-400 hover:text-blue-500 transition-colors" />
                  </Button>
                  <Button size="sm" variant="outline" title="Editar" onClick={() => navigate(`/grupos/${g.id}/editar`)}>
                    <FiEdit2 size={18} className="text-gray-400 hover:text-blue-500 transition-colors" />
                  </Button>
                  <Button size="sm" variant="outline" title="Excluir" onClick={() => handleExcluir(g.id)}>
                    <FiTrash2 size={18} className="text-gray-400 hover:text-red-500 transition-colors" />
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </PageContainer>
  );
}
