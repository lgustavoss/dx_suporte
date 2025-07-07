export default function PageContainer({ children }) {
  return (
    <div className="max-w-3xl mx-auto bg-card text-card-foreground rounded-2xl shadow-2xl px-8 py-10 mt-10">
      {children}
    </div>
  );
}