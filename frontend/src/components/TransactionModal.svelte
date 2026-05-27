<script>
  import { onMount } from 'svelte';
  import { api } from '../api.js';
  import { notify, refreshData } from '../store.js';

  export let show = false;
  export let type = 'GASTO'; // GASTO o INGRESO
  export let onClose = () => {};

  let monto = "";
  let fecha = new Date().toISOString().split('T')[0];
  let descripcion = "";
  let caja_id = "";
  let class_id = ""; // categoria_gasto_id o fuente_ingreso_id

  let cajas = [];
  let opciones = []; // lista de categorias o fuentes
  let loading = false;

  $: if (show) {
    loadFormData();
  }

  async function loadFormData() {
    try {
      cajas = await api.getCajas();
      if (cajas.length > 0) {
        caja_id = cajas[0].id;
      }
      
      if (type === 'GASTO') {
        opciones = await api.getCategorias();
      } else {
        opciones = await api.getFuentes();
      }
      
      if (opciones.length > 0) {
        class_id = opciones[0].id;
      }
    } catch (e) {
      notify("Error al cargar opciones de formulario: " + e.message, "error");
    }
  }

  function formatCurrency(val) {
    return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' })
      .format(val)
      .replace("ARS", "$");
  }

  async function handleSubmit() {
    if (!monto || parseFloat(monto) <= 0) {
      notify("El monto debe ser un valor numérico mayor a cero.", "warning");
      return;
    }
    if (!caja_id) {
      notify("Por favor, selecciona una caja/cuenta.", "warning");
      return;
    }
    if (!class_id) {
      notify("Por favor, selecciona una clasificación.", "warning");
      return;
    }

    if (type === 'GASTO') {
      const selectedCaja = cajas.find(c => c.id === caja_id);
      if (selectedCaja && parseFloat(monto) > parseFloat(selectedCaja.saldo_actual)) {
        notify(`Saldo insuficiente en la caja "${selectedCaja.nombre}". El saldo disponible es ${formatCurrency(selectedCaja.saldo_actual)} y el gasto propuesto es ${formatCurrency(parseFloat(monto))}.`, "error");
        return;
      }
    }

    loading = true;
    try {
      const data = {
        monto: parseFloat(monto),
        fecha,
        descripcion,
        caja_id,
      };

      if (type === 'GASTO') {
        data.categoria_gasto_id = class_id;
        await api.createGasto(data);
        notify("Gasto registrado y debitado con éxito.");
      } else {
        data.fuente_ingreso_id = class_id;
        await api.createIngreso(data);
        notify("Ingreso registrado y acreditado con éxito.");
      }
      
      // Limpiar formulario y cerrar
      monto = "";
      descripcion = "";
      refreshData();
      onClose();
    } catch (e) {
      notify(e.message, "error");
    } finally {
      loading = false;
    }
  }
</script>

{#if show}
  <!-- Backdrop -->
  <div class="modal-backdrop" on:click={onClose}></div>
  
  <!-- Modal Card -->
  <div class="modal-card glass-panel animate-fade-in">
    <div class="modal-header">
      <h3 class="modal-title">
        {#if type === 'GASTO'}
          <span class="icon-circle bg-rose">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 17l-4 4m0 0l-4-4m4 4V3" />
            </svg>
          </span>
          Registrar Nuevo Gasto
        {:else}
          <span class="icon-circle bg-emerald">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7l4-4m0 0l4 4m-4-4v18" />
            </svg>
          </span>
          Registrar Nuevo Ingreso
        {/if}
      </h3>
      <button class="close-btn" on:click={onClose}>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <form on:submit|preventDefault={handleSubmit} class="modal-body">
      <div class="form-group">
        <label for="monto">Monto ($) <span class="required">*</span></label>
        <input 
          id="monto" 
          type="number" 
          step="0.01" 
          placeholder="0.00" 
          bind:value={monto} 
          class="glass-input financial-num font-lg"
          required 
          disabled={loading}
        />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="fecha">Fecha <span class="required">*</span></label>
          <input 
            id="fecha" 
            type="date" 
            bind:value={fecha} 
            class="glass-input" 
            required 
            disabled={loading}
          />
        </div>

        <div class="form-group">
          <label for="caja">Caja / Cuenta <span class="required">*</span></label>
          <select id="caja" bind:value={caja_id} class="glass-input select-dark" required disabled={loading}>
            {#each cajas as c}
              <option value={c.id}>{c.nombre} (Saldo: ${c.saldo_actual})</option>
            {/each}
          </select>
        </div>
      </div>

      <div class="form-group">
        <label for="clasificacion">
          {#if type === 'GASTO'}
            Categoría del Gasto <span class="required">*</span>
          {:else}
            Fuente del Ingreso <span class="required">*</span>
          {/if}
        </label>
        <select id="clasificacion" bind:value={class_id} class="glass-input select-dark" required disabled={loading}>
          {#each opciones as op}
            {#if op.nombre !== "Ajuste por Conciliación"}
              <option value={op.id}>{op.nombre}</option>
            {/if}
          {/each}
        </select>
      </div>

      <div class="form-group">
        <label for="descripcion">Descripción / Nota</label>
        <input 
          id="descripcion" 
          type="text" 
          placeholder="Ej. Compra supermercado mensual, Cobro factura 42..." 
          bind:value={descripcion} 
          class="glass-input"
          disabled={loading}
        />
      </div>

      <div class="modal-footer">
        <button type="button" class="glass-btn glass-btn-secondary" on:click={onClose} disabled={loading}>
          Cancelar
        </button>
        <button type="submit" class="glass-btn glass-btn-primary" disabled={loading}>
          {#if loading}
            Registrando...
          {:else if type === 'GASTO'}
            Debitar Gasto
          {:else}
            Acreditar Ingreso
          {/if}
        </button>
      </div>
    </form>
  </div>
{/if}

<style>
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
    top: 24%;
    left: 36%;
    transform: translate(-50%, -50%);
    width: 90%;
    max-width: 520px;
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
  }

  .icon-circle {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
  }

  .bg-rose {
    background: rgba(239, 68, 68, 0.2);
    border: 1px solid rgba(239, 68, 68, 0.4);
    color: var(--accent-rose);
  }

  .bg-emerald {
    background: rgba(16, 185, 129, 0.2);
    border: 1px solid rgba(16, 185, 129, 0.4);
    color: var(--accent-emerald);
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

  .font-lg {
    font-size: 1.5rem;
    padding: 12px 16px;
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

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 12px;
  }
</style>
