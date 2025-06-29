const forms = require('@tailwindcss/forms');
const typography = require('@tailwindcss/typography');
const flowbite = require('flowbite/plugin');

module.exports = {
  content: [
    "./src/**/*.{html,svelte,js,ts}",
    "./node_modules/flowbite-svelte/**/*.{js,svelte}",
    "./node_modules/flowbite-svelte-icons/**/*.{html,js,svelte,ts}"
  ],
  theme: {
    extend: {},
  },
  plugins: [
    forms,
    typography,
    flowbite,
  ],
}