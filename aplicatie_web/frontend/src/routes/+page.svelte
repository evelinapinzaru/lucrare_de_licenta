<!-- COMMAND TO RUN FRONTEND: npm run dev -->

<script>
  import '../global.css';
  import { Button, Input, Spinner } from 'flowbite-svelte';
  import { goto } from '$app/navigation';
  import FileIcon from '$lib/components/FileIcon.svelte';

  // API constants
  const API_BASE_URL = 'http://localhost:8080';

  // Delay constants
  const TOAST_FADE_DELAY = 4500;
  const TOAST_HIDE_DELAY = 5000;
  const REDIRECT_DELAY = 1000;

  // File constants
  const MAX_FILE_SIZE_MB = 10;
  const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;
  const VALID_FILE_EXTENSIONS = ['pdf', 'doc', 'docx', 'txt'];

  // Toast state
  let isToastVisible = false;
  let toastFadeOut = false;
  let toastMessage = '';
  let toastType = '';

  // Authentication state
  let isLoginModalVisible = false;
  let isSignupModalVisible = false;
  let username = '';
  let password = '';
  let currentUser = '';

  // File state
  let uploadedFile = null;
  // let extractedConcepts = [];
  let isProcessing = false;

  function showToast(message, type = 'error') {
    toastMessage = message;
    toastType = type;
    isToastVisible = true;
    toastFadeOut = false;

    setTimeout(() => { toastFadeOut = true; }, TOAST_FADE_DELAY);
    setTimeout(() => { isToastVisible = false; toastFadeOut = false; }, TOAST_HIDE_DELAY);
  }

  function getFileSizeLabel(fileSizeBytes) {
    const mb = fileSizeBytes / (1024 * 1024);

    if (mb < 1) {
      const kb = fileSizeBytes / 1024;
      return `${Math.trunc(kb)} KB`;
    }
    return `${Math.trunc(mb * 100) / 100} MB`;
  }

  function discardFile() {
    uploadedFile = null;
  }

  function validateFileForUpload(file) {
    const extension = file.name.split('.').pop()?.toLowerCase() || '';

    if (!VALID_FILE_EXTENSIONS.includes(extension)) {
      showToast('Unsupported file type.', 'warning');
      discardFile();
      return;
    }
    if (file.size > MAX_FILE_SIZE_BYTES) {
      showToast(`File too large (${getFileSizeLabel(file.size)}). Maximum size is ${MAX_FILE_SIZE_MB}MB.`, 'warning');
      discardFile();
      return;
    }
    uploadedFile = file;
  }

  async function handleFileUpload() {
    if (uploadedFile) {
      isProcessing = true;
      const formData = new FormData();
      formData.append('file', uploadedFile);

      try {
        const res = await fetch(`${API_BASE_URL}/upload`, {
          method: 'POST',
          body: formData,
          credentials: 'include'
        });

        if (!res.ok) {
          console.error(`File upload failed: ${res.status}`);
          isProcessing = false;
          showToast('File upload failed! Please try again.', 'error');
          return;
        }
        // const data = await res.json();
        // extractedConcepts = data.extractedConcepts || [];
        showToast('File uploaded successfully!', 'success');
        setTimeout(() => { goto('/exercises'); }, REDIRECT_DELAY);
      } catch (err) {
        console.error('File upload error:', err);
        isProcessing = false;

        if (err.name === 'AbortError') {
          showToast('File upload was cancelled', 'info');
        } else if (!navigator.onLine) {
          showToast('No internet connection! Please check your network.', 'error');
        } else if (err.message && err.message.includes('timeout')) {
          showToast('File upload timed out! Please try again.', 'error');
        } else {
          showToast('File upload failed! Please try again.', 'error');
        }
      }
    } else showToast('Please select a file before continuing.', 'warning');
  }

  function toggleLoginModal() {
    isLoginModalVisible = !isLoginModalVisible;
    isSignupModalVisible = false;
  }

  function toggleSignupModal() {
    isSignupModalVisible = !isSignupModalVisible;
    isLoginModalVisible = false;
  }

  async function register() {
    const form = new FormData();
    form.append('username', username);
    form.append('password', password);
    const res = await fetch(`${API_BASE_URL}/register`, {
      method: 'POST',
      body: form
    });
    const data = await res.json();
    const messageType = data.message ? 'success' : 'error';
    showToast(data.message || data.error, messageType);

    if (data.message) {
      isSignupModalVisible = false;
      username = '';
      password = '';
    }
  }

  async function login() {
    const form = new FormData();
    form.append('username', username);
    form.append('password', password);
    const res = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      credentials: 'include',
      body: form
    });
    const data = await res.json();

    if (data.message) {
      currentUser = username;
      isLoginModalVisible = false;
      username = '';
      password = '';
    } else {
      showToast(data.error || 'Login failed!', 'error');
    }
  }

  async function logout() {
    await fetch(`${API_BASE_URL}/logout`, {
      method: 'POST',
      credentials: 'include'
    });
    currentUser = '';
  }
</script>

<svelte:head>
  <link href="https://cdnjs.cloudflare.com/ajax/libs/flowbite/2.2.1/flowbite.min.css" rel="stylesheet" />
</svelte:head>

<style>
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

  .toast {
    position: fixed;
    top: 100px;
    left: 50%;
    transform: translateX(-50%);
    color: white;
    padding: 15px 25px;
    border-radius: 12px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    font-weight: 600;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 10px;
    animation: slideDown 0.3s ease-out;
    border: 1px solid rgba(255, 255, 255, 0.2);
    transition: opacity 0.4s ease-out, transform 0.4s ease-out;
  }

  .toast.error {
    background: #D0342C; /* Error color - red */
  }

  .toast.warning {
    background: #EED202; /* Warning color - yellow */
    color: #333;
  }

  .toast.success {
    background: #28a745; /* Success color - green */
  }

  .toast.fade-out {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }

  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateX(-50%) translateY(-20px);
    }
    to {
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }
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

<!-- Toast Notification -->
{#if isToastVisible }
  <div class="toast {toastType}"
       class:fade-out={toastFadeOut}>
    {#if toastType === 'error'}
      <svg class="w-5 h-5 flex-shrink-0"
           fill="currentColor"
           viewBox="0 0 20 20">
        <path fill-rule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clip-rule="evenodd" />
      </svg>
    {:else if toastType === 'warning'}
      <svg class="w-5 h-5 flex-shrink-0"
           fill="currentColor"
           viewBox="0 0 20 20">
        <path fill-rule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clip-rule="evenodd" />
      </svg>
    {:else if toastType === 'success'}
      <svg class="w-5 h-5 flex-shrink-0"
           fill="currentColor"
           viewBox="0 0 20 20">
        <path fill-rule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
              clip-rule="evenodd" />
      </svg>
    {/if}
    <span>{toastMessage}</span>
  </div>
{/if}

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
               viewBox="0 0 20 20">
            <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
          </svg>
        </div>
        <span class="text-2xl font-bold text-gray-800">CodeFlow</span>
      </a>
    </div>

    <!-- Authentication Buttons -->
    <div class="flex items-center space-x-3 relative mr-8"
         style="margin-right: 3rem;">
      {#if currentUser}
        <span class="text-gray-700 text-sm font-medium">Welcome, {currentUser}!</span>
        <Button onclick={logout}
                outline color="red"
                size="sm">Logout</Button>
      {:else}
        <Button onclick={toggleLoginModal}
                outline color="dark"
                size="sm">Log In</Button>
        <Button onclick={toggleSignupModal}
                outline color="purple"
                size="sm">Sign Up</Button>

        <!-- Login dropdown -->
        {#if isLoginModalVisible}
          <div class="auth-dropdown">
            <form class="flex flex-col space-y-2"
                  onsubmit={(e) => { e.preventDefault(); login(); }}>
              <!-- Title -->
              <h3 class="text-base font-medium text-gray-900 leading-tight">Sign in to CodeFlow</h3>
              <!-- Username & password textboxes + login button -->
              <div class="flex items-center space-x-2">
                <Input type="text"
                       bind:value={username}
                       placeholder="Username"
                       required class="h-8 text-sm flex-1" />
                <Input type="password"
                       bind:value={password}
                       placeholder="Password"
                       required class="h-8 text-sm flex-1" />
                <Button type="submit"
                        color="dark"
                        size="sm"
                        class="flex-1"
                        style="height: 2rem;">
                  Log in
                </Button>
              </div>
              <!-- Footer text -->
              <div class="text-xs font-medium text-gray-500">
                Don't have an account yet?
                <button type="button"
                        onclick={toggleSignupModal}
                        class="text-purple-600 hover:text-purple-800 hover:underline">Sign up here</button>
              </div>
            </form>
          </div>
        {/if}

        <!-- Signup dropdown -->
        {#if isSignupModalVisible}
          <div class="auth-dropdown">
            <form class="flex flex-col space-y-2"
                  onsubmit={(e) => { e.preventDefault(); register(); }}>
              <!-- Title -->
              <h3 class="text-base font-medium text-gray-900 leading-tight">Create your CodeFlow account</h3>
              <!-- Username & password textboxes + signup button -->
              <div class="flex items-center space-x-2">
                <Input type="text"
                       bind:value={username}
                       placeholder="Username"
                       required class="h-8 text-sm flex-1" />
                <Input type="password"
                       bind:value={password}
                       placeholder="Password"
                       required class="h-8 text-sm flex-1" />
                <Button type="submit"
                        color="dark"
                        size="sm"
                        class="flex-1"
                        style="height: 2rem;">
                  Sign up
                </Button>
              </div>
              <!-- Footer text -->
              <div class="text-xs font-medium text-gray-500">
                Already have an account?
                <button type="button"
                        onclick={toggleLoginModal}
                        class="text-purple-600 hover:text-purple-800 hover:underline">Log in here</button>
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
      <h1 class="text-6xl md:text-7xl font-bold text-white mb-8">Welcome to CodeFlow</h1>
      <p class="text-2xl md:text-3xl text-white mb-12 max-w-3xl mx-auto leading-relaxed">
        Choose a file and start practicing your programming skills.
      </p>
      <!-- File section -->
      <div class="space-y-12 pt-16">
        <div class="flex items-center justify-center w-full max-w-2xl mx-auto">
          {#if !uploadedFile}
            <label for="file-upload"
                   class="flex flex-col items-center justify-center w-full h-32 border-2 border-white/30 border-dashed rounded-[24px] cursor-pointer bg-white/10 hover:bg-white/20 transition-all duration-300">
              <div class="flex flex-col items-center justify-center pt-5 pb-6">
                <svg class="w-8 h-8 mb-4 text-white"
                     fill="none"
                     stroke="currentColor"
                     viewBox="0 0 24 24">
                  <path stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p class="mb-2 text-sm text-white font-semibold">
                  Click to upload / drag and drop your learning materials
                </p>
                <p class="text-xs text-white">PDF, DOC, DOCX, TXT (MAX. 10MB)</p>
              </div>
              <input id="file-upload"
                     type="file"
                     class="hidden"
                     accept=".pdf,.doc,.docx,.txt"
                     onchange={(e) => validateFileForUpload(e.target.files[0])}
                     disabled={isProcessing} />
            </label>
          {:else}
            <!-- Selected file preview -->
            <div class="w-full h-32 border-2 border-white/30 border-dashed rounded-[24px] p-1">
              <div class="file-display w-full rounded-[20px] flex items-center justify-between px-8 text-white">
                <div class="flex items-center space-x-6">
                  <div class="flex items-center justify-center">
                    <FileIcon filename={uploadedFile.name}
                              size="w-12 h-12" />
                  </div>
                  <div class="text-left">
                    <p class="font-semibold text-base">{uploadedFile.name}</p>
                    <p class="text-sm opacity-80">{getFileSizeLabel(uploadedFile.size)}</p>
                  </div>
                </div>
                <button
                        class="remove-file-btn w-12 h-12 rounded-full border border-white/50 text-white bg-transparent transition-colors flex items-center justify-center"
                        onclick={discardFile}
                        title="Remove file"
                        aria-label="Remove uploaded file">
                  <svg class="w-6 h-6"
                       fill="none"
                       stroke="currentColor"
                       viewBox="0 0 24 24">
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

        <!-- 'Code it' Button -->
        <div class="flex justify-center pt-8">
          <Button onclick={handleFileUpload}
                  color="purple"
                  size="lg"
                  disabled={isProcessing}
                  class="flex items-center space-x-3 rounded-[24px] px-6 py-3 shadow-lg">
            {#if isProcessing}
              <Spinner class="me-3" size="4" color="gray" />
              Processing...
            {:else}
              <svg class="w-5 h-5 me-3"
                   fill="none"
                   stroke="currentColor"
                   viewBox="0 0 24 24">
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