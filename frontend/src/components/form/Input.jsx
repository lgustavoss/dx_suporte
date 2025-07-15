import React, { useState } from "react";
import { FiEye, FiEyeOff } from "react-icons/fi";

export default function Input({
  label,
  name,
  type = "text",
  value,
  onChange,
  placeholder = "",
  className = "",
  ...props
}) {
  const [show, setShow] = useState(false);
  const isPassword = type === "password";
  return (
    <div className="mb-6 relative">
      {label && (
        <label
          htmlFor={name}
          className="block mb-1 font-heading text-primary"
        >
          {label}
        </label>
      )}
      <input
        id={name}
        name={name}
        type={isPassword && show ? "text" : type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={`w-full px-3 ${className?.includes('h-12') ? 'text-base' : 'py-2'} border border-accent rounded bg-input text-foreground focus:outline-none focus:ring-2 focus:ring-secondary font-sans ${className} ${isPassword ? 'pr-10' : ''}`}
        {...props}
      />
    </div>
  );
}
