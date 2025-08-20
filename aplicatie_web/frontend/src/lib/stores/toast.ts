import { writable, type Writable, type Readable } from 'svelte/store';
import { TOAST, TIMING } from '$lib/utils/constants';

// ========== Types ==========
export type ToastType = typeof TOAST.TYPE[keyof typeof TOAST.TYPE];

export interface ToastState {
  visible: boolean;
  fadeOut: boolean;
  message: string;
  type: ToastType | null;
}

// ========== Store ==========
const blank = (): ToastState => ({
  visible: false,
  fadeOut: false,
  message: '',
  type: null
});
const toastState: Writable<ToastState> = writable(blank());

let fadeTimeout: ReturnType<typeof setTimeout> | null = null;
let hideTimeout: ReturnType<typeof setTimeout> | null = null;

// ========== Internal functions ==========
function showToast(message: string, type: ToastType) {
  hideToast();

  toastState.set({ visible: true, fadeOut: false, message, type });

  fadeTimeout = setTimeout(() => {
    toastState.update((state) => ({ ...state, fadeOut: true }));
  }, TIMING.TOAST_FADE_DELAY);

  hideTimeout = setTimeout(() => {
    toastState.set(blank());
  }, TIMING.TOAST_HIDE_DELAY);
}

function hideToast() {
  if (fadeTimeout) { clearTimeout(fadeTimeout); fadeTimeout = null; }
  if (hideTimeout) { clearTimeout(hideTimeout); hideTimeout = null; }
  toastState.set(blank());
}

// ========== Public API ==========
export const toast: Readable<ToastState> & { hide: () => void } = {
  subscribe: toastState.subscribe,
  hide: hideToast
};

export const toastSuccess = (msg: string) => showToast(msg, TOAST.TYPE.SUCCESS);
export const toastWarning = (msg: string) => showToast(msg, TOAST.TYPE.WARNING);
export const toastError   = (msg: string) => showToast(msg, TOAST.TYPE.ERROR);