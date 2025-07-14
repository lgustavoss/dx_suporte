import { useState } from "react";
import { fetchGrupos } from "../services/groupService";

export function useGrupos() {
  const [grupos, setGrupos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function getGrupos() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchGrupos();
      setGrupos(data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }

  return {
    grupos,
    loading,
    error,
    fetchGrupos: getGrupos,
  };
}
