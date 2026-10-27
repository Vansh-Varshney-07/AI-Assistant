import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const appRoot = fileURLToPath(new URL('.', import.meta.url));
export default defineConfig({
  root: path.resolve(appRoot, 'src/renderer'), base: './',
  plugins: [react()],
  build: { outDir: path.resolve(appRoot, 'dist/renderer'), emptyOutDir: true, target: 'es2022' },
  test: { root: appRoot, environment: 'jsdom', include: ['tests/**/*.test.{ts,tsx}'], globals: true, setupFiles: ['./tests/setup.ts'] },
});
