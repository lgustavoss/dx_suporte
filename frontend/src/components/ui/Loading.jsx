export default function Loading({ message = "Carregando..." }) {
  return (
    <div className="flex justify-center items-center h-full py-20">
      <span className="text-muted-foreground animate-pulse">{message}</span>
    </div>
  );
}