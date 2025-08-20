<script lang="ts">
    import '../global.css';
    import { afterNavigate } from '$app/navigation';
    import { toast } from '$lib/stores/toast.js';
    import ToastNotification from '$lib/components/ToastNotification.svelte';

    afterNavigate(() => toast.hide());
</script>

<svelte:head>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/flowbite/2.2.1/flowbite.min.css" rel="stylesheet" />
</svelte:head>

<!-- Page content -->
<slot />

<!-- Global toast -->
<ToastNotification />