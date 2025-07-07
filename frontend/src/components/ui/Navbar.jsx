import { useNavigate } from "react-router-dom";
import { useState, useRef, useEffect } from "react";
import { FiMenu, FiSun, FiMoon, FiBell, FiPlus, FiSearch, FiUser, FiLogOut, FiSettings } from "react-icons/fi";
import { useLogout } from "../../hooks/useLogout";
import UserAvatar from "./UserAvatar";
import { useSidebar } from "../../components/ui/Sidebar";

export default function Navbar({ sidebarExpanded, setSidebarExpanded }) {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  const menuRef = useRef();
  const { logout } = useLogout();
  const { toggleSidebar, isMobile } = useSidebar();

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

  // Troca tema
  const toggleTheme = () => {
    document.documentElement.classList.toggle("dark");
    if (document.documentElement.classList.contains("dark")) {
      localStorage.setItem("theme", "dark");
    } else {
      localStorage.setItem("theme", "light");
    }
  };

  return (
    <nav className="w-full bg-card/80 backdrop-blur border-b border-border shadow-sm px-4 h-14 flex items-center justify-between fixed top-0 left-0 z-50 transition-all">
      {/* Logo e menu */}
      <div className="flex items-center gap-2">
        {/* Botão de expandir/recolher */}
        <button
          className="mr-4 text-muted-foreground hover:text-primary focus:outline-none"
          onClick={toggleSidebar}
          aria-label="Abrir menu lateral"
        >
          <FiMenu size={22} />
        </button>
        <span className="font-heading text-lg font-bold tracking-tight select-none whitespace-nowrap text-foreground">
          DX Suporte
        </span>
      </div>
      {/* Busca */}
      <div className="hidden md:flex flex-1 justify-center px-4">
        <div className="relative w-full max-w-xs">
          <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Buscar tickets, clientes..."
            className="w-full pl-10 pr-3 py-2 rounded-lg bg-input text-foreground border border-input focus:outline-none focus:ring-2 focus:ring-primary text-sm transition"
          />
        </div>
      </div>
      {/* Ações */}
      <div className="flex items-center gap-2">
        {/* Botão criar */}
        <button
          className="flex items-center gap-2 px-3 py-2 rounded-lg bg-popover text-popover-foreground font-semibold hover:bg-muted transition text-sm shadow-sm border border-border"
          title="Criar"
        >
          <FiPlus className="w-5 h-5" />
          <span className="hidden md:inline">Criar</span>
        </button>
        {/* Notificações */}
        <div className="relative">
          <button className="p-2 rounded-full hover:bg-accent transition" title="Notificações">
            <FiBell className="w-5 h-5 text-muted-foreground" />
            <span className="absolute -top-1 -right-1 bg-destructive text-white text-[10px] rounded-full px-1 font-bold shadow">
              3
            </span>
          </button>
        </div>
        {/* Dropdown usuário */}
        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setOpen((v) => !v)}
            className="flex items-center gap-2 font-semibold focus:outline-none rounded-full px-2 py-1 hover:bg-accent transition"
          >
            <UserAvatar name={user.username || user.email || "Usuário"} image={user.avatar} />
            <span className="font-medium hidden md:inline text-foreground">
              {user.username || user.email || "Usuário"}
            </span>
            <svg
              className={`w-4 h-4 transition-transform text-muted-foreground ${open ? "rotate-180" : ""}`}
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
            <div className="absolute right-0 mt-2 w-64 bg-popover text-popover-foreground rounded-xl shadow-lg z-50 py-2 animate-fade-in border border-border text-sm">
              {/* Username e email */}
              <div className="px-4 py-2">
                <div className="font-semibold text-foreground">{user.username || user.email || "Usuário"}</div>
                <div className="text-xs text-muted-foreground truncate">{user.email}</div>
              </div>
              <div className="my-2 border-t border-border" />
              {/* Opções */}
              <button
                className="flex items-center gap-2 w-full text-left px-4 py-2 rounded hover:bg-muted transition"
                onClick={() => {
                  setOpen(false);
                  navigate("/perfil");
                }}
              >
                <FiUser className="w-4 h-4 opacity-80" />
                <span>Meu Perfil</span>
              </button>
              <button
                className="flex items-center gap-2 w-full text-left px-4 py-2 rounded hover:bg-muted transition"
                onClick={() => {
                  setOpen(false);
                  navigate("/configuracoes");
                }}
              >
                <FiSettings className="w-4 h-4 opacity-80" />
                <span>Configurações</span>
              </button>
              <div className="my-2 border-t border-border" />
              <button
                onClick={logout}
                className="flex items-center gap-2 w-full text-left px-4 py-2 rounded hover:bg-muted transition text-destructive"
              >
                <FiLogOut className="w-4 h-4 opacity-80" />
                <span>Sair</span>
              </button>
            </div>
          )}
        </div>
        {/* Botão de tema */}
        <button
          onClick={toggleTheme}
          className="ml-1 p-2 rounded-full hover:bg-accent transition"
          aria-label="Alternar tema"
        >
          {document.documentElement.classList.contains("dark") ? (
            <FiSun className="text-blue-500" />
          ) : (
            <FiMoon className="text-blue-500" />
          )}
        </button>
      </div>
    </nav>
  );
}