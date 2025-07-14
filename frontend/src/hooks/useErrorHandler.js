import { toast } from "react-toastify";

/**
 * Exibe uma mensagem de erro genérica para o usuário.
 * Nunca mostra detalhes técnicos ou mensagens sensíveis do backend.
 */
export function useErrorHandler() {
  function showError(error) {
    toast.error("Ocorreu um erro. Tente novamente.");
    // Apenas em desenvolvimento, loga detalhes no console
    if (process.env.NODE_ENV === "development") {
      // eslint-disable-next-line no-console
      console.error("Detalhes do erro:", error);
    }
  }

  return { showError };
}