import { useNavigate } from "react-router-dom";
import { useState, useRef, useEffect } from "react";
import { FiMenu } from "react-icons/fi";
import { useLogout } from "../../hooks/useLogout";

export default function Navbar({ sidebarExpanded, setSidebarExpanded }) {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  const menuRef = useRef();
  const { logout } = useLogout(); // <-- Corrija aqui

  // Fecha o dropdown ao clicar fora
  useEffect(() => {
    function handleClickOutside(event) {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setOpen(false);
      }
    }
    if (open) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open]);

  return (
    <nav className="w-full bg-primary text-white px-6 py-3 flex items-center justify-between shadow fixed top-0 left-0 z-50">
      <div className="flex items-center gap-4">
        <span className="font-heading text-xl font-bold tracking-wide select-none whitespace-nowrap">
          Duplex Soft
        </span>
        <button
          className="ml-2 flex items-center justify-center focus:outline-none rounded-full bg-white/10 p-2 hover:bg-white/20 transition"
          onClick={() => setSidebarExpanded((v) => !v)}
          aria-label="Expandir/recolher menu"
        >
          <FiMenu className="w-6 h-6" />
        </button>
      </div>
      <div className="flex items-center gap-4">
        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setOpen((v) => !v)}
            className="flex items-center gap-2 font-semibold focus:outline-none rounded-full bg-white/10 px-4 py-2 hover:bg-white/20 transition"
          >
            <span className="font-medium">
              {user.username || user.email || "Usuário"}
            </span>
            <svg
              className={`w-4 h-4 transition-transform ${open ? "rotate-180" : ""}`}
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>
          {open && (
            <div className="absolute right-0 mt-2 w-44 bg-white text-gray-800 rounded-xl shadow-lg z-50 py-2 animate-fade-in">
              <button
                className="block w-full text-left px-4 py-2 rounded hover:bg-gray-100 transition"
                onClick={() => {
                  setOpen(false);
                  navigate("/perfil");
                }}
              >
                Perfil
              </button>
              <button
                onClick={logout} // Agora funciona!
                className="block w-full text-left px-4 py-2 rounded hover:bg-gray-100 transition"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}