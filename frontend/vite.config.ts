import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
// Phase 22: Vercel Edge Global Frontend Deployment & CDN Optimization
// Governing Mathematical Invariant: TTFB_global <= 80ms, LighthouseScore >= 98
export default defineConfig({
  plugins: [react()],
  build: {
    target: 'esnext',
    minify: true,
    cssMinify: true,
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks(id: string) {
          if (id.includes('node_modules/react') || id.includes('node_modules/react-dom')) {
            return 'vendor-react';
          }
          if (id.includes('node_modules/leaflet')) {
            return 'vendor-leaflet';
          }
          if (id.includes('node_modules/lucide-react')) {
            return 'vendor-icons';
          }
        }
      }
    },
    chunkSizeWarningLimit: 600
  },
  server: {
    port: 5173,
    host: true
  }
})
