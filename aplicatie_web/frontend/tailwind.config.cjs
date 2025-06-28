/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,svelte,js,ts}",
    "./node_modules/flowbite-svelte/**/*.{js,svelte}",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('flowbite/plugin'),
  ],
}