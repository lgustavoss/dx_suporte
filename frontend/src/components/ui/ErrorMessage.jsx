export default function ErrorMessage({ message = "Ocorreu um erro." }) {
  return (
    <div className="flex justify-center items-center h-full py-20">
      <span className="text-red-500">{message}</span>
    </div>
  );
}