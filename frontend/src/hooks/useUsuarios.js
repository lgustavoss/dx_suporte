import { useState } from "react";
import { fetchUsuarios } from "../services/userService";

export function useUsuarios() {
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showAll, setShowAll] = useState(false); // false = só ativos, true = todos

  async function getUsuarios(opts = {}) {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchUsuarios({ includeInactive: opts.includeInactive ?? showAll });
      if (Array.isArray(data)) {
        setUsuarios(data);
      } else if (Array.isArray(data.results)) {
        setUsuarios(data.results);
      } else {
        setUsuarios([]);
      }
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }

  return {
    usuarios,
    loading,
    error,
    fetchUsuarios: getUsuarios,
    showAll,
    setShowAll,
  };
}
