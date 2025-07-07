import {
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
} from "./Sidebar";
import { useSidebar } from "../../hooks/sidebar-context";
import { FiHome, FiUser } from "react-icons/fi";
import { useLocation } from "react-router-dom";

export default function CustomSidebarMenu() {
  const { state } = useSidebar();
  const location = useLocation();

  const menu = [
    {
      label: "Dashboard",
      icon: <FiHome className="w-5 h-5" />,
      href: "/dashboard",
      active: location.pathname === "/dashboard",
    },
    {
      label: "Perfil",
      icon: <FiUser className="w-5 h-5" />,
      href: "/perfil",
      active: location.pathname === "/perfil",
    },
  ];

  return (
    <SidebarMenu>
      {menu.map((item) => (
        <SidebarMenuItem key={item.href}>
          <SidebarMenuButton
            asChild
            isActive={item.active}
            tooltip={item.label}
          >
            <a
              href={item.href}
              className={`flex items-center rounded-lg transition-colors text-sm font-medium
                ${
                  item.active
                    ? "bg-accent text-accent-foreground"
                    : "text-muted-foreground"
                }
                hover:bg-accent hover:text-accent-foreground
                ${
                  state === "collapsed"
                    ? "justify-center w-12 h-12 p-0 mx-auto"
                    : "gap-3 px-3 py-2 w-full"
                }
              `}
              title={item.label}
            >
              {item.icon}
              {state !== "collapsed" && <span>{item.label}</span>}
            </a>
          </SidebarMenuButton>
        </SidebarMenuItem>
      ))}
    </SidebarMenu>
  );
}