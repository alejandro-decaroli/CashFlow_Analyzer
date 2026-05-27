<script>
  import { onMount } from 'svelte';
  import { api } from '../api.js';
  import { notify, refreshData, triggerRefresh } from '../store.js';
  import ConfirmDialog from './ConfirmDialog.svelte';

  let transactions = [];
  let filteredTransactions = [];
  let loading = true;

  // Filter States
  let searchQuery = "";
  let selectedType = "ALL"; // ALL, GASTO, INGRESO
  let selectedCaja = "ALL";
  let selectedClass = "ALL"; // categoria o fuente

  let uniqueCajas = [];
  let uniqueClasses = [];

  $: {
    if ($triggerRefresh >= 0) {
      loadFeed();
    }
  }

  // Reactive filtering
  $: {
    filteredTransactions = transactions.filter(t => {
      const matchesSearch = t.descripcion?.toLowerCase().includes(searchQuery.toLowerCase()) || 
                            t.categoria_o_fuente_nombre?.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesType = selectedType === "ALL" || t.tipo === selectedType;
      const matchesCaja = selectedCaja === "ALL" || t.caja_id === selectedCaja;
      const matchesClass = selectedClass === "ALL" || t.categoria_o_fuente_id === selectedClass;

      return matchesSearch && matchesType && matchesCaja && matchesClass;
    });
  }

  async function loadFeed() {
    loading = true;
    try {
      transactions = await api.getTransactionsFeed();
      
      // Extraer valores únicos para los selectores de filtro
      const cajasMap = new Map();
      const classMap = new Map();
      
      transactions.forEach(t => {
        cajasMap.set(t.caja_id, t.caja_nombre);
        classMap.set(t.categoria_o_fuente_id, t.categoria_o_fuente_nombre);
      });

      uniqueCajas = Array.from(cajasMap.entries()).map(([id, nombre]) => ({ id, nombre }));
      uniqueClasses = Array.from(classMap.entries()).map(([id, nombre]) => ({ id, nombre }));
    } catch (e) {
      notify("Error al cargar movimientos: " + e.message, "error");
    } finally {
      loading = false;
    }
  }

  let showConfirmDelete = false;
  let pendingDeleteTransaction = null;

  function handleDelete(t) {
    pendingDeleteTransaction = t;
    showConfirmDelete = true;
  }

  async function executeDelete() {
    if (!pendingDeleteTransaction) return;
    const t = pendingDeleteTransaction;
    try {
      if (t.tipo === 'GASTO') {
        await api.deleteGasto(t.id);
      } else {
        await api.deleteIngreso(t.id);
      }
      notify("Movimiento eliminado y saldo recalculado.");
      refreshData();
    } catch (e) {
      // Si el período está cerrado, el backend lanzará un error 400 impidiendo borrar
      notify(e.message, "error");
    } finally {
      pendingDeleteTransaction = null;
    }
  }

  function formatCurrency(val) {
    return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' })
      .format(val)
      .replace("ARS", "$");
  }
</script>

<div class="feed-wrapper animate-fade-in">
  <div class="feed-header">
    <div class="header-text">
      <h2>Historial de Movimientos</h2>
      <p class="text-secondary">Audita, filtra y busca transacciones en tiempo real sobre todas tus cajas</p>
    </div>
  </div>

  <!-- Barra de Filtros Glassmorphic -->
  <div class="filters-panel glass-panel">
    <div class="filter-group-row">
      <!-- Búsqueda por texto -->
      <div class="filter-field flex-2">
        <label for="search">Buscar Nota o Clasificación</label>
        <input 
          id="search"
          type="text" 
          placeholder="Ej. supermercado, sueldo, servicios..." 
          bind:value={searchQuery}
          class="glass-input search-input"
        />
      </div>

      <!-- Tipo de transacción -->
      <div class="filter-field">
        <label for="filterType">Tipo</label>
        <select id="filterType" bind:value={selectedType} class="glass-input select-dark">
          <option value="ALL">Todos</option>
          <option value="GASTO">Gastos (Egresos)</option>
          <option value="INGRESO">Ingresos (Créditos)</option>
        </select>
      </div>

      <!-- Caja/Cuenta -->
      <div class="filter-field">
        <label for="filterCaja">Caja / Cuenta</label>
        <select id="filterCaja" bind:value={selectedCaja} class="glass-input select-dark">
          <option value="ALL">Todas las Cajas</option>
          {#each uniqueCajas as c}
            <option value={c.id}>{c.nombre}</option>
          {/each}
        </select>
      </div>

      <!-- Categoría/Fuente -->
      <div class="filter-field">
        <label for="filterClass">Clasificación</label>
        <select id="filterClass" bind:value={selectedClass} class="glass-input select-dark">
          <option value="ALL">Todas</option>
          {#each uniqueClasses as cl}
            {#if cl.nombre !== "Ajuste por Conciliación"}
              <option value={cl.id}>{cl.nombre}</option>
            {/if}
          {/each}
        </select>
      </div>
    </div>
  </div>

  {#if loading}
    <div class="loading-state glass-panel">
      <div class="spinner"></div>
      <p>Cargando libro de movimientos...</p>
    </div>
  {:else}
    <!-- Tabla de Movimientos Ledger -->
    <div class="table-container glass-panel">
      {#if filteredTransactions.length === 0}
        <div class="empty-state">No se encontraron movimientos que coincidan con los filtros seleccionados.</div>
      {:else}
        <table class="ledger-table">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Descripción / Nota</th>
              <th>Caja / Cuenta</th>
              <th>Clasificación</th>
              <th class="text-right">Monto</th>
              <th class="text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {#each filteredTransactions as t}
              <tr class="ledger-row glass-panel-hover">
                <td class="date-cell font-sans text-secondary">{t.fecha}</td>
                <td class="desc-cell">
                  <div class="desc-inner">
                    <div class="desc-text">{t.descripcion || 'Sin descripción'}</div>
                    {#if t.categoria_o_fuente_nombre === 'Ajuste por Conciliación'}
                      <span class="auto-badge">Auto-ajuste</span>
                    {/if}
                  </div>
                </td>
                <td class="caja-cell">
                  <div class="caja-inner">
                    <span class="caja-dot {t.tipo}"></span>
                    <span>{t.caja_nombre}</span>
                  </div>
                </td>
                <td class="tag-cell">
                  <span class="category-tag" style="background-color: {t.color}15; border-color: {t.color}; color: {t.color}">
                    {t.categoria_o_fuente_nombre}
                  </span>
                </td>
                <td class="amount-cell text-right financial-num {t.tipo === 'INGRESO' ? 'text-emerald' : 'text-rose'}">
                  {t.tipo === 'INGRESO' ? '+' : '-'}{formatCurrency(t.monto)}
                </td>
                <td class="actions-cell text-center">
                  {#if t.categoria_o_fuente_nombre !== 'Ajuste por Conciliación'}
                    <button class="delete-btn" on:click={() => handleDelete(t)} title="Eliminar Movimiento">
                      <svg xmlns="http://www.w3.org/2000/svg" class="action-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  {:else}
                    <span class="locked-icon" title="Ajuste automático de auditoría. Es de sólo lectura.">
                      <svg xmlns="http://www.w3.org/2000/svg" class="action-icon text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                      </svg>
                    </span>
                  {/if}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      {/if}
    </div>
  {/if}
</div>

<ConfirmDialog
  bind:show={showConfirmDelete}
  title="Eliminar Movimiento"
  message={pendingDeleteTransaction ? `¿Estás seguro de que deseas eliminar este movimiento por ${formatCurrency(pendingDeleteTransaction.monto)} (${pendingDeleteTransaction.descripcion || 'Sin descripción'})?` : ''}
  confirmLabel="Eliminar"
  cancelLabel="Cancelar"
  variant="danger"
  onConfirm={executeDelete}
/>

<style>
  .feed-wrapper {
    max-width: 96%;
    margin: 0 auto;
    padding: 0 40px 40px 40px;
    width: 100%;
  }

  .feed-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    margin-top: 15px;
  }

  .header-text h2 {
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #ffffff;
  }

  /* Filters Panel Centered */
  .filters-panel {
    padding: 20px 24px;
    margin-bottom: 28px;
    border-color: rgba(255, 255, 255, 0.04);
    display: flex;
    justify-content: center;
    width: 100%;
  }

  .filter-group-row {
    display: flex;
    gap: 20px;
    align-items: flex-end;
    justify-content: center;
    width: 100%;
  }

  @media (max-width: 768px) {
    .filter-group-row {
      flex-direction: column;
      align-items: stretch;
      gap: 16px;
    }
  }

  .filter-field {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .flex-2 {
    flex: 2;
  }

  .filter-field label {
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--text-secondary);
  }

  .search-input {
    background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3ccircle cx='11' cy='11' r='8'%3e%3c/circle%3e%3cline x1='21' y1='21' x2='16.65' y2='16.65'%3e%3c/line%3e%3c/svg%3e");
    background-repeat: no-repeat;
    background-position: 14px center;
    background-size: 16px;
    padding-left: 40px !important;
  }

  .select-dark {
    appearance: none;
    background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
    background-repeat: no-repeat;
    background-position: right 14px center;
    background-size: 16px;
    padding-right: 40px;
    cursor: pointer;
  }

  .select-dark option {
    background-color: var(--bg-deep);
    color: var(--text-primary);
  }

  /* Table styles */
  .table-container {
    overflow-x: auto;
    border-color: rgba(255, 255, 255, 0.04);
  }

  .ledger-table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
  }

  .ledger-table th {
    padding: 14px 18px;
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  }

  .ledger-row {
    border-bottom: 1px solid rgba(255, 255, 255, 0.02);
  }

  .ledger-row:last-child {
    border-bottom: none;
  }

  .ledger-table td {
    padding: 14px 18px;
    font-size: 0.95rem;
    vertical-align: middle;
  }

  .date-cell {
    white-space: nowrap;
  }

  .desc-cell {
    /* Safe table cell */
  }

  .desc-inner {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }

  .auto-badge {
    background: rgba(139, 92, 246, 0.1);
    color: var(--accent-purple);
    font-size: 0.7rem;
    font-weight: 700;
    padding: 1px 6px;
    border-radius: 4px;
    border: 1px solid rgba(139, 92, 246, 0.2);
  }

  .caja-cell {
    white-space: nowrap;
  }

  .caja-inner {
    display: inline-flex;
    align-items: center;
    gap: 8px;
  }

  .caja-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
  }
  .caja-dot.INGRESO { background-color: #10b981; }
  .caja-dot.GASTO { background-color: #ef4444; }

  .category-tag {
    font-size: 0.78rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 9999px;
    border: 1px solid transparent;
    white-space: nowrap;
  }

  .text-right { text-align: right; }
  .text-center { text-align: center; }

  .actions-cell {
    width: 80px;
  }

  .delete-btn {
    background: transparent;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    padding: 6px;
    border-radius: 50%;
    transition: var(--transition-smooth);
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .delete-btn:hover {
    color: var(--accent-rose);
    background: rgba(239, 68, 68, 0.08);
  }

  .action-icon {
    width: 16px;
    height: 16px;
  }

  /* Spinner */
  .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px;
    gap: 16px;
    border-color: rgba(255, 255, 255, 0.04);
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(255, 255, 255, 0.05);
    border-top: 3px solid var(--accent-purple);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .empty-state {
    color: var(--text-muted);
    font-size: 0.9rem;
    text-align: center;
    padding: 40px;
    background: rgba(255, 255, 255, 0.005);
  }
</style>
