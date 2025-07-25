import React from "react";
import { BrowserRouter, useLocation, Routes, Route } from "react-router-dom";
import { AppRoutes } from "./routes/AppRoutes";
import Layout from "./layout/Layout";
import "react-toastify/dist/ReactToastify.css";
import UsuariosList from "./pages/usuarios/UsuariosList";
import UsuarioNovo from "./pages/usuarios/UsuarioNovo";
import UsuarioEditar from "./pages/usuarios/UsuarioEditar";
import UsuarioVisualizar from "./pages/usuarios/UsuarioVisualizar";
import GruposList from "./pages/grupos/GruposList";
import GrupoNovo from "./pages/grupos/GrupoNovo";
import GrupoVisualizar from "./pages/grupos/GrupoVisualizar";
import CustomSidebarMenu from "./components/ui/SidebarMenu";
import { SidebarProvider } from "./hooks/sidebar-context";
import Navbar from "./components/ui/Navbar";
import Sidebar from "./components/ui/Sidebar";
import PrivateRoute from "./routes/PrivateRoute";
import Dashboard from "./pages/dashboard/Dashboard";
import Perfil from "./pages/perfil/Perfil";
import Login from "./pages/auth/Login";
import { ToastContainer } from "react-toastify";

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
            className={`flex-1 min-h-0 transition-all overflow-y-auto ${
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
                    <GruposList />
                  </PrivateRoute>
                }
              />
              <Route
                path="/grupos/novo"
                element={
                  <PrivateRoute>
                    <GrupoNovo />
                  </PrivateRoute>
                }
              />
              <Route
                path="/grupos/:id/visualizar"
                element={
                  <PrivateRoute>
                    <GrupoVisualizar />
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
      <Layout>
        <AppRoutes />
      </Layout>
    </BrowserRouter>
  );
}