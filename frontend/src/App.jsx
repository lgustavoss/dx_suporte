import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { useState } from "react";
import Login from "./pages/auth/Login";
import Dashboard from "./pages/dashboard/Dashboard";
import PrivateRoute from "./routes/PrivateRoute";
import Navbar from "./components/ui/Navbar";
import Sidebar from "./components/ui/Sidebar";
import Perfil from "./pages/perfil/Perfil";
import { FiMenu } from "react-icons/fi";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function AppRoutes() {
  const location = useLocation();
  const hideNavbar = location.pathname === "/";
  const hideSidebar = location.pathname === "/";
  const [sidebarExpanded, setSidebarExpanded] = useState(true);

  return (
    <>
      {!hideNavbar && (
        <Navbar
          sidebarExpanded={sidebarExpanded}
          setSidebarExpanded={setSidebarExpanded}
        />
      )}
      {!hideSidebar && (
        <Sidebar expanded={sidebarExpanded} setExpanded={setSidebarExpanded} />
      )}
      <div
        className={
          !hideSidebar
            ? `pt-16 ${sidebarExpanded ? "pl-56" : "pl-16"} transition-all`
            : "pt-16"
        }
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
      </div>
      <button
        className="flex items-center justify-center h-16 focus:outline-none"
        onClick={() => setSidebarExpanded((v) => !v)}
        aria-label="Expandir/recolher menu"
      >
        <FiMenu className="w-6 h-6" />
      </button>
      <ToastContainer position="bottom-right" autoClose={4000} />
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}
