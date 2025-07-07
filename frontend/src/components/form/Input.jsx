import React from "react";

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
  return (
    <div className="mb-4">
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
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={`w-full px-3 py-2 border border-accent rounded bg-input text-foreground focus:outline-none focus:ring-2 focus:ring-secondary font-sans ${className}`}
        {...props}
      />
    </div>
  );
}
