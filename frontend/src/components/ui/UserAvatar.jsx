export default function UserAvatar({ name, image }) {
  if (image) {
    return (
      <img
        src={image}
        alt={name}
        className="w-8 h-8 rounded-full object-cover bg-muted"
      />
    );
  }
  // Mostra as iniciais
  const initials = name
    ? name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
    : "U";
  return (
    <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center font-bold text-primary-foreground">
      {initials}
    </div>
  );
}