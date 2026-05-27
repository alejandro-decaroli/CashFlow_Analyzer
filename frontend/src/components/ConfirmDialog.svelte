<script>
  export let show = false;
  export let title = "Confirmar Acción";
  export let message = "¿Estás seguro de que deseas continuar?";
  export let confirmLabel = "Confirmar";
  export let cancelLabel = "Cancelar";
  export let variant = "danger"; // 'danger' | 'warning' | 'info'
  export let onConfirm = () => {};
  export let onCancel = () => {};

  function handleConfirm() {
    onConfirm();
    show = false;
  }

  function handleCancel() {
    onCancel();
    show = false;
  }
</script>

{#if show}
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div class="confirm-backdrop" on:click={handleCancel}></div>

  <div class="confirm-dialog glass-panel animate-fade-in">
    <div class="confirm-icon-wrap {variant}">
      {#if variant === 'danger'}
        <svg xmlns="http://www.w3.org/2000/svg" class="confirm-icon-svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      {:else if variant === 'warning'}
        <svg xmlns="http://www.w3.org/2000/svg" class="confirm-icon-svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      {:else}
        <svg xmlns="http://www.w3.org/2000/svg" class="confirm-icon-svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      {/if}
    </div>

    <h3 class="confirm-title">{title}</h3>
    <p class="confirm-message">{message}</p>

    <div class="confirm-actions">
      <button class="glass-btn glass-btn-secondary" on:click={handleCancel}>
        {cancelLabel}
      </button>
      <button class="glass-btn confirm-btn-{variant}" on:click={handleConfirm}>
        {confirmLabel}
      </button>
    </div>
  </div>
{/if}

<style>
  .confirm-backdrop {
    position: fixed;
    inset: 0;
    background: radial-gradient(circle at center, rgba(239, 68, 68, 0.08) 0%, rgba(5, 7, 15, 0.92) 100%);
    backdrop-filter: blur(14px);
    z-index: 2000;
  }

  .confirm-dialog {
    position: fixed;
    top: 30%;
    left: 35%;
    transform: translate(-50%, -50%);
    z-index: 2001;
    width: 90%;
    max-width: 440px;
    padding: 32px;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 16px;
    border-color: rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7);
  }

  .confirm-icon-wrap {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 4px;
  }

  .confirm-icon-wrap.danger {
    background: rgba(239, 68, 68, 0.15);
    border: 2px solid rgba(239, 68, 68, 0.3);
    color: #ef4444;
  }

  .confirm-icon-wrap.warning {
    background: rgba(245, 158, 11, 0.15);
    border: 2px solid rgba(245, 158, 11, 0.3);
    color: #f59e0b;
  }

  .confirm-icon-wrap.info {
    background: rgba(59, 130, 246, 0.15);
    border: 2px solid rgba(59, 130, 246, 0.3);
    color: #3b82f6;
  }

  .confirm-icon-svg {
    width: 28px;
    height: 28px;
  }

  .confirm-title {
    font-size: 1.3rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.3px;
  }

  .confirm-message {
    font-size: 0.95rem;
    color: var(--text-secondary);
    line-height: 1.6;
    max-width: 360px;
  }

  .confirm-actions {
    display: flex;
    gap: 14px;
    margin-top: 8px;
    width: 100%;
    justify-content: center;
  }

  .confirm-actions .glass-btn {
    min-width: 120px;
    padding: 12px 24px;
    font-size: 0.95rem;
    font-weight: 600;
  }

  /* Danger confirm button */
  .confirm-btn-danger {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
    color: #ffffff !important;
    border: 1px solid #ef4444 !important;
    box-shadow: 0 4px 16px rgba(239, 68, 68, 0.35) !important;
  }
  .confirm-btn-danger:hover {
    filter: brightness(1.15);
    box-shadow: 0 6px 22px rgba(239, 68, 68, 0.5) !important;
  }

  /* Warning confirm button */
  .confirm-btn-warning {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
    color: #ffffff !important;
    border: 1px solid #f59e0b !important;
    box-shadow: 0 4px 16px rgba(245, 158, 11, 0.35) !important;
  }
  .confirm-btn-warning:hover {
    filter: brightness(1.15);
    box-shadow: 0 6px 22px rgba(245, 158, 11, 0.5) !important;
  }

  /* Info confirm button */
  .confirm-btn-info {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    color: #ffffff !important;
    border: 1px solid #3b82f6 !important;
    box-shadow: 0 4px 16px rgba(59, 130, 246, 0.35) !important;
  }
  .confirm-btn-info:hover {
    filter: brightness(1.15);
    box-shadow: 0 6px 22px rgba(59, 130, 246, 0.5) !important;
  }
</style>
