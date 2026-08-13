import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://cafe-cenit.example.com',
  integrations: [],
  vite: {
    css: {
      preprocessorOptions: {
        css: {
          // Enable CSS custom properties
        }
      }
    }
  }
});