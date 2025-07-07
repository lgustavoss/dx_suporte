import { FiCheckCircle, FiXCircle } from "react-icons/fi";

export default function BadgeStatus({ value, activeLabel = "Ativo", inactiveLabel = "Inativo" }) {
  const isActive = value === true || value === "Sim";
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold
        ${isActive
          ? "bg-green-600/20 text-green-400"
          : "bg-red-600/20 text-red-400"}
      `}
    >
      {isActive ? (
        <FiCheckCircle className="w-4 h-4" />
      ) : (
        <FiXCircle className="w-4 h-4" />
      )}
      {isActive ? activeLabel : inactiveLabel}
    </span>
  );
}