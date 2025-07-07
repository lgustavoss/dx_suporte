import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import Login from "./pages/auth/Login";
import Dashboard from "./pages/dashboard/Dashboard";
import PrivateRoute from "./routes/PrivateRoute";
import Navbar from "./components/ui/Navbar";
import { Sidebar } from "./components/ui/Sidebar";
import { SidebarProvider } from "./hooks/sidebar-context";
import Perfil from "./pages/perfil/Perfil";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import CustomSidebarMenu from "./components/ui/SidebarMenu";

function AppRoutes() {
  const location = useLocation();
  const hideNavbar = location.pathname === "/";
  const hideSidebar = location.pathname === "/";

  return (
    <SidebarProvider>
      {!hideNavbar && <Navbar />}
      <div className="fixed inset-0 flex bg-background text-foreground">
        {!hideSidebar && (
          <Sidebar
            className="pt-14 bg-card/80 backdrop-blur border-r border-border"
            collapsible="icon"
          >
            <CustomSidebarMenu />
          </Sidebar>
        )}
        <div className="flex-1 flex flex-col min-h-0">
          <main
            className={`flex-1 min-h-0 transition-all ${
              !hideNavbar ? "pt-16" : ""
            }`}
          >
            <Routes>
              <Route path="/" element={<Login />} />
              <Route
                path="/dashboard"
                element={
                  <PrivateRoute>
                    <Dashboard />
                  </PrivateRoute>
                }
              />
              <Route
                path="/perfil"
                element={
                  <PrivateRoute>
                    <Perfil />
                  </PrivateRoute>
                }
              />
              {/* Outras rotas protegidas */}
            </Routes>
          </main>
        </div>
      </div>
      <ToastContainer position="bottom-right" autoClose={4000} />
    </SidebarProvider>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}
