import { requireEnv } from '$lib/utils/env';

// ========== API configuration ==========
export const API_BASE_URL: string = requireEnv('VITE_API_BASE_URL');

// ========== File constraints ==========
export interface FileConstraints {
  MAX_SIZE_MB: number;
  MAX_SIZE_BYTES: number;
  SUPPORTED_EXTENSIONS: string[];
  SUPPORTED_MIME_TYPES: string[];
}

const DEFAULT_FILE_CONSTRAINTS: FileConstraints = {
  MAX_SIZE_MB: 10,
  MAX_SIZE_BYTES: 10 * 1024 * 1024,
  SUPPORTED_EXTENSIONS: ['pdf', 'doc', 'docx', 'txt'],
  SUPPORTED_MIME_TYPES: [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain'
  ]
} as const;

export const FILE_CONSTRAINTS: FileConstraints = { ...DEFAULT_FILE_CONSTRAINTS };

// ========== Modal types ==========
export const MODAL_TYPES = {
  LOGIN: 'login',
  SIGNUP: 'signup',
  USER_MENU: 'userMenu'
} as const;

export type ModalType = typeof MODAL_TYPES[keyof typeof MODAL_TYPES];

// ========== Timing (milliseconds) ==========
export const TIMING = {
  TOAST_FADE_DELAY: 4500,
  TOAST_HIDE_DELAY: 5000,
  REDIRECT_DELAY: 1000,
  NETWORK_TIMEOUT: 30000,
  CONFIG_FETCH_TIMEOUT: 7000,
  DEBOUNCE_DELAY: 300
} as const;

// ========== HTTP error messages ==========
const HTTP_ERROR_MESSAGES: Record<number, string> = {
  400: 'Invalid file or request',
  401: 'Authentication required',
  403: 'Access denied',
  413: 'File exceeds size limit',
  415: 'File type not supported',
  422: 'File validation failed',
  500: 'Server error occurred',
  502: 'Service temporarily unavailable',
  503: 'Service unavailable'
};

// ========== Toast configuration ==========
export const TOAST = {
  TYPE: {
    ERROR: 'error',
    WARNING: 'warning',
    SUCCESS: 'success'
  } as const,

  MESSAGE: {
    ERROR: {
      FILE: {
        VALIDATION: {
          EMPTY: 'File is empty. Please select a valid file.',
          OVERSIZED: (sizeLabel: string) =>
              `File too large (${sizeLabel}). Maximum size is ${FILE_CONSTRAINTS.MAX_SIZE_MB}MB.`,
          INVALID_TYPE:
              'Invalid file type detected. Please select a genuine PDF, DOC, DOCX, or TXT file.',
          UNSUPPORTED_TYPE:
              'Unsupported file type. Please upload a PDF, DOC, DOCX, or TXT file.',
          NOT_SELECTED: 'Please select a file before continuing.'
        },
        UPLOAD: {
          FAILED: (error: unknown) => {
            if (typeof error === 'number') {
              const message = HTTP_ERROR_MESSAGES[error] || `Error code ${error}`;
              return `File upload failed: ${message}. Please try again.`;
            }
            return `File upload failed: ${String(error) || 'unknown error'}. Please try again.`;
          },
          CANCELLED: 'File upload was cancelled.',
          TIMEOUT: 'File upload timed out. Please try again.',
          UNKNOWN: 'Unknown error. Please try again.'
        }
      },

      AUTH: {
        LOGIN: 'Login failed. Please try again.',
        SIGNUP: 'Signup failed. Please try again.',
        UNKNOWN: 'Unable to complete request. Please try again.'
      },

      SYSTEM: {
        NETWORK: 'Network error. Please check your connection.',
        SERVER: 'Server error. Please try again later.'
      }
    },

    SUCCESS: {
      FILE: {
        UPLOAD: 'File uploaded successfully.'
      },
      AUTH: {
        LOGIN: 'Logged in successfully.',
        LOGOUT: 'Logged out successfully.',
        SIGNUP: 'Account created successfully.'
      }
    }
  }
} as const;