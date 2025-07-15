import { useLocation } from "react-router-dom";
import Navbar from "../components/ui/Navbar";
import { Sidebar } from "../components/ui/Sidebar";
import CustomSidebarMenu from "../components/ui/SidebarMenu";
import { SidebarProvider } from "../hooks/sidebar-context";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

export default function MainLayout({ children }) {
  const location = useLocation();
  const hideUI = location.pathname === "/";

  return (
    <SidebarProvider>
      {!hideUI && <Navbar />}
      <div className="fixed inset-0 flex bg-background text-foreground">
        {!hideUI && (
          <Sidebar className="pt-14 bg-card/80 backdrop-blur border-r border-border" collapsible="icon">
            <CustomSidebarMenu />
          </Sidebar>
        )}
        <div className="flex-1 flex flex-col min-h-0">
          <main className={`flex-1 min-h-0 transition-all overflow-y-auto ${!hideUI ? "pt-16" : ""}`}>
            {children}
          </main>
        </div>
      </div>
      <ToastContainer position="bottom-right" autoClose={4000} />
    </SidebarProvider>
  );
}
