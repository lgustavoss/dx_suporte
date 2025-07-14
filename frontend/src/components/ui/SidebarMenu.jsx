import {
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
} from "./Sidebar";

import { useSidebar } from "../../hooks/sidebar-context";
import { FiHome, FiUsers, FiLayers, FiSettings, FiChevronDown } from "react-icons/fi";
import { useLocation, Link } from "react-router-dom";
import React from "react";

export default function CustomSidebarMenu() {
  const { state } = useSidebar();
  const location = useLocation();
  const [gestaoOpen, setGestaoOpen] = React.useState(
    location.pathname.startsWith("/usuarios") || location.pathname.startsWith("/grupos")
  );

  React.useEffect(() => {
    // Expande automaticamente se navegar para rota de gestão
    if (location.pathname.startsWith("/usuarios") || location.pathname.startsWith("/grupos")) {
      setGestaoOpen(true);
    }
  }, [location.pathname]);

  const menu = [
    {
      label: "Dashboard",
      icon: <FiHome className="w-5 h-5" />,
      href: "/dashboard",
      active: location.pathname === "/dashboard",
    },
    {
      label: "Gestão",
      icon: <FiSettings className="w-5 h-5" />,
      href: "#",
      active: location.pathname.startsWith("/usuarios") || location.pathname.startsWith("/grupos"),
      children: [
        {
          label: "Usuários",
          icon: <FiUsers className="w-4 h-4" />,
          href: "/usuarios",
          active: location.pathname.startsWith("/usuarios"),
        },
        {
          label: "Grupos",
          icon: <FiLayers className="w-4 h-4" />,
          href: "/grupos",
          active: location.pathname.startsWith("/grupos"),
        },
      ],
    },
  ];

  return (
    <SidebarMenu>
      {menu.map((item) => (
        <SidebarMenuItem key={item.label}>
          {item.children ? (
            <button
              type="button"
              className={`flex items-center rounded-lg transition-colors text-sm font-medium w-full
                ${item.active ? "bg-accent text-accent-foreground" : "text-muted-foreground"}
                hover:bg-accent hover:text-accent-foreground
                ${state === "collapsed" ? "justify-center w-12 h-12 p-0 mx-auto" : "gap-3 px-3 py-2"}
              `}
              title={item.label}
              onClick={() => setGestaoOpen((open) => !open)}
            >
              {item.icon}
              {state !== "collapsed" && <span>{item.label}</span>}
              {state !== "collapsed" && (
                <FiChevronDown
                  className={`ml-auto transition-transform ${gestaoOpen ? "rotate-180" : "rotate-0"}`}
                />
              )}
            </button>
          ) : (
            <SidebarMenuButton
              asChild
              isActive={item.active}
              tooltip={item.label}
            >
              <Link
                to={item.href}
                className={`flex items-center rounded-lg transition-colors text-sm font-medium
                  ${item.active ? "bg-accent text-accent-foreground" : "text-muted-foreground"}
                  hover:bg-accent hover:text-accent-foreground
                  ${state === "collapsed" ? "justify-center w-12 h-12 p-0 mx-auto" : "gap-3 px-3 py-2 w-full"}
                `}
                title={item.label}
              >
                {item.icon}
                {state !== "collapsed" && <span>{item.label}</span>}
              </Link>
            </SidebarMenuButton>
          )}
          {/* Submenu de gestão */}
          {item.children && gestaoOpen && state !== "collapsed" && (
            <div className="ml-8 mt-1 flex flex-col gap-1">
              {item.children.map((child) => (
                <SidebarMenuButton
                  asChild
                  key={child.href}
                  isActive={child.active}
                  tooltip={child.label}
                >
                  <Link
                    to={child.href}
                    className={`flex items-center rounded-lg transition-colors text-xs font-medium
                      ${child.active ? "bg-accent text-accent-foreground" : "text-muted-foreground"}
                      hover:bg-accent hover:text-accent-foreground gap-2 px-3 py-2 w-full`
                    }
                    title={child.label}
                  >
                    {child.icon}
                    <span>{child.label}</span>
                  </Link>
                </SidebarMenuButton>
              ))}
            </div>
          )}
        </SidebarMenuItem>
      ))}
    </SidebarMenu>
  );
}