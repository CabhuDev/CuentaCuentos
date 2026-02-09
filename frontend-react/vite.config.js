import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => ({
  plugins: [react()],
  base: mode === 'production' ? '/cuentacuentos/' : '/',
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/token': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/users': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/forgot-password': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/reset-password': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/change-password': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/data/audio': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
}))
