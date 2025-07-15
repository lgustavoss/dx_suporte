import React from "react";
import Input from "../../components/form/Input";
import PasswordInput from "../../components/form/PasswordInput";
import { Button } from "../../components/ui/Button";
import bgImg from "../../assets/fundo.png";
import { useLoginForm } from "../../hooks/useLoginForm";
import { toast } from "react-toastify";
import { useErrorHandler } from "../../hooks/useErrorHandler";

export default function Login() {
  const { form, emailValid, emailTouched, handleChange, handleBlur, handleSubmit, loading } = useLoginForm();
  const { showError } = useErrorHandler();

  return (
    <div
      className="fixed inset-0 flex items-center justify-center"
      style={{
        backgroundImage: `url(${bgImg})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        backgroundColor: "hsl(var(--background))",
        minHeight: "100vh",
        minWidth: "100vw",
        overflow: "hidden",
      }}
    >
      {/* Overlay escuro para opacidade */}
      <div className="absolute inset-0 bg-background/80 pointer-events-none" />
      <div className="relative z-10 bg-card backdrop-blur-xl rounded-2xl shadow-2xl px-8 py-10 w-full max-w-sm flex flex-col gap-6">
        <div className="flex flex-col items-center mb-4">
          {/* <img src="/logo.png" alt="Logo" className="h-12 mb-4" /> */}
          <h1 className="text-3xl font-heading font-bold text-primary mb-2 tracking-tight">
            Bem-vindo
          </h1>
          <p className="text-base text-muted-foreground">Acesse sua conta para continuar</p>
        </div>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Input
            label="E-mail"
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder="seu@email.com"
            autoComplete="username"
            className={`h-12 rounded-xl border transition bg-input text-foreground placeholder:text-muted-foreground ${
              !emailValid && emailTouched
                ? "border-red-500 focus:border-red-500 focus:ring-2 focus:ring-red-200"
                : "border-accent focus:border-secondary focus:ring-2 focus:ring-secondary/20"
            }`}
          />
          <PasswordInput
            label="Senha"
            name="password"
            value={form.password}
            onChange={handleChange}
            placeholder="Sua senha"
            autoComplete="current-password"
            className="h-12 rounded-xl border border-accent focus:border-secondary focus:ring-2 focus:ring-secondary/20 transition bg-input text-foreground placeholder:text-muted-foreground"
          />
          <Button
            type="submit"
            className="w-full h-12 rounded-xl bg-primary text-primary-foreground font-semibold shadow hover:bg-secondary transition"
            disabled={loading}
          >
            {loading ? "Entrando..." : "Entrar"}
          </Button>
        </form>
        <div className="text-center mt-2">
          <a
            href="#"
            className="text-sm text-primary font-semibold hover:underline transition"
          >
            Esqueceu a senha?
          </a>
        </div>
      </div>
    </div>
  );
}
