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
import React from "react";
import UsuariosList from "./pages/usuarios/UsuariosList";
import UsuarioNovo from "./pages/usuarios/UsuarioNovo";
import UsuarioEditar from "./pages/usuarios/UsuarioEditar";
import UsuarioVisualizar from "./pages/usuarios/UsuarioVisualizar";
import GruposList from "./pages/grupos/GruposList";
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
              <Route
                path="/usuarios"
                element={
                  <PrivateRoute>
                    <UsuariosList />
                  </PrivateRoute>
                }
              />
              <Route
                path="/usuarios/novo"
                element={
                  <PrivateRoute>
                    <UsuarioNovo />
                  </PrivateRoute>
                }
              />
              <Route
                path="/usuarios/:id/editar"
                element={
                  <PrivateRoute>
                    <UsuarioEditar />
                  </PrivateRoute>
                }
              />
              <Route
                path="/usuarios/:id/visualizar"
                element={
                  <PrivateRoute>
                    <UsuarioVisualizar />
                  </PrivateRoute>
                }
              />
              <Route
                path="/grupos"
                element={
                  <PrivateRoute>
                    {/* Importação direta do componente */}
                    <GruposList />
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
