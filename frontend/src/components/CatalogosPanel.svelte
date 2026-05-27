<script>
  import { onMount } from 'svelte';
  import { api } from '../api.js';
  import { notify, refreshData, triggerRefresh } from '../store.js';
  import ConfirmDialog from './ConfirmDialog.svelte';

  let categorias = [];
  let fuentes = [];
  let loadingCat = true;
  let loadingFue = true;

  // Form States
  let showCatModal = false;
  let showFueModal = false;

  // Categoria form
  let catNombre = "";
  let catColor = "#8b5cf6";
  let catDesc = "";
  let submittingCat = false;

  // Fuente form
  let fueNombre = "";
  let fueColor = "#10b981";
  let fueDesc = "";
  let submittingFue = false;

  $: {
    if ($triggerRefresh >= 0) {
      loadCatalogos();
    }
  }

  async function loadCatalogos() {
    loadingCat = true;
    loadingFue = true;
    try {
      [categorias, fuentes] = await Promise.all([
        api.getAllCategorias(),
        api.getAllFuentes()
      ]);
    } catch (e) {
      notify("Error al cargar catálogos: " + e.message, "error");
    } finally {
      loadingCat = false;
      loadingFue = false;
    }
  }

  async function handleCreateCategoria() {
    if (!catNombre.trim()) {
      notify("El nombre de la categoría es obligatorio.", "warning");
      return;
    }
    submittingCat = true;
    try {
      await api.createCategoria({ nombre: catNombre.trim(), color: catColor, descripcion: catDesc || null, activo: true });
      notify("Categoría creada exitosamente.");
      catNombre = ""; catColor = "#8b5cf6"; catDesc = "";
      showCatModal = false;
      refreshData();
    } catch (e) {
      notify(e.message, "error");
    } finally {
      submittingCat = false;
    }
  }

  let showConfirmDeleteCat = false;
  let pendingDeleteCat = null;
  let showConfirmDeleteFue = false;
  let pendingDeleteFue = null;

  function handleDeleteCategoria(cat) {
    pendingDeleteCat = cat;
    showConfirmDeleteCat = true;
  }

  async function executeDeleteCategoria() {
    if (!pendingDeleteCat) return;
    try {
      await api.deleteCategoria(pendingDeleteCat.id);
      notify("Categoría eliminada.");
      refreshData();
    } catch (e) {
      notify(e.message, "info");
      refreshData();
    } finally {
      pendingDeleteCat = null;
    }
  }

  async function handleCreateFuente() {
    if (!fueNombre.trim()) {
      notify("El nombre de la fuente es obligatorio.", "warning");
      return;
    }
    submittingFue = true;
    try {
      await api.createFuente({ nombre: fueNombre.trim(), color: fueColor, descripcion: fueDesc || null, activo: true });
      notify("Fuente de ingreso creada exitosamente.");
      fueNombre = ""; fueColor = "#10b981"; fueDesc = "";
      showFueModal = false;
      refreshData();
    } catch (e) {
      notify(e.message, "error");
    } finally {
      submittingFue = false;
    }
  }

  function handleDeleteFuente(fue) {
    pendingDeleteFue = fue;
    showConfirmDeleteFue = true;
  }

  async function executeDeleteFuente() {
    if (!pendingDeleteFue) return;
    try {
      await api.deleteFuente(pendingDeleteFue.id);
      notify("Fuente de ingresos eliminada.");
      refreshData();
    } catch (e) {
      notify(e.message, "info");
      refreshData();
    } finally {
      pendingDeleteFue = null;
    }
  }
</script>

<div class="catalogos-wrapper animate-fade-in">
  <div class="catalogos-header">
    <div class="header-text">
      <h2>Catálogos del Sistema</h2>
      <p class="text-secondary">Administra las categorías de gasto y las fuentes de ingreso del sistema</p>
    </div>
  </div>

  <div class="dashboard-grid">

    <!-- Panel Categorías de Gastos -->
    <div class="col-6 glass-panel catalog-panel">
      <div class="panel-header">
        <div>
          <h3>Categorías de Gasto</h3>
          <p class="text-secondary">Etiquetas para clasificar tus egresos y auditar por rubro</p>
        </div>
        <button class="glass-btn glass-btn-rose" on:click={() => showCatModal = true}>
          <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Nueva
        </button>
      </div>

      {#if loadingCat}
        <div class="mini-spinner"></div>
      {:else if categorias.length === 0}
        <div class="empty-state">No hay categorías registradas.</div>
      {:else}
        <div class="catalog-list">
          {#each categorias as cat}
            <div class="catalog-item {cat.activo ? '' : 'archived'}">
              <div class="item-left">
                <span class="color-swatch" style="background-color: {cat.color}"></span>
                <div>
                  <div class="item-name">{cat.nombre}</div>
                  {#if cat.descripcion}
                    <div class="item-desc text-muted">{cat.descripcion}</div>
                  {/if}
                </div>
              </div>
              <div class="item-right">
                {#if !cat.activo}
                  <span class="archived-badge">Archivada</span>
                {/if}
                {#if cat.nombre !== 'Ajuste por Conciliación'}
                  <button class="icon-btn delete-icon" on:click={() => handleDeleteCategoria(cat)} title="Eliminar categoría">
                    <svg xmlns="http://www.w3.org/2000/svg" class="icon-sm" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                {:else}
                  <span class="system-badge">Sistema</span>
                {/if}
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Panel Fuentes de Ingreso -->
    <div class="col-6 glass-panel catalog-panel">
      <div class="panel-header">
        <div>
          <h3>Fuentes de Ingreso</h3>
          <p class="text-secondary">Etiquetas para identificar el origen de tus créditos mensuales</p>
        </div>
        <button class="glass-btn glass-btn-emerald" on:click={() => showFueModal = true}>
          <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Nueva
        </button>
      </div>

      {#if loadingFue}
        <div class="mini-spinner"></div>
      {:else if fuentes.length === 0}
        <div class="empty-state">No hay fuentes de ingreso registradas.</div>
      {:else}
        <div class="catalog-list">
          {#each fuentes as fue}
            <div class="catalog-item {fue.activo ? '' : 'archived'}">
              <div class="item-left">
                <span class="color-swatch" style="background-color: {fue.color}"></span>
                <div>
                  <div class="item-name">{fue.nombre}</div>
                  {#if fue.descripcion}
                    <div class="item-desc text-muted">{fue.descripcion}</div>
                  {/if}
                </div>
              </div>
              <div class="item-right">
                {#if !fue.activo}
                  <span class="archived-badge">Archivada</span>
                {/if}
                {#if fue.nombre !== 'Ajuste por Conciliación'}
                  <button class="icon-btn delete-icon" on:click={() => handleDeleteFuente(fue)} title="Eliminar fuente">
                    <svg xmlns="http://www.w3.org/2000/svg" class="icon-sm" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                {:else}
                  <span class="system-badge">Sistema</span>
                {/if}
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>
</div>

<!-- Modal Nueva Categoría -->
{#if showCatModal}
  <div class="modal-backdrop" on:click={() => showCatModal = false}></div>
  <div class="modal-card glass-panel animate-fade-in">
    <div class="modal-header">
      <h3 class="modal-title">
        <span class="icon-circle bg-rose-circle text-rose">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
          </svg>
        </span>
        Nueva Categoría de Gasto
      </h3>
      <button class="close-btn" on:click={() => showCatModal = false}>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
    <form on:submit|preventDefault={handleCreateCategoria} class="modal-body">
      <div class="form-group">
        <label for="catNombre">Nombre <span class="required">*</span></label>
        <input id="catNombre" type="text" placeholder="Ej. Alimentación, Transporte, Salud..." bind:value={catNombre} class="glass-input" required disabled={submittingCat} />
      </div>
      <div class="form-row">
        <div class="form-group">
          <label for="catDesc">Descripción (Opcional)</label>
          <input id="catDesc" type="text" placeholder="Ej. Gastos de supermercado y almacén" bind:value={catDesc} class="glass-input" disabled={submittingCat} />
        </div>
        <div class="form-group color-group">
          <label for="catColor">Color de Etiqueta</label>
          <div class="color-row">
            <input id="catColor" type="color" bind:value={catColor} class="color-picker" disabled={submittingCat} />
            <span class="color-preview financial-num" style="color: {catColor}">{catColor}</span>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="glass-btn glass-btn-secondary" on:click={() => showCatModal = false} disabled={submittingCat}>Cancelar</button>
        <button type="submit" class="glass-btn glass-btn-primary" disabled={submittingCat}>{submittingCat ? 'Creando...' : 'Crear Categoría'}</button>
      </div>
    </form>
  </div>
{/if}

<!-- Modal Nueva Fuente -->
{#if showFueModal}
  <div class="modal-backdrop" on:click={() => showFueModal = false}></div>
  <div class="modal-card glass-panel animate-fade-in">
    <div class="modal-header">
      <h3 class="modal-title">
        <span class="icon-circle bg-emerald-circle text-emerald">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
          </svg>
        </span>
        Nueva Fuente de Ingreso
      </h3>
      <button class="close-btn" on:click={() => showFueModal = false}>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
    <form on:submit|preventDefault={handleCreateFuente} class="modal-body">
      <div class="form-group">
        <label for="fueNombre">Nombre <span class="required">*</span></label>
        <input id="fueNombre" type="text" placeholder="Ej. Sueldo Principal, Freelance, Alquiler..." bind:value={fueNombre} class="glass-input" required disabled={submittingFue} />
      </div>
      <div class="form-row">
        <div class="form-group">
          <label for="fueDesc">Descripción (Opcional)</label>
          <input id="fueDesc" type="text" placeholder="Ej. Cobro mensual primer trabajo" bind:value={fueDesc} class="glass-input" disabled={submittingFue} />
        </div>
        <div class="form-group color-group">
          <label for="fueColor">Color de Etiqueta</label>
          <div class="color-row">
            <input id="fueColor" type="color" bind:value={fueColor} class="color-picker" disabled={submittingFue} />
            <span class="color-preview financial-num" style="color: {fueColor}">{fueColor}</span>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="glass-btn glass-btn-secondary" on:click={() => showFueModal = false} disabled={submittingFue}>Cancelar</button>
        <button type="submit" class="glass-btn glass-btn-primary" disabled={submittingFue}>{submittingFue ? 'Creando...' : 'Crear Fuente'}</button>
      </div>
    </form>
  </div>
{/if}

<ConfirmDialog
  bind:show={showConfirmDeleteCat}
  title="Eliminar Categoría"
  message={pendingDeleteCat ? `¿Estás seguro de que deseas eliminar la categoría "${pendingDeleteCat.nombre}"? Si tiene gastos históricos, será archivada.` : ''}
  confirmLabel="Eliminar"
  cancelLabel="Cancelar"
  variant="danger"
  onConfirm={executeDeleteCategoria}
/>

<ConfirmDialog
  bind:show={showConfirmDeleteFue}
  title="Eliminar Fuente de Ingreso"
  message={pendingDeleteFue ? `¿Estás seguro de que deseas eliminar la fuente "${pendingDeleteFue.nombre}"? Si tiene ingresos históricos, será archivada.` : ''}
  confirmLabel="Eliminar"
  cancelLabel="Cancelar"
  variant="danger"
  onConfirm={executeDeleteFuente}
/>

<style>
  .catalogos-wrapper {
    max-width: 96%;
    margin: 0 auto;
    padding: 0 40px 40px 40px;
    width: 100%;
  }

  .catalogos-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 28px;
    margin-top: 15px;
    width: 100%;
    text-align: left;
  }

  .header-text h2 {
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #ffffff;
    text-align: left;
  }

  .col-6 { grid-column: span 6; }

  @media (max-width: 768px) {
    .col-6 { grid-column: span 12; }
  }

  .catalog-panel {
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 18px;
    border-color: rgba(255,255,255,0.04);
    background: var(--bg-card);
    border-radius: 16px;
    border: 1px solid var(--border-glass);
  }

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center; /* Center the buttons vertically */
    gap: 16px;
    width: 100%;
    text-align: left; /* Justify text to left */
  }

  .panel-header h3 {
    font-size: 1.2rem;
    font-weight: 700;
    color: #ffffff;
    text-align: left; /* Justify h3 to left */
  }

  .panel-header p {
    text-align: left; /* Justify secondary text to left */
  }

  .btn-icon {
    width: 16px;
    height: 16px;
    margin-right: 6px;
  }

  /* Catalog List */
  .catalog-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-height: 480px;
    overflow-y: auto;
    padding-right: 4px;
  }

  .catalog-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 16px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.015);
    border: 1px solid rgba(255, 255, 255, 0.03);
    transition: var(--transition-smooth);
  }

  .catalog-item:hover {
    background: rgba(255, 255, 255, 0.03);
    border-color: rgba(255, 255, 255, 0.07);
    transform: translateX(4px);
  }

  .catalog-item.archived {
    opacity: 0.55;
  }

  .item-left {
    display: flex;
    align-items: center;
    gap: 12px;
    text-align: left; /* Justify item contents to left */
  }

  .color-swatch {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
    box-shadow: 0 0 6px currentColor;
  }

  .item-name {
    font-size: 0.95rem;
    font-weight: 600;
    color: #ffffff;
    text-align: left;
  }

  .item-desc {
    font-size: 0.78rem;
    margin-top: 2px;
    text-align: left;
  }

  .item-right {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .icon-btn {
    background: transparent;
    border: none;
    cursor: pointer;
    padding: 6px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition: var(--transition-smooth);
  }

  .delete-icon {
    color: var(--text-muted);
  }

  .delete-icon:hover {
    color: var(--accent-rose);
    background: rgba(239, 68, 68, 0.08);
  }

  .icon-sm {
    width: 15px;
    height: 15px;
  }

  .archived-badge {
    font-size: 0.7rem;
    font-weight: 700;
    background: rgba(100, 116, 139, 0.12);
    color: var(--text-muted);
    padding: 2px 6px;
    border-radius: 4px;
    border: 1px solid rgba(100, 116, 139, 0.2);
  }

  .system-badge {
    font-size: 0.7rem;
    font-weight: 700;
    background: rgba(139, 92, 246, 0.1);
    color: var(--accent-purple);
    padding: 2px 6px;
    border-radius: 4px;
    border: 1px solid rgba(139, 92, 246, 0.2);
  }

  /* Spinner mini */
  .mini-spinner {
    width: 24px;
    height: 24px;
    border: 2px solid rgba(255, 255, 255, 0.05);
    border-top: 2px solid var(--accent-purple);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 30px auto;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .empty-state {
    color: var(--text-muted);
    font-size: 0.85rem;
    text-align: center;
    padding: 24px;
    background: rgba(255, 255, 255, 0.01);
    border: 1px dashed rgba(255,255,255,0.05);
    border-radius: 8px;
  }

  /* Modals */
  .modal-backdrop {
    position: fixed;
    inset: 0;
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
    max-width: 480px;
    z-index: 1001;
    padding: 24px;
    border-color: rgba(255, 255, 255, 0.08);
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }

  .modal-title {
    font-size: 1.15rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 12px;
    color: #ffffff;
  }

  .icon-circle {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .text-rose { color: var(--accent-rose); }
  .text-emerald { color: var(--accent-emerald); }
  .bg-rose-circle { background: rgba(239,68,68,0.12); border: 1px solid rgba(239,68,68,0.2); }
  .bg-emerald-circle { background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.2); }

  .close-btn {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    padding: 4px;
    border-radius: 50%;
    transition: var(--transition-smooth);
  }

  .close-btn:hover {
    color: #fff;
    background: rgba(255,255,255,0.05);
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

  .form-group label {
    font-size: 0.83rem;
    font-weight: 500;
    color: var(--text-secondary);
  }

  .required { color: var(--accent-rose); }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }

  @media (max-width: 480px) {
    .form-row { display: flex; flex-direction: column; }
  }

  .color-group .color-row {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .color-picker {
    width: 38px;
    height: 38px;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    background: none;
    cursor: pointer;
    padding: 2px;
  }

  .color-preview {
    font-size: 0.85rem;
    font-weight: 600;
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 8px;
  }
</style>
