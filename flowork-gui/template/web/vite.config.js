//#######################################################################
// WEBSITE https://flowork.cloud
// File NAME : C:\FLOWORK\flowork-gui\template\web\vite.config.js total lines 71 
//#######################################################################

import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify';
import path from 'path';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  const targetUrl = env.VITE_GATEWAY_URL || 'http://localhost:8000';
  const productionUrl = 'https://flowork.cloud';

  return {
    plugins: [
      vue({ template: { transformAssetUrls } }),
      vuetify({
        autoImport: true,
        styles: { configFile: 'src/styles/settings.scss' },
      }),
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        '@mdi/font': path.resolve(__dirname, 'node_modules/@mdi/font'),
      },
    },
    publicDir: 'public',
    server: {
      host: '127.0.0.1',
      port: 5173,
      allowedHosts: ['flowork.cloud', 'localhost', '127.0.0.1'],
      hmr: {
        protocol: 'ws',
        host: '127.0.0.1',
        port: 5173,
      },
      proxy: {
        '/api/socket.io': {
          target: targetUrl,
          ws: true,
          changeOrigin: true,
          secure: false,
        },
        '/api/v1/ai': {
          target: productionUrl,
          changeOrigin: true,
          secure: true,
        },
        '/api': {
          target: targetUrl,
          changeOrigin: true,
          secure: false,
        },
      },
    },
    build: {
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: true,
          drop_debugger: true,
        },
      },
    },
  };
});
