<!-- COMMAND TO RUN FRONTEND: npm run dev -->

<script>
    import '../global.css';
    import { Button, Input } from 'flowbite-svelte';
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';

    // User authentication functionality
    let isLoginModalVisible = false;
    let isSignupModalVisible = false;
    let username = '';
    let password = '';
    let sessionUser = '';

    // File upload functionality
	let uploadedFile = null;
    let extractedConcepts = [];
    let isLoading = false;

    // Toast warning
    let showFileWarning = false;
    let toastFadeOut = false;

    onMount(() => {
      uploadedFile = null;
    });

    function toggleLoginModal() {
      isLoginModalVisible = !isLoginModalVisible;
      isSignupModalVisible = false;
    }

    function toggleSignupModal() {
      isSignupModalVisible = !isSignupModalVisible;
      isLoginModalVisible = false;
    }

    function showFileWarningToast() {
        showFileWarning = true;
        toastFadeOut = false;

        setTimeout(() => {
            toastFadeOut = true;
        }, 4500);

        setTimeout(() => {
            showFileWarning = false;
            toastFadeOut = false;
        }, 5000);
    }

    function removeUploadedFile() {
        uploadedFile = null;
    }

    function getFileIcon(filename) {
        const extension = filename.split(".").pop().toLowerCase();
        if (extension === "pdf") return "📄";
        if (["doc", "docx"].includes(extension)) return "📝";
        if (extension === "txt") return "📃";
        return "📄";
    }

	async function handleFileUpload() {
		if (uploadedFile) {
           isLoading = true;

		const formData = new FormData();
		formData.append("file", uploadedFile);
		try {
			const res = await fetch("http://localhost:8080/upload", {
				method: "POST",
				body: formData,
				credentials: "include"
			});

            if (!res.ok) {
              throw new Error(`HTTP error! status: ${res.status}`);
            }

			const data = await res.json();
			extractedConcepts = data.extractedConcepts || [];

            setTimeout(() => {
              goto("/exercises");
            }, 1000);
		} catch (err) {
			console.error("Upload error:", err);
            isLoading = false;
		}
        } else {
            showFileWarningToast();
        }
	}

  async function register() {
    const form = new FormData();
    form.append("username", username);
    form.append("password", password);
    const res = await fetch("http://localhost:8080/register", {
      method: "POST",
      body: form
    });
    const data = await res.json();
    alert(data.message || data.error);
    if (data.message) {
      isSignupModalVisible = false;
      username = '';
      password = '';
    }
  }

  async function login() {
    const form = new FormData();
    form.append("username", username);
    form.append("password", password);
    const res = await fetch("http://localhost:8080/login", {
      method: "POST",
      credentials: "include",
      body: form
    });
    const data = await res.json();
    if (data.message) {
      sessionUser = username;
      isLoginModalVisible = false;
      username = '';
      password = '';
    } else {
      alert(data.error || "Login failed!");
    }
  }

  async function logout() {
    await fetch("http://localhost:8080/logout", {
      method: "POST",
      credentials: "include"
    });
    sessionUser = '';
  }
</script>

<svelte:head>
  <link href="https://cdnjs.cloudflare.com/ajax/libs/flowbite/2.2.1/flowbite.min.css" rel="stylesheet" />
</svelte:head>

<style>
  .custom-purple-hover:hover {
    background-color: #6F2DA8 !important;
    color: white !important;
  }

  .auth-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    margin-top: 24px;
    width: 400px;
    background: white;
    border-radius: 24px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
    z-index: 50;
    padding: 12px 20px;
    border: 1px solid #e5e7eb;
  }

  .toast-warning {
    position: fixed;
    top: 100px;
    left: 50%;
    transform: translateX(-50%);
    background: #D0342C;
    color: white;
    padding: 16px 24px;
    border-radius: 24px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 1000;
    font-weight: 600;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 12px;
    animation: slideDown 0.3s ease-out;
    border: 1px solid rgba(255, 255, 255, 0.2);
    transition: opacity 0.4s ease-out, transform 0.4s ease-out;
  }

  .toast-warning.fade-out {
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
    height: 120px; /* Fixed height to match container minus padding */
  }

  .remove-file-btn:hover {
    background-color: rgba(255, 255, 255, 0.2) !important;
  }

</style>

<!-- Toast Warning -->
{#if showFileWarning}
  <div class="toast-warning" class:fade-out={toastFadeOut}>
    <svg class="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
    </svg>
    <span>Please select a file before continuing.</span>
  </div>
{/if}

<!-- Navbar -->
<nav class="bg-white/70 backdrop-blur-md border-b border-gray-200/30">
  <div class="flex justify-between items-center h-16">
      <!-- Logo -->
      <div class="flex items-center" style="margin-left: 0rem;">
        <a href="/" class="flex items-center space-x-3">
          <div class="w-8 h-8 bg-gradient-to-r from-gray-800 to-black rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
            </svg>
          </div>
          <span class="text-2xl font-bold text-gray-800">
            CodeFlow
          </span>
        </a>
      </div>

      <!-- Authentication Buttons -->
      <div class="flex items-center space-x-3 relative mr-8" style="margin-right: 3rem;">
        {#if sessionUser}
          <span class="text-gray-700 text-sm font-medium">Welcome, {sessionUser}!</span>
          <Button onclick={logout} outline color="red" size="sm">Logout</Button>
        {:else}
          <Button onclick={toggleLoginModal} outline color="dark" size="sm">Log In</Button>
          <Button onclick={toggleSignupModal} outline color="purple" size="sm">Sign Up</Button>

          <!-- Login dropdown -->
          {#if isLoginModalVisible}
            <div class="auth-dropdown">
              <form class="flex flex-col space-y-2" onsubmit={(e) => { e.preventDefault(); login(); }}>
                <!-- Title -->
                <h3 class="text-base font-medium text-gray-900 leading-tight">Sign in to CodeFlow</h3>

                <!-- Username & password textboxes + login button -->
                <div class="flex items-center space-x-2">
                  <Input type="text" bind:value={username} placeholder="Username" required class="h-8 text-sm flex-1" />
                  <Input type="password" bind:value={password} placeholder="Password" required class="h-8 text-sm flex-1" />
                  <button type="submit" class="h-8 text-sm py-1 px-3 rounded-lg font-medium flex-1" style="background: linear-gradient(to right, #1f2937, #000000); color: white; border: none;">Log in</button>
                </div>

                <!-- Footer text -->
                <div class="text-xs font-medium text-gray-500">
                  Don't have an account yet?
                  <button type="button" onclick={toggleSignupModal} class="text-purple-600 hover:text-purple-800 hover:underline">
                    Sign up here
                  </button>
                </div>
              </form>
            </div>
          {/if}

          <!-- Signup dropdown -->
          {#if isSignupModalVisible}
            <div class="auth-dropdown">
              <form class="flex flex-col space-y-2" onsubmit={(e) => { e.preventDefault(); register(); }}>
                <!-- Title -->
                <h3 class="text-base font-medium text-gray-900 leading-tight">Create your CodeFlow account</h3>

                <!-- Username & password textboxes + signup button -->
                <div class="flex items-center space-x-2">
                  <Input type="text" bind:value={username} placeholder="Username" required class="h-8 text-sm flex-1" />
                  <Input type="password" bind:value={password} placeholder="Password" required class="h-8 text-sm flex-1" />
                  <button type="submit" class="h-8 text-sm py-1 px-3 rounded-lg font-medium flex-1" style="background: linear-gradient(to right, #1f2937, #000000); color: white; border: none;">Sign up</button>
                </div>

                <!-- Footer text -->
                <div class="text-xs font-medium text-gray-500">
                  Already have an account?
                  <button type="button" onclick={toggleLoginModal} class="text-purple-600 hover:text-purple-800 hover:underline">
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
<main class="min-h-screen" style="background-color: #1E1E1E; display: flex; align-items: center; justify-content: center;">
  <div class="relative py-20 px-4 sm:px-6 lg:px-8 w-full">
    <div class="max-w-5xl mx-auto text-center">
      <h1 class="text-6xl md:text-7xl font-bold text-white mb-8">
        Welcome to CodeFlow
      </h1>
      <p class="text-2xl md:text-3xl text-white mb-12 max-w-3xl mx-auto leading-relaxed">
        Choose a file and start practicing your programming skills.
      </p>

      <!-- Upload section -->
      <div class="space-y-12 pt-16">
        <!-- File input area -->
        <div class="flex items-center justify-center w-full max-w-2xl mx-auto">
          {#if !uploadedFile}
            <!-- Upload prompt -->
            <label for="dropzone-file" class="flex flex-col items-center justify-center w-full h-32 border-2 border-white/30 border-dashed rounded-[24px] cursor-pointer bg-white/10 hover:bg-white/20 transition-all duration-300">
              <div class="flex flex-col items-center justify-center pt-5 pb-6">
                <svg class="w-8 h-8 mb-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
                </svg>
                <p class="mb-2 text-sm text-white font-semibold">
                  Click to upload / drag and drop your learning materials
                </p>
                <p class="text-xs text-white">PDF, DOC, TXT (MAX. 10MB)</p>
              </div>
              <input id="dropzone-file" type="file" class="hidden" onchange={(e) => uploadedFile = e.target.files[0]} disabled={isLoading} />
            </label>
          {:else}
            <!-- File display inside dotted border -->
            <div class="w-full h-32 border-2 border-white/30 border-dashed rounded-[24px] p-1">
              <div class="file-display w-full rounded-[20px] flex items-center justify-between px-6 text-white">
                <div class="flex items-center space-x-4">
                  <div class="text-3xl">
                    {getFileIcon(uploadedFile.name)}
                  </div>
                  <div class="text-left">
                    <p class="font-semibold text-base">{uploadedFile.name}</p>
                    <p class="text-sm opacity-80">{(uploadedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                  </div>
                </div>
                <button
                  onclick={removeUploadedFile}
                  class="remove-file-btn p-2 rounded-full transition-all duration-200"
                  title="Remove file"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </div>
            </div>
          {/if}
        </div>

        <!-- Code it Button -->
        <div class="flex justify-center pt-8">
          <button
            onclick={handleFileUpload}
            class="custom-purple-hover flex items-center space-x-3 bg-white text-black font-medium rounded-[24px] px-6 py-3 border border-gray-300 transition-all duration-200 shadow-lg"
            disabled={isLoading}
          >
            {#if isLoading}
              <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Processing...</span>
            {:else}
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/>
              </svg>
              <span>Code it</span>
            {/if}
          </button>
        </div>
      </div>
    </div>
  </div>
</main>