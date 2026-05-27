<script>
  import { onMount } from 'svelte';
  import { api } from '../api.js';
  import { notify, refreshData, triggerRefresh } from '../store.js';
  import ConfirmDialog from './ConfirmDialog.svelte';

  let cajas = [];
  let loading = true;

  // Add/Edit Modal state
  let showModal = false;
  let isEditing = false;
  let currentId = null;

  let nombre = "";
  let tipo = "BANCO"; // BANCO, EFECTIVO, TARJETA_DEBITO, OTRO
  let saldo_inicial = "";
  let activo = true;

  let submitting = false;

  $: {
    if ($triggerRefresh >= 0) {
      loadCajas();
    }
  }

  async function loadCajas() {
    loading = true;
    try {
      cajas = await api.getAllCajas();
    } catch (e) {
      notify("Error al cargar cajas: " + e.message, "error");
    } finally {
      loading = false;
    }
  }

  function openCreateModal() {
    isEditing = false;
    currentId = null;
    nombre = "";
    tipo = "BANCO";
    saldo_inicial = "";
    activo = true;
    showModal = true;
  }

  function openEditModal(caja) {
    isEditing = true;
    currentId = caja.id;
    nombre = caja.nombre;
    tipo = caja.tipo;
    saldo_inicial = caja.saldo_inicial;
    activo = caja.activo;
    showModal = true;
  }

  async function handleSubmit() {
    if (!nombre) {
      notify("El nombre de la caja es obligatorio.", "warning");
      return;
    }

    if (!isEditing) {
      const val = parseFloat(saldo_inicial) || 0.00;
      if (val < 0) {
        notify("El saldo inicial de una caja no puede ser un número negativo.", "error");
        return;
      }
    }

    submitting = true;
    try {
      if (isEditing) {
        await api.updateCaja(currentId, { nombre, tipo, activo });
        notify("Caja actualizada exitosamente.");
      } else {
        const val = parseFloat(saldo_inicial) || 0.00;
        await api.createCaja({ nombre, tipo, saldo_inicial: val, activo });
        notify("Caja creada exitosamente.");
      }
      refreshData();
      showModal = false;
    } catch (e) {
      notify(e.message, "error");
    } finally {
      submitting = false;
    }
  }

  let showConfirmDelete = false;
  let pendingDeleteCaja = null;

  function handleDelete(caja) {
    pendingDeleteCaja = caja;
    showConfirmDelete = true;
  }

  async function executeDelete() {
    if (!pendingDeleteCaja) return;
    const caja = pendingDeleteCaja;
    try {
      await api.deleteCaja(caja.id);
      notify("Caja eliminada físicamente.");
      refreshData();
    } catch (e) {
      // Si la caja tiene transacciones vinculadas, el backend responderá con error y se desactivará lógicamente.
      notify(e.message, "info");
      refreshData();
    } finally {
      pendingDeleteCaja = null;
    }
  }

  function formatCurrency(val) {
    return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' })
      .format(val)
      .replace("ARS", "$");
  }

  function getCajaTypeLabel(t) {
    switch (t) {
      case 'BANCO': return 'Cuenta Bancaria';
      case 'EFECTIVO': return 'Efectivo';
      case 'TARJETA_DEBITO': return 'Tarjeta de Débito';
      default: return 'Otro Método';
    }
  }

  function getCajaColorClass(t) {
    switch (t) {
      case 'BANCO': return 'text-blue bg-blue-caja';
      case 'EFECTIVO': return 'text-emerald bg-emerald-caja';
      case 'TARJETA_DEBITO': return 'text-purple bg-purple-caja';
      default: return 'text-amber bg-amber-caja';
    }
  }
</script>

<div class="cajas-wrapper animate-fade-in">
  <div class="cajas-header">
    <div class="header-text">
      <h2>Cajas y Cuentas</h2>
      <p class="text-secondary">Visualiza tus saldos activos e iniciales configurados en el sistema</p>
    </div>
    
    <button class="glass-btn glass-btn-primary" on:click={openCreateModal}>
      <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
      </svg>
      Nueva Caja
    </button>
  </div>

  {#if loading}
    <div class="loading-state glass-panel">
      <div class="spinner"></div>
      <p>Cargando información de cuentas...</p>
    </div>
  {:else}
    <div class="cajas-grid">
      {#each cajas as c}
        <div class="caja-card glass-panel {c.activo ? '' : 'inactive-card'}">
          <div class="caja-card-header">
            <!-- Icono y Tipo -->
            <div class="type-badge {getCajaColorClass(c.tipo)}">
              {#if c.tipo === 'BANCO'}
                <svg xmlns="http://www.w3.org/2000/svg" class="caja-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              {:else if c.tipo === 'EFECTIVO'}
                <svg xmlns="http://www.w3.org/2000/svg" class="caja-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              {:else if c.tipo === 'TARJETA_DEBITO'}
                <svg xmlns="http://www.w3.org/2000/svg" class="caja-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                </svg>
              {:else}
                <svg xmlns="http://www.w3.org/2000/svg" class="caja-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              {/if}
              <span class="type-label">{getCajaTypeLabel(c.tipo)}</span>
            </div>

            <!-- Status Badge -->
            {#if c.activo}
              <span class="status-badge active-status">Activa</span>
            {:else}
              <span class="status-badge inactive-status">Inactiva</span>
            {/if}
          </div>

          <div class="caja-info">
            <h3 class="caja-name">{c.nombre}</h3>
            
            <div class="caja-balances">
              <div class="balance-item">
                <span class="balance-title">Saldo Actual</span>
                <span class="balance-val actual-val financial-num">{formatCurrency(c.saldo_actual)}</span>
              </div>
              <div class="balance-item line-divider"></div>
              <div class="balance-item">
                <span class="balance-title">Saldo Inicial</span>
                <span class="balance-val initial-val financial-num">{formatCurrency(c.saldo_inicial)}</span>
              </div>
            </div>
          </div>

          <!-- Card Actions -->
          <div class="caja-actions">
            <button class="caja-btn edit-btn" on:click={() => openEditModal(c)}>
              <svg xmlns="http://www.w3.org/2000/svg" class="action-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
              Editar
            </button>
            <button class="caja-btn delete-btn" on:click={() => handleDelete(c)}>
              <svg xmlns="http://www.w3.org/2000/svg" class="action-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Eliminar
            </button>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<!-- Modal para Crear/Editar Caja -->
{#if showModal}
  <div class="modal-backdrop" on:click={() => showModal = false}></div>
  <div class="modal-card glass-panel animate-fade-in">
    <div class="modal-header">
      <h3 class="modal-title">
        {#if isEditing}
          <span class="icon-circle bg-blue-caja text-blue">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
            </svg>
          </span>
          Editar Caja / Cuenta
        {:else}
          <span class="icon-circle bg-purple-caja text-purple">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
          </span>
          Agregar Nueva Caja
        {/if}
      </h3>
      <button class="close-btn" on:click={() => showModal = false}>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <form on:submit|preventDefault={handleSubmit} class="modal-body">
      <div class="form-group">
        <label for="nombre">Nombre de la Cuenta <span class="required">*</span></label>
        <input 
          id="nombre" 
          type="text" 
          placeholder="Ej. Efectivo Billetera, Banco Galicia, Débito Santander..." 
          bind:value={nombre} 
          class="glass-input" 
          required 
          disabled={submitting}
        />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="tipo">Tipo de Caja</label>
          <select id="tipo" bind:value={tipo} class="glass-input select-dark" required disabled={submitting}>
            <option value="BANCO">Cuenta Bancaria</option>
            <option value="EFECTIVO">Efectivo</option>
            <option value="TARJETA_DEBITO">Tarjeta de Débito</option>
            <option value="OTRO">Otro Método</option>
          </select>
        </div>

        <div class="form-group">
          <label for="saldo_inicial">Saldo Inicial ($)</label>
          <input 
            id="saldo_inicial" 
            type="number" 
            step="0.01" 
            min="0"
            placeholder="0.00" 
            bind:value={saldo_inicial} 
            class="glass-input financial-num" 
            disabled={isEditing || submitting}
            required={!isEditing}
          />
          {#if isEditing}
            <span class="hint text-muted">No editable tras creación</span>
          {/if}
        </div>
      </div>

      {#if isEditing}
        <div class="form-group-row">
          <input 
            id="activo" 
            type="checkbox" 
            bind:checked={activo} 
            disabled={submitting}
          />
          <label for="activo">Cuenta Activa (Habilitar para transacciones)</label>
        </div>
      {/if}

      <div class="modal-footer">
        <button type="button" class="glass-btn glass-btn-secondary" on:click={() => showModal = false} disabled={submitting}>
          Cancelar
        </button>
        <button type="submit" class="glass-btn glass-btn-primary" disabled={submitting}>
          {#if submitting}
            Guardando...
          {:else if isEditing}
            Guardar Cambios
          {:else}
            Crear Caja
          {/if}
        </button>
      </div>
    </form>
  </div>
{/if}

<ConfirmDialog
  bind:show={showConfirmDelete}
  title="Eliminar Caja"
  message={pendingDeleteCaja ? `¿Estás seguro de que deseas eliminar la caja "${pendingDeleteCaja.nombre}"? Si ya tiene transacciones, se desactivará en lugar de borrarse.` : ''}
  confirmLabel="Eliminar"
  cancelLabel="Cancelar"
  variant="danger"
  onConfirm={executeDelete}
/>

<style>
  .cajas-wrapper {
    max-width: 96%;
    margin: 0 auto;
    padding: 0 40px 40px 40px;
    width: 100%;
  }

  .cajas-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 28px;
    margin-top: 15px;
    width: 100%;
  }

  @media (max-width: 580px) {
    .cajas-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 16px;
    }
    
    .cajas-header button {
      width: 100%;
    }
  }

  .header-text h2 {
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #ffffff;
  }

  .btn-icon {
    width: 18px;
    height: 18px;
    margin-right: 8px;
  }

  /* Spinner */
  .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px;
    gap: 20px;
    border-color: rgba(255, 255, 255, 0.04);
  }

  .spinner {
    width: 44px;
    height: 44px;
    border: 3px solid rgba(255, 255, 255, 0.05);
    border-top: 3px solid var(--accent-purple);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  /* Grid de Cajas */
  .cajas-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
    width: 100%;
  }

  @media (max-width: 960px) {
    .cajas-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  @media (max-width: 640px) {
    .cajas-grid {
      grid-template-columns: 1fr;
    }
  }

  .caja-card {
    padding: 24px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 20px;
    border-color: rgba(255, 255, 255, 0.04);
    min-height: 240px;
    border-radius: 16px;
    background: var(--bg-card);
    transition: var(--transition-smooth);
    border: 1px solid var(--border-glass);
  }
  .caja-card:hover {
    border-color: var(--border-glass-hover);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
    transform: translateY(-3px);
  }

  .inactive-card {
    opacity: 0.65;
    background: rgba(255, 255, 255, 0.01) !important;
  }

  .caja-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .type-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    border-radius: 8px;
  }

  .caja-icon {
    width: 16px;
    height: 16px;
  }

  .type-label {
    font-size: 0.8rem;
    font-weight: 700;
  }

  /* Paleta especifica de las badges de Cajas */
  .text-blue { color: var(--accent-blue); }
  .bg-blue-caja { background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(59, 130, 246, 0.2); }

  .text-emerald { color: var(--accent-emerald); }
  .bg-emerald-caja { background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.2); }

  .text-purple { color: var(--accent-purple); }
  .bg-purple-caja { background: rgba(139, 92, 246, 0.12); border: 1px solid rgba(139, 92, 246, 0.2); }

  .text-amber { color: var(--accent-amber); }
  .bg-amber-caja { background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.2); }

  .status-badge {
    font-size: 0.75rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 9999px;
  }

  .active-status {
    background: rgba(16, 185, 129, 0.1);
    color: var(--accent-emerald);
    border: 1px solid rgba(16, 185, 129, 0.2);
  }

  .inactive-status {
    background: rgba(255, 255, 255, 0.05);
    color: var(--text-muted);
    border: 1px solid rgba(255, 255, 255, 0.1);
  }

  .caja-info {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .caja-name {
    font-size: 1.25rem;
    font-weight: 700;
    letter-spacing: -0.3px;
    color: #ffffff;
  }

  .caja-balances {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(255, 255, 255, 0.015);
    border: 1px solid rgba(255, 255, 255, 0.03);
    border-radius: 12px;
    padding: 10px 16px;
  }

  .balance-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
    flex: 1;
  }

  .line-divider {
    max-width: 1px;
    height: 35px;
    background: rgba(255, 255, 255, 0.05);
    margin: 0 16px;
  }

  .balance-title {
    font-size: 0.72rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .balance-val {
    font-size: 1.15rem;
  }

  .actual-val {
    color: var(--text-primary);
  }

  .initial-val {
    color: var(--text-secondary);
    font-size: 0.95rem;
  }

  /* Actions */
  .caja-actions {
    display: flex;
    gap: 8px;
    border-top: 1px solid rgba(255, 255, 255, 0.04);
    padding-top: 14px;
  }

  .caja-btn {
    flex: 1;
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 8px;
    color: var(--text-secondary);
    font-size: 0.85rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 8px 12px;
    cursor: pointer;
    transition: var(--transition-smooth);
  }

  .action-icon {
    width: 14px;
    height: 14px;
  }

  .caja-btn:hover {
    color: #fff;
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.15);
  }

  .delete-btn:hover {
    border-color: rgba(239, 68, 68, 0.3) !important;
    background: rgba(239, 68, 68, 0.12) !important;
    color: #ef4444 !important;
  }

  /* Modals elements styling mapping */
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at center, rgba(139, 92, 246, 0.15) 0%, rgba(5, 7, 15, 0.9) 100%);
    backdrop-filter: blur(12px);
    z-index: 1000;
  }

  .modal-card {
    position: fixed;
    top: 30%;
    left: 35%;
    transform: translate(-50%, -50%);
    width: 90%;
    max-width: 500px;
    z-index: 1001;
    padding: 24px;
    display: flex;
    flex-direction: column;
    border-color: rgba(255, 255, 255, 0.08);
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }

  .modal-title {
    font-size: 1.25rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 12px;
    color: #ffffff;
  }

  .icon-circle {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .close-btn {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    transition: var(--transition-smooth);
    padding: 4px;
    border-radius: 50%;
  }

  .close-btn:hover {
    color: #fff;
    background: rgba(255, 255, 255, 0.05);
  }

  .modal-body {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .form-group-row {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .form-group-row label {
    font-size: 0.88rem;
    color: var(--text-secondary);
    cursor: pointer;
  }

  .form-group-row input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
    accent-color: var(--accent-purple);
  }

  .form-group label {
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--text-secondary);
  }

  .required {
    color: var(--accent-rose);
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }

  @media (max-width: 480px) {
    .form-row {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
  }

  .hint {
    font-size: 0.72rem;
    margin-top: 2px;
  }

  .select-dark {
    appearance: none;
    background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
    background-repeat: no-repeat;
    background-position: right 14px center;
    background-size: 16px;
    padding-right: 40px;
    cursor: pointer;
    background-color: rgba(20, 25, 45, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
  }

  .select-dark option {
    background-color: #0d1222;
    color: #ffffff;
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 12px;
  }
</style>
