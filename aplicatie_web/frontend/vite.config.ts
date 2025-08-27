import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve, join } from 'node:path';

const __filename = fileURLToPath(import.meta.url);
const __dirname  = dirname(__filename);

const certDir = resolve(__dirname, '../certs');
const certPath = join(certDir, 'dev-cert.pem');
const keyPath = join(certDir, 'dev-key.pem');

const https =
  existsSync(certPath) && existsSync(keyPath)
    ? {
        cert: readFileSync(certPath),
        key: readFileSync(keyPath),
      }
    : undefined;

export default defineConfig({
  plugins: [sveltekit()],
  server: { https, host: true, port: 5173 },
  preview: { https, host: true, port: 5173 },
  build: { sourcemap: false },
  css: { devSourcemap: false }
});