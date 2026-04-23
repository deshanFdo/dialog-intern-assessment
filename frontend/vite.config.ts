import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  base: '/dialog-intern-assessment/',
  plugins: [react()],
  server: {
    port: 5173,
  },
})
