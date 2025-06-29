declare module '$app/navigation' {
  export function goto(url: string | URL, opts?: {
    replaceState?: boolean;
    noScroll?: boolean;
    keepFocus?: boolean;
    invalidateAll?: boolean;
    state?: any;
  }): Promise<void>;

  export function invalidate(url: string | URL): Promise<void>;
  export function invalidateAll(): Promise<void>;
  export function preloadData(href: string): Promise<void>;
  export function preloadCode(...urls: string[]): Promise<void>;
  export function beforeNavigate(fn: (navigation: any) => void): void;
  export function afterNavigate(fn: (navigation: any) => void): void;
  export function disableScrollHandling(): void;
}

declare module '$app/stores' {
  import type { Readable } from 'svelte/store';
  export const page: Readable<any>;
  export const navigating: Readable<any>;
  export const updated: Readable<boolean>;
}