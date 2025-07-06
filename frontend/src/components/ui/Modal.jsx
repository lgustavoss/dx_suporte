import React from "react";

export default function Modal({ open, onClose, children }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div className="bg-white rounded shadow-lg p-6 min-w-[300px]">
        {children}
        <button
          className="mt-4 px-4 py-2 bg-secondary text-white rounded font-heading"
          onClick={onClose}
        >
          Fechar
        </button>
      </div>
    </div>
  );
}
