
import { Routes, Route } from "react-router-dom";
import PrivateRoute from "./PrivateRoute";
import Login from "../pages/auth/Login";
import Dashboard from "../pages/dashboard/Dashboard";
import Perfil from "../pages/perfil/Perfil";
import UsuariosList from "../pages/usuarios/UsuariosList";
import UsuarioNovo from "../pages/usuarios/UsuarioNovo";
import UsuarioEditar from "../pages/usuarios/UsuarioEditar";
import UsuarioVisualizar from "../pages/usuarios/UsuarioVisualizar";
import GruposList from "../pages/grupos/GruposList";
import GrupoNovo from "../pages/grupos/GrupoNovo";

export function AppRoutes() {
  return (
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
                  {/* Outras rotas protegidas */}
                </Routes>
  );
}