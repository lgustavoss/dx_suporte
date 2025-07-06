/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#0A2A5C",      // Azul escuro de fundo
        secondary: "#1976D2",    // Azul médio do logo
        accent: "#5AB3FF",       // Azul claro dos detalhes
        white: "#FFFFFF",
        // Adicione outros tons se necessário
      },
      fontFamily: {
        sans: ['"Inter"', 'Arial', 'sans-serif'],
        heading: ['"Montserrat"', 'sans-serif'],
        // Se quiser usar a fonte do logo, adicione aqui quando souber o nome
      },
    },
  },
  plugins: [],
}

