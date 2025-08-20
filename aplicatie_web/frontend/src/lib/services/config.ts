import { z } from 'zod';
import { API_BASE_URL, FILE_CONSTRAINTS, TIMING } from '$lib/utils/constants';

const PublicConfigSchema = z.object({
  maxSizeMb: z.number().positive().optional(),
  supportedExtensions: z.array(z.string().min(1)).optional(),
  supportedMimeTypes: z.array(z.string().min(1)).optional()
});

export type PublicConfig = z.infer<typeof PublicConfigSchema>;

function applyPublicConfig(cfg: PublicConfig) {
  if (typeof cfg.maxSizeMb === 'number' && cfg.maxSizeMb > 0) {
    FILE_CONSTRAINTS.MAX_SIZE_MB = cfg.maxSizeMb;
    FILE_CONSTRAINTS.MAX_SIZE_BYTES = cfg.maxSizeMb * 1024 * 1024;
  }
  if (Array.isArray(cfg.supportedExtensions)) {
    const exts = [...new Set(cfg.supportedExtensions.map((s) => s.toLowerCase().trim()))];
    if (exts.length) FILE_CONSTRAINTS.SUPPORTED_EXTENSIONS = exts;
  }
  if (Array.isArray(cfg.supportedMimeTypes)) {
    const mimes = Array.from(new Set(cfg.supportedMimeTypes.map((s) => String(s).trim())));
    if (mimes.length) FILE_CONSTRAINTS.SUPPORTED_MIME_TYPES = mimes;
  }
}

export async function loadBackendConstraints(opts?: { signal?: AbortSignal }): Promise<void> {
  if (typeof window === 'undefined') return;

  const controller = opts?.signal ? undefined : new AbortController();
  const signal = opts?.signal ?? controller!.signal;
  const timeoutId = controller ? setTimeout(() => controller.abort(), TIMING.CONFIG_FETCH_TIMEOUT) : undefined;

  try {
    const res = await fetch(`${API_BASE_URL}/public-config`, {
      cache: 'no-store',
      signal
    });

    if (!res.ok) {
      console.warn(`Public config unavailable: HTTP ${res.status}`);
      return;
    }
    const json = await res.json();
    const parsed = PublicConfigSchema.safeParse(json);

    if (!parsed.success) {
      console.warn('Public config failed validation; keeping defaults.', parsed.error);
      return;
    }
    applyPublicConfig(parsed.data);
  } catch (err) {
    console.warn('Using default FILE_CONSTRAINTS; could not load from backend.', err);
  } finally {
    if (timeoutId) clearTimeout(timeoutId);
  }
}