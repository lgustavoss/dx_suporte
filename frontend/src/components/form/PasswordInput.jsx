import React, { useState } from "react";
import { FiEye, FiEyeOff } from "react-icons/fi";
import Input from "./Input";

export default function PasswordInput({
  label,
  name = "password",
  value,
  onChange,
  placeholder = "",
  className = "",
  ...props
}) {
  const [show, setShow] = useState(false);
  return (
    <div className="mb-4 relative">
      <Input
        label={label}
        name={name}
        type={show ? "text" : "password"}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={`pr-10 ${className}`}
        {...props}
      />
      <button
        type="button"
        tabIndex={-1}
        className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center justify-center text-muted-foreground hover:text-primary focus:outline-none"
        onClick={() => setShow((s) => !s)}
        aria-label={show ? "Ocultar senha" : "Mostrar senha"}
      >
        {show ? <FiEyeOff size={22} className="pointer-events-none" /> : <FiEye size={22} className="pointer-events-none" />}
      </button>
    </div>
  );
}
