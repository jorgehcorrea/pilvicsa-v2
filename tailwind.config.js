/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './*.html',
    './src/**/*.js',
    './node_modules/flowbite/**/*.js'
  ],
  theme: {
    extend: {
      colors: {
        pilvicsa: {
          dark:    '#0d1f13',
          primary: '#1a4d2e',
          mid:     '#2c6e3f',
          light:   '#4a9e5c',
          accent:  '#8bc34a',
          surface: '#f4f8f5',
        }
      },
      fontFamily: {
        sans:    ['Inter', 'sans-serif'],
        display: ['Syne', 'sans-serif'],
      }
    }
  },
  plugins: [
    require('flowbite/plugin')
  ]
}
