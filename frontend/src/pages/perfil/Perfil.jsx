import PageContainer from "../../components/ui/PageContainer";
import Loading from "../../components/ui/Loading";
import ErrorMessage from "../../components/ui/ErrorMessage";
import { usePerfil } from "../../hooks/usePerfil";

export default function Perfil() {
  const { user, loading } = usePerfil();

  if (loading) {
    return <Loading message="Carregando perfil..." />;
  }

  if (!user) {
    return <ErrorMessage message="Não foi possível carregar o perfil." />;
  }

  return (
    <PageContainer>
      <h2 className="text-2xl font-bold text-primary mb-6">Perfil do Usuário</h2>
      <div className="flex flex-col gap-3">
        <div>
          <span className="font-semibold">Nome:</span> {user.full_name || user.username}
        </div>
        <div>
          <span className="font-semibold">E-mail:</span> {user.email}
        </div>
        <div>
          <span className="font-semibold">Usuário:</span> {user.username}
        </div>
        <div>
          <span className="font-semibold">Grupos:</span> {user.grupos_nomes?.join(", ") || "-"}
        </div>
        <div>
          <span className="font-semibold">Ativo:</span> {user.is_active ? "Sim" : "Não"}
        </div>
        <div>
          <span className="font-semibold">Online:</span> {user.is_online ? "Sim" : "Não"}
        </div>
        <div>
          <span className="font-semibold">Entrou em:</span> {new Date(user.date_joined).toLocaleString()}
        </div>
        <div>
          <span className="font-semibold">Último login:</span> {user.last_login ? new Date(user.last_login).toLocaleString() : "-"}
        </div>
      </div>
    </PageContainer>
  );
}