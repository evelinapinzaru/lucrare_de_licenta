<!-- COMMAND TO RUN FRONTEND: pnpm run dev -->

<script lang="ts">
  // Framework imports
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  // Third-party imports
  import { Button, Input, Spinner } from 'flowbite-svelte';

  // Internal imports
  import { toast, toastSuccess, toastWarning, toastError } from '$lib/stores/toast';
  import { API_BASE_URL, FILE_CONSTRAINTS, MODAL_TYPES, TIMING, TOAST } from '$lib/utils/constants';
  import { loadBackendConstraints } from '$lib/services/config';
  import FileIcon from '$lib/components/FileIcon.svelte';
  import type { ModalType } from '$lib/utils/constants';

  // --- Local types
  type ToastMessage = string;

  // UI state
  let isHovering = false;

  // Authentication state
  let activeModal: ModalType | null = null;
  let username = '';
  let password = '';
  let currentUser = '';
  let currentUserAvatar: { initial?: string; bg_color?: string } | null = null;
  let isLoggingIn = false;
  let isSigningUp = false;

  // File state
  let selectedFile: File | null = null;
  // let extractedConcepts = [];
  let isProcessing = false;
  let isDragOver = false;
  let fileInput: HTMLInputElement | undefined;

  $: acceptAttribute = FILE_CONSTRAINTS.SUPPORTED_EXTENSIONS.map(ext => `.${ext}`).join(',');
  $: supportedTypesText = FILE_CONSTRAINTS.SUPPORTED_EXTENSIONS.map(ext => ext.toUpperCase()).join(', ');

  onMount(async () => {
    await loadBackendConstraints();
  });

  function getFileSizeLabel(fileSizeBytes: number): string {
    const mb = fileSizeBytes / (1024 * 1024);

    if (mb < 1) {
      const kb = fileSizeBytes / 1024;
      return `${Math.trunc(kb)} KB`;
    }
    return `${Math.trunc(mb * 100) / 100} MB`;
  }

  function discardFile(): void {
    selectedFile = null;
    if (fileInput) fileInput.value = '';
  }

  function validateFileForUpload(file: File): boolean {
    const extension = file.name.split('.').pop()?.toLowerCase() || '';

    if (file.size === 0) {
      toastWarning(TOAST.MESSAGE.ERROR.FILE.VALIDATION.EMPTY);
      discardFile();
      return false;
    }
    if (!FILE_CONSTRAINTS.SUPPORTED_EXTENSIONS.includes(extension)) {
      toastWarning(TOAST.MESSAGE.ERROR.FILE.VALIDATION.UNSUPPORTED_TYPE);
      discardFile();
      return false;
    }
    if (!FILE_CONSTRAINTS.SUPPORTED_MIME_TYPES.includes(file.type)) {
      toastWarning(TOAST.MESSAGE.ERROR.FILE.VALIDATION.INVALID_TYPE);
      discardFile();
      return false;
    }
    if (file.size > FILE_CONSTRAINTS.MAX_SIZE_BYTES) {
      toastWarning(TOAST.MESSAGE.ERROR.FILE.VALIDATION.OVERSIZED(getFileSizeLabel(file.size)));
      discardFile();
      return false;
    }
    selectedFile = file;
    return true;
  }

  async function handleFileUpload(): Promise<void> {
    if (!selectedFile) {
      toastWarning(TOAST.MESSAGE.ERROR.FILE.VALIDATION.NOT_SELECTED);
      return;
    }

    isProcessing = true;
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const res = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });

      if (!res.ok) {
        console.error(`File upload failed: ${res.status}`);
        toastError(TOAST.MESSAGE.ERROR.FILE.UPLOAD.FAILED(res.status));
        return;
      }
      // const data = await res.json();
      // extractedConcepts = data.extractedConcepts || [];
      toastSuccess(TOAST.MESSAGE.SUCCESS.FILE.UPLOAD);
      setTimeout(() => { goto('/exercises'); }, TIMING.REDIRECT_DELAY);
    } catch (error: unknown) {
      console.error('File upload error:', error);
      const e = error as { name?: string; message?: string };

      if (e?.name === 'AbortError') {
        toastWarning(TOAST.MESSAGE.ERROR.FILE.UPLOAD.CANCELLED);
      } else if (!navigator.onLine) {
        toastError(TOAST.MESSAGE.ERROR.SYSTEM.NETWORK);
      } else if (e?.message?.includes?.('timeout')) {
        toastError(TOAST.MESSAGE.ERROR.FILE.UPLOAD.TIMEOUT);
      } else {
        toastError(TOAST.MESSAGE.ERROR.FILE.UPLOAD.FAILED(e?.message ?? 'unknown error'));
      }
    } finally {
      isProcessing = false;
    }
  }

  function handleModalToggle(modalType: ModalType, event: MouseEvent): void {
    event.stopPropagation();
    toast.hide();
    activeModal = activeModal === modalType ? null : modalType;
  }

  function handleAuthError(error: unknown, context: 'signup' | 'login'): void {
    console.error(`Auth operation '${context}' error:`, error);
    const e = error as Error;

    if (e?.name === 'TypeError' && e?.message?.includes?.('fetch')) {
      toastError(TOAST.MESSAGE.ERROR.SYSTEM.NETWORK);
    } else if (e?.message?.includes?.('Unexpected token')) {
      toastError(TOAST.MESSAGE.ERROR.SYSTEM.SERVER);
    } else if (context === 'signup') {
      toastError(TOAST.MESSAGE.ERROR.AUTH.SIGNUP);
    } else if (context === 'login') {
      toastError(TOAST.MESSAGE.ERROR.AUTH.LOGIN);
    } else {
      toastError(TOAST.MESSAGE.ERROR.AUTH.UNKNOWN);
    }
  }

  async function signup(): Promise<void> {
    if (isSigningUp) return;
    isSigningUp = true;

    try {
      const form = new FormData();
      form.append('username', username);
      form.append('password', password);
      const res = await fetch(`${API_BASE_URL}/signup`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      if (!res.ok) {
        handleAuthError(new Error(`HTTP error! status: ${res.status}`), 'signup');
        return;
      }
      const data: { message?: ToastMessage; error?: string; username?: string; avatar?: any } = await res.json();
      data.message ? toastSuccess(data.message) : toastError(data.error ?? '');

      if (data.message) {
        currentUser = data.username ?? '';
        currentUserAvatar = data.avatar ?? null;
        activeModal = null;
        password = '';
      }
    } catch (error) {
      handleAuthError(error, 'signup');
    } finally {
      isSigningUp = false;
    }
  }

  async function login(): Promise<void> {
    if (isLoggingIn) return;
    isLoggingIn = true;

    try {
      const form = new FormData();
      form.append('username', username);
      form.append('password', password);
      const res = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      if (!res.ok) {
        handleAuthError(new Error(`HTTP error! status: ${res.status}`), 'login');
        return;
      }
      const data: { message?: ToastMessage; error?: string; username?: string; avatar?: any } = await res.json();

      if (data.message) {
        currentUser = data.username ?? '';
        currentUserAvatar = data.avatar ?? null;
        activeModal = null;
        username = '';
        password = '';
        toastSuccess(TOAST.MESSAGE.SUCCESS.AUTH.LOGIN);
      } else {
        toastError(data.error || TOAST.MESSAGE.ERROR.AUTH.LOGIN);
      }
    } catch (error) {
      handleAuthError(error, 'login');
    } finally {
      isLoggingIn = false;
    }
  }

  async function logout(): Promise<void> {
    try {
      const res = await fetch(`${API_BASE_URL}/logout`, {
        method: 'POST',
        credentials: 'include'
      });

      if (!res.ok) {
        console.warn('Logout request failed, but clearing local session anyway');
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      currentUser = '';
      currentUserAvatar = null;
      username = '';
      password = '';
      selectedFile = null;
      activeModal = null;
      toastSuccess(TOAST.MESSAGE.SUCCESS.AUTH.LOGOUT);
    }
  }

  function handleKeydown(event: KeyboardEvent): void {
    if (event.key === 'Escape') {
      activeModal = null;
    }
  }

  function handleOutsideClick(event: MouseEvent): void {
    const target = event.target as HTMLElement | null;
    if (!target?.closest('.auth-dropdown')) {
      activeModal = null;
    }
  }

  function handleDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    isDragOver = true;
  }

  function handleDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    isDragOver = false;
  }

  function handleDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    isDragOver = false;

    if (isProcessing) return;

    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      validateFileForUpload(files[0]);
    }
  }
</script>

<svelte:window
        on:keydown={handleKeydown}
        on:click={handleOutsideClick} />

<style>
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }

  .auth-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    margin-top: 25px;
    width: 400px;
    background: white;
    border-radius: 24px;
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
    z-index: 50;
    padding: 15px 20px;
    border: 1px solid #e5e7eb;
  }

  .drag-over {
    border-color: #a855f7 !important;
    background-color: rgba(255, 255, 255, 0.2) !important;
  }

  .file-display {
    background: linear-gradient(135deg, #6F2DA8 0%, #9333ea 100%);
    height: 120px;
  }

  .remove-file-btn {
    transition: all 0.2s;
  }

  .remove-file-btn:hover {
    background-color: rgba(255, 255, 255, 0.2) !important;
  }
</style>

<!-- Navbar -->
<nav class="bg-white/70 backdrop-blur-md border-b border-gray-200/30">
  <div class="flex justify-between items-center h-16">
    <!-- Logo -->
    <div class="flex items-center">
      <a href="/"
         class="flex items-center space-x-3">
        <div class="w-8 h-8 bg-gradient-to-r from-gray-800 to-black rounded-lg flex items-center justify-center">
          <svg class="w-5 h-5 text-white"
               fill="currentColor"
               viewBox="0 0 20 20"
               aria-hidden="true"
               focusable="false">
            <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
          </svg>
        </div>
        <span class="text-2xl font-bold text-gray-800">
          CodeFlow
        </span>
      </a>
    </div>

    <!-- Authentication Buttons -->
    <div class="flex items-center space-x-3 relative mr-8"
         style="margin-right: 3rem;">
      {#if currentUser}
        <button class="w-8 h-8 rounded-full flex items-center justify-center text-white font-semibold text-sm focus:outline-none transition-all"
                style:background-color={currentUserAvatar?.['bg_color'] || '#6B7280'}
                style:box-shadow={activeModal === MODAL_TYPES.USER_MENU ? '0 0 0 3px white, 0 0 0 5px #a855f7' :
                (isHovering ? '0 0 0 3px white, 0 0 0 5px #d1d5db' : undefined)}
                onmouseenter={() => isHovering = true}
                onmouseleave={() => isHovering = false}
                onclick={(e) => handleModalToggle(MODAL_TYPES.USER_MENU, e)}
                title="Logged in as {currentUser}"
                aria-label="User avatar for {currentUser}, click to open menu"
                aria-expanded={activeModal === MODAL_TYPES.USER_MENU}
                aria-haspopup="true">
          {currentUserAvatar?.initial || '?'}
        </button>

        <!-- User menu dropdown -->
        {#if activeModal === MODAL_TYPES.USER_MENU}
          <div class="auth-dropdown"
               role="menu">
            <div class="flex flex-col space-y-3">
              <!-- User info header -->
              <div class="flex items-center space-x-3 pb-3 border-b border-gray-200">
                <div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold"
                     style:background-color={currentUserAvatar?.['bg_color'] || '#6B7280'}>
                  {currentUserAvatar?.initial || '?'}
                </div>
                <div>
                  <p class="font-medium text-gray-900">{currentUser}</p>
                  <p class="text-sm text-gray-500">Signed in</p>
                </div>
              </div>

              <!-- Menu options -->
              <div class="space-y-1">
                <Button onclick={logout}
                        color="red"
                        outline
                        size="sm"
                        class="w-full justify-start">
                  <svg class="w-4 h-4 mr-2"
                       fill="none"
                       stroke="currentColor"
                       viewBox="0 0 24 24"
                       aria-hidden="true"
                       focusable="false">
                    <path stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
                  </svg>
                  Sign out
                </Button>
              </div>
            </div>
          </div>
        {/if}
      {:else}
        <Button onclick={(e: MouseEvent) => handleModalToggle(MODAL_TYPES.LOGIN, e)}
                outline
                color="dark"
                size="sm"
                aria-expanded={activeModal === MODAL_TYPES.LOGIN}
                aria-haspopup="true">
          Log In
        </Button>
        <Button onclick={(e: MouseEvent) => handleModalToggle(MODAL_TYPES.SIGNUP, e)}
                outline
                color="purple"
                size="sm"
                aria-expanded={activeModal === MODAL_TYPES.SIGNUP}
                aria-haspopup="true">
          Sign Up
        </Button>

        <!-- Login dropdown -->
        {#if activeModal === MODAL_TYPES.LOGIN}
          <div class="auth-dropdown"
               role="dialog"
               aria-modal="true"
               aria-labelledby="login-title"
               aria-describedby="login-form">
            <form id="login-form"
                  class="flex flex-col space-y-2"
                  onsubmit={(e) => { e.preventDefault(); login(); }}>
              <!-- Title -->
              <h3 id="login-title"
                  class="text-base font-medium text-gray-900 leading-tight">
                Sign in to CodeFlow
              </h3>
              <!-- Username & password textboxes + login button -->
              <div class="flex items-center space-x-2">
                <Input type="text"
                       bind:value={username}
                       placeholder="Username"
                       required
                       class="h-8 text-sm flex-1"
                       aria-label="Username"
                       autocomplete="username" />
                <Input type="password"
                       bind:value={password}
                       placeholder="Password"
                       required
                       class="h-8 text-sm flex-1"
                       aria-label="Password"
                       autocomplete="current-password" />
                <Button type="submit"
                        color="dark"
                        size="sm"
                        class="flex-1"
                        style="height: 2rem;"
                        disabled={isLoggingIn}>
                  {#if isLoggingIn}
                    Logging in...
                  {:else}
                    Log in
                  {/if}
                </Button>
              </div>
              <!-- Footer text -->
              <div class="text-xs font-medium text-gray-500">
                Don't have an account yet?
                <button type="button"
                        onclick={(e) => handleModalToggle(MODAL_TYPES.SIGNUP, e)}
                        class="text-purple-600 hover:text-purple-800 hover:underline">
                  Sign up here
                </button>
              </div>
            </form>
          </div>
        {/if}

        <!-- Signup dropdown -->
        {#if activeModal === MODAL_TYPES.SIGNUP}
          <div class="auth-dropdown"
               role="dialog"
               aria-modal="true"
               aria-labelledby="signup-title"
               aria-describedby="signup-form">
            <form id="signup-form"
                  class="flex flex-col space-y-2"
                  onsubmit={(e) => { e.preventDefault(); signup(); }}>
              <!-- Title -->
              <h3 id="signup-title"
                  class="text-base font-medium text-gray-900 leading-tight">
                Create your CodeFlow account
              </h3>
              <!-- Username & password textboxes + signup button -->
              <div class="flex items-center space-x-2">
                <Input type="text"
                       bind:value={username}
                       placeholder="Username"
                       required
                       class="h-8 text-sm flex-1"
                       aria-label="Username"
                       autocomplete="username" />
                <Input type="password"
                       bind:value={password}
                       placeholder="Password"
                       required
                       class="h-8 text-sm flex-1"
                       aria-label="Password"
                       autocomplete="new-password" />
                <Button type="submit"
                        color="dark"
                        size="sm"
                        class="flex-1"
                        style="height: 2rem;"
                        disabled={isSigningUp}>
                  {#if isSigningUp}
                    Signing up...
                  {:else}
                    Sign up
                  {/if}
                </Button>
              </div>
              <!-- Footer text -->
              <div class="text-xs font-medium text-gray-500">
                Already have an account?
                <button type="button"
                        onclick={(e) => handleModalToggle(MODAL_TYPES.LOGIN, e)}
                        class="text-purple-600 hover:text-purple-800 hover:underline">
                  Log in here
                </button>
              </div>
            </form>
          </div>
        {/if}
      {/if}
    </div>
  </div>
</nav>

<!-- Main area -->
<main class="min-h-screen"
      style="background-color: #1E1E1E; display: flex; align-items: center; justify-content: center;">
  <div class="relative py-20 px-4 sm:px-6 lg:px-8 w-full">
    <div class="max-w-5xl mx-auto text-center">
      <h1 class="text-6xl md:text-7xl font-bold text-white mb-8">
        Welcome to CodeFlow
      </h1>
      <p class="text-2xl md:text-3xl text-white mb-12 max-w-3xl mx-auto leading-relaxed">
        Choose a file and start practicing your programming skills.
      </p>
      <!-- File section -->
      <div class="space-y-12 pt-16">
        <div class="flex items-center justify-center w-full max-w-2xl mx-auto">
          {#if !selectedFile}
            <input id="file-upload"
                   type="file"
                   class="hidden"
                   accept={acceptAttribute}
                   bind:this={fileInput}
                   onchange={(e) => {
                       const file = e.currentTarget.files?.[0];
                       if (file) validateFileForUpload(file);
                     }}
                   disabled={isProcessing} />
            <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
            <label for="file-upload"
                   class="flex flex-col items-center justify-center w-full h-32 border-2 border-white/30 border-dashed rounded-[24px] cursor-pointer bg-white/10 hover:bg-white/20 transition-all duration-300 pt-5 pb-6"
                   class:drag-over={isDragOver}
                   aria-describedby="file-instructions upload-status"
                   aria-busy={isProcessing}
                   ondragover={handleDragOver}
                   ondragleave={handleDragLeave}
                   ondrop={handleDrop}
                   onkeydown={(e) => {
                     if ((e.key === 'Enter' || e.key === ' ') && !isProcessing) {
                       e.preventDefault();
                       fileInput?.click();
                     }
                   }}>
              <svg class="w-8 h-8 mb-4 text-white pointer-events-none"
                   fill="none"
                   stroke="currentColor"
                   viewBox="0 0 24 24"
                   aria-hidden="true"
                   focusable="false">
                <path stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <span class="mb-2 text-sm text-white font-semibold pointer-events-none">
                  Click to upload / drag and drop your learning materials
                </span>
              <span class="text-xs text-white pointer-events-none">
                {supportedTypesText} (MAX. {FILE_CONSTRAINTS.MAX_SIZE_MB}MB)
              </span>
            </label>
            <div id="file-instructions"
                 class="sr-only">
              Supported file formats: {supportedTypesText}. Maximum size: {FILE_CONSTRAINTS.MAX_SIZE_MB}MB.
            </div>
          {:else}
            <!-- Selected file preview -->
            <div class="w-full h-32 border-2 border-white/30 border-dashed rounded-[24px] p-1">
              <div class="file-display w-full rounded-[20px] flex items-center justify-between px-8 text-white">
                <div class="flex items-center space-x-6">
                  <div class="flex items-center justify-center">
                    <FileIcon filename={selectedFile.name}
                              sizeClass="w-12 h-12" />
                  </div>
                  <div class="text-left">
                    <p class="font-semibold text-base">{selectedFile.name}</p>
                    <p class="text-sm opacity-80">{getFileSizeLabel(selectedFile.size)}</p>
                  </div>
                </div>
                <button type="button"
                        class="remove-file-btn w-12 h-12 rounded-full border border-white/50 text-white bg-transparent transition-colors flex items-center justify-center"
                        onclick={discardFile}
                        title="Remove file"
                        aria-label="Remove uploaded file">
                  <svg class="w-6 h-6"
                       fill="none"
                       stroke="currentColor"
                       viewBox="0 0 24 24"
                       aria-hidden="true"
                       focusable="false">
                    <path stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          {/if}
        </div>
        <div id="upload-status"
             aria-live="polite"
             aria-atomic="true"
             class={!isProcessing && !selectedFile ? "sr-only" : ""}>
          {#if isProcessing}
            File is being processed, please wait.
          {:else if !selectedFile}
            Please select a file to upload.
          {:else}
            Ready to upload {selectedFile.name}.
          {/if}
        </div>
        <!-- 'Code it' Button -->
        <div class="flex justify-center pt-8">
          <Button onclick={handleFileUpload}
                  color="purple"
                  size="lg"
                  disabled={isProcessing || !selectedFile}
                  class="flex items-center space-x-3 rounded-[24px] px-6 py-3 shadow-lg"
                  aria-describedby="upload-status">


            {#if isProcessing}
              <Spinner class="me-3"
                       size="4"
                       color="gray"
                       aria-hidden="true" />
              Processing...
            {:else}
              <svg class="w-5 h-5 me-3"
                   fill="none"
                   stroke="currentColor"
                   viewBox="0 0 24 24"
                   aria-hidden="true"
                   focusable="false">
                <path stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
              </svg>
              Code it
            {/if}
          </Button>
        </div>
      </div>
    </div>
  </div>
</main>