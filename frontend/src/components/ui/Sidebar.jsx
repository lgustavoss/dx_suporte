import { Link, useLocation } from "react-router-dom";
import { FiUser, FiHome, FiUsers } from "react-icons/fi";

const menuItems = [
  { label: "Dashboard", icon: <FiHome />, to: "/dashboard" },
  { label: "Usuários", icon: <FiUsers />, to: "/usuarios" },
];

export default function Sidebar({ expanded, setExpanded }) {
  const location = useLocation();

  return (
    <aside
      className={`fixed left-0 top-16 h-[calc(100vh-4rem)] bg-primary text-white shadow-lg transition-all duration-300
        ${expanded ? "w-56" : "w-16"} flex flex-col overflow-x-hidden min-w-0`}
    >
      <nav className="flex-1 flex flex-col gap-2 mt-4">
        {menuItems.map((item) => (
          <Link
            key={item.to}
            to={item.to}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition 
              ${location.pathname === item.to ? "bg-white/20 font-bold" : "hover:bg-white/10"}
              ${expanded ? "justify-start" : "justify-center"}
            `}
          >
            {item.icon}
            {expanded && <span>{item.label}</span>}
          </Link>
        ))}
      </nav>
      <div className="flex items-center gap-2 px-4 py-4 border-t border-white/10">
        <FiUser className="w-6 h-6" />
        {expanded && (
          <span className="truncate">
            {JSON.parse(localStorage.getItem("user") || "{}").username || "Usuário"}
          </span>
        )}
      </div>
    </aside>
  );
}