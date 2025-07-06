import React from "react";

export default function Button({ children, type = "button", className = "", ...props }) {
  return (
    <button
      type={type}
      className={`px-4 py-2 rounded font-heading transition ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
