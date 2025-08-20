<script lang="ts">
  import { derived } from 'svelte/store';
  import { toast, type ToastType } from '$lib/stores/toast';
  import { TOAST } from '$lib/utils/constants';
  import { CircleCheck, CircleAlert, CircleX } from 'lucide-svelte';

  type IconComponent = typeof CircleX;

  type ToastStyle = {
    icon: IconComponent;
    bgColor: string;
    textColor: string;
  };

  const TOAST_STYLES: Record<ToastType, ToastStyle> = {
    [TOAST.TYPE.ERROR]: { icon: CircleX, bgColor: '#D0342C', textColor: 'white' },
    [TOAST.TYPE.WARNING]: { icon: CircleAlert, bgColor: '#EED202', textColor: '#333' },
    [TOAST.TYPE.SUCCESS]: { icon: CircleCheck, bgColor: '#28a745', textColor: 'white' }
  };

  const config = derived(toast, (toastState) =>
          TOAST_STYLES[(toastState.type || TOAST.TYPE.ERROR) as ToastType]
  );

  const aria = derived(toast, (toastState) => {
    const isError = toastState.type === TOAST.TYPE.ERROR;
    return {
      role: isError ? 'alert' : 'status',
      live: isError ? undefined : ('polite' as const)
    };
  });
</script>

{#if $toast.visible}
  <div class="toast"
       class:fade-out={$toast.fadeOut}
       style:background={$config.bgColor}
       style:color={$config.textColor}
       role={$aria.role}
       aria-live={$aria.live}
       aria-atomic="true">
    <svelte:component this={$config.icon}
                      size={20}
                      aria-hidden="true" />
    <span>{$toast.message}</span>
  </div>
{/if}

<style>
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
    max-width: min(90vw, 560px);
    overflow-wrap: anywhere;
    word-break: break-word;
    white-space: pre-wrap;
  }

  .fade-out {
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

  @media (prefers-reduced-motion: reduce) {
    .toast {
      animation: none !important;
      transition: none !important;
    }
  }
</style>