<script>
  import { onMount } from 'svelte';
  import Navbar from './components/Navbar.svelte';
  import Dashboard from './components/Dashboard.svelte';
  import TransactionsFeed from './components/TransactionsFeed.svelte';
  import CajasGrid from './components/CajasGrid.svelte';
  import ReconciliationWizard from './components/ReconciliationWizard.svelte';
  import CatalogosPanel from './components/CatalogosPanel.svelte';

  import { activeTab, selectedMonth, selectedYear, notification } from './store.js';

  const MESES = [
    "Enero","Febrero","Marzo","Abril","Mayo","Junio",
    "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
  ];

  const YEARS = [2025, 2026, 2027];

  // Toast auto-dismiss handled in store.js
</script>

<svelte:head>
  <title>CashFlow Analyzer — Finanzas Personales</title>
  <meta name="description" content="CashFlow Personal Analyzer: auditá tus ingresos, egresos, cajas y conciliaciones mensuales en un solo lugar." />
</svelte:head>

<!-- Barra de Navegación Principal -->
<Navbar />

<!-- Selector de Período Global (solo visible en Dashboard, oculto en otros contextos por diseño) -->
{#if $activeTab === 'dashboard' || $activeTab === 'conciliacion'}
  <div class="period-bar">
    <div class="period-inner">
      <span class="period-label">Período:</span>
      <div class="period-selects">
        <select bind:value={$selectedMonth} class="period-select">
          {#each MESES as m, i}
            <option value={i + 1}>{m}</option>
          {/each}
        </select>
        <select bind:value={$selectedYear} class="period-select">
          {#each YEARS as y}
            <option value={y}>{y}</option>
          {/each}
        </select>
      </div>
    </div>
  </div>
{/if}

<!-- Contenido Principal: vista reactiva según tab activo -->
<main class="main-content">
  {#if $activeTab === 'dashboard'}
    <Dashboard />
  {:else if $activeTab === 'transacciones'}
    <TransactionsFeed />
  {:else if $activeTab === 'cajas'}
    <CajasGrid />
  {:else if $activeTab === 'conciliacion'}
    <ReconciliationWizard />
  {:else if $activeTab === 'catalogos'}
    <CatalogosPanel />
  {/if}
</main>

<!-- Toast de Notificaciones Flotante -->
{#if $notification}
  <div class="toast-container">
    <div class="toast glass-panel toast-{$notification.type} animate-fade-in">
      <span class="toast-icon">
        {#if $notification.type === 'success'}
          <svg xmlns="http://www.w3.org/2000/svg" class="t-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        {:else if $notification.type === 'error'}
          <svg xmlns="http://www.w3.org/2000/svg" class="t-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        {:else if $notification.type === 'warning'}
          <svg xmlns="http://www.w3.org/2000/svg" class="t-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        {:else}
          <svg xmlns="http://www.w3.org/2000/svg" class="t-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        {/if}
      </span>
      <span class="toast-msg">{$notification.message}</span>
    </div>
  </div>
{/if}

<style>
  /* Selector de Período */
  .period-bar {
    max-width: 100%;
    margin: 15px auto 5px auto;
    padding: 0 40px;
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .period-inner {
    display: flex;
    align-items: center;
    gap: 12px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 8px 16px;
  }

  .period-label {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
  }

  .period-selects {
    display: flex;
    gap: 8px;
  }

  .period-select {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 6px;
    color: var(--text-primary);
    font-family: var(--font-sans);
    font-size: 0.88rem;
    font-weight: 500;
    padding: 4px 28px 4px 10px;
    cursor: pointer;
    outline: none;
    appearance: none;
    background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
    background-repeat: no-repeat;
    background-position: right 8px center;
    background-size: 14px;
    transition: var(--transition-smooth);
  }

  .period-select:hover,
  .period-select:focus {
    border-color: var(--accent-purple);
    background-color: rgba(139, 92, 246, 0.06);
  }

  .period-select option {
    background: var(--bg-deep);
    color: var(--text-primary);
  }

  /* Área de contenido */
  .main-content {
    padding-top: 12px;
    /* Espacio en móvil para la bottom navbar fija */
    padding-bottom: 80px;
  }

  @media (min-width: 769px) {
    .main-content {
      padding-bottom: 40px;
    }
  }

  /* ─── Toast de notificaciones ─── */
  .toast-container {
    position: fixed;
    bottom: 90px;
    right: 20px;
    z-index: 2000;
    pointer-events: none;
  }

  @media (min-width: 769px) {
    .toast-container {
      bottom: 28px;
    }
  }

  .toast {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 18px;
    border-radius: 12px;
    max-width: 380px;
    font-size: 0.9rem;
    font-weight: 500;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    pointer-events: all;
  }

  .t-icon {
    width: 20px;
    height: 20px;
    flex-shrink: 0;
  }

  .toast-success {
    background: rgba(16, 185, 129, 0.12);
    border-color: rgba(16, 185, 129, 0.3);
    color: #ecfdf5;
  }
  .toast-success .t-icon { color: var(--accent-emerald); }

  .toast-error {
    background: rgba(239, 68, 68, 0.12);
    border-color: rgba(239, 68, 68, 0.3);
    color: #fff1f2;
  }
  .toast-error .t-icon { color: var(--accent-rose); }

  .toast-warning {
    background: rgba(245, 158, 11, 0.12);
    border-color: rgba(245, 158, 11, 0.3);
    color: #fffbeb;
  }
  .toast-warning .t-icon { color: var(--accent-amber); }

  .toast-info {
    background: rgba(59, 130, 246, 0.12);
    border-color: rgba(59, 130, 246, 0.3);
    color: #eff6ff;
  }
  .toast-info .t-icon { color: var(--accent-blue); }
</style>
