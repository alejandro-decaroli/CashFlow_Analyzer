<script>
  import { onMount } from 'svelte';
  import { api } from '../api.js';
  import { notify, refreshData, triggerRefresh, selectedMonth, selectedYear } from '../store.js';
  import ConfirmDialog from './ConfirmDialog.svelte';

  let history = [];
  let loadingHistory = true;

  // Active Audit Wizard state
  let auditMonth = 5;
  let auditYear = 2026;
  let calculatedData = null;
  let loadingCalc = false;
  let declaredBalances = {}; // caja_id -> declared float string

  let submittingAudit = false;

  $: {
    if ($triggerRefresh >= 0) {
      loadHistory();
    }
  }

  onMount(() => {
    // Sincronizar el mes y año inicial del wizard con el store global
    auditMonth = $selectedMonth;
    auditYear = $selectedYear;
  });

  async function loadHistory() {
    loadingHistory = true;
    try {
      history = await api.getConciliacionesHistory();
    } catch (e) {
      notify("Error al cargar historial de auditorías: " + e.message, "error");
    } finally {
      loadingHistory = false;
    }
  }

  async function handleStartAudit() {
    loadingCalc = true;
    calculatedData = null;
    declaredBalances = {};
    
    try {
      calculatedData = await api.calculateConciliacion(auditMonth, auditYear);
      // Inicializar balances declarados con los calculados para facilitarle la carga
      calculatedData.cajas.forEach(c => {
        declaredBalances[c.caja_id] = c.saldo_calculado.toString();
      });
    } catch (e) {
      notify(e.message, "error");
    } finally {
      loadingCalc = false;
    }
  }

  let showConfirmAudit = false;
  let pendingAuditDetails = null;

  async function handleSubmitAudit() {
    // Validar balances ingresados
    const detalles = [];
    for (const c of calculatedData.cajas) {
      const realVal = parseFloat(declaredBalances[c.caja_id]);
      if (isNaN(realVal)) {
        notify(`Por favor ingresa un balance físico válido para la caja "${c.caja_nombre}".`, "warning");
        return;
      }
      detalles.push({
        caja_id: c.caja_id,
        saldo_real: realVal
      });
    }

    pendingAuditDetails = detalles;
    showConfirmAudit = true;
  }

  async function executeSubmitAudit() {
    if (!pendingAuditDetails) return;
    submittingAudit = true;
    try {
      await api.submitConciliacion({
        mes: auditMonth,
        anio: auditYear,
        detalles: pendingAuditDetails
      });
      notify(`¡Período ${auditMonth}/${auditYear} cerrado con éxito! Se aplicaron los ajustes necesarios.`);
      calculatedData = null;
      refreshData();
    } catch (e) {
      notify(e.message, "error");
    } finally {
      submittingAudit = false;
      pendingAuditDetails = null;
    }
  }

  function formatCurrency(val) {
    return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' })
      .format(val)
      .replace("ARS", "$");
  }

  function getNombreMes(n) {
    const nombres = {
      1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
      7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    };
    return nombres[n] || n.toString();
  }

  // Cómputo dinámico de diferencias de auditoría
  $: differences = calculatedData ? calculatedData.cajas.map(c => {
    const real = parseFloat(declaredBalances[c.caja_id]) || 0;
    const calc = parseFloat(c.saldo_calculado) || 0;
    const diff = real - calc;
    return {
      caja_id: c.caja_id,
      nombre: c.caja_nombre,
      calculado: calc,
      real: real,
      diferencia: diff
    };
  }) : [];

  $: totalDiscrepancies = differences.reduce((sum, d) => sum + Math.abs(d.diferencia), 0);
</script>

<div class="audit-wrapper animate-fade-in">
  <div class="audit-header">
    <div class="header-text">
      <h2>Auditoría y Conciliación Mensual</h2>
      <p class="text-secondary">Concilia saldos físicos, ajusta balances de sistema y bloquea cierres históricos</p>
    </div>
  </div>

  <div class="dashboard-grid">
    <!-- Columna Izquierda: Panel Activo de Conciliación -->
    <div class="col-8 glass-panel audit-panel">
      <div class="panel-header">
        <h3>Iniciar Nueva Auditoría</h3>
        <p class="text-secondary">Selecciona el mes calendario para contrastar tus saldos reales contra el libro mayor</p>
      </div>

      <!-- Form Selector -->
      <div class="audit-selector-form">
        <div class="form-row-selector">
          <div class="form-group-selector">
            <label for="auditMonth">Mes</label>
            <select id="auditMonth" bind:value={auditMonth} class="glass-input select-dark" disabled={loadingCalc || submittingAudit}>
              {#each Array(12) as _, i}
                <option value={i + 1}>{getNombreMes(i + 1)}</option>
              {/each}
            </select>
          </div>

          <div class="form-group-selector">
            <label for="auditYear">Año</label>
            <select id="auditYear" bind:value={auditYear} class="glass-input select-dark" disabled={loadingCalc || submittingAudit}>
              <option value={2026}>2026</option>
              <option value={2027}>2027</option>
            </select>
          </div>

          <button class="glass-btn glass-btn-primary" on:click={handleStartAudit} disabled={loadingCalc || submittingAudit}>
            {#if loadingCalc}
              Consultando...
            {:else}
              Iniciar Conciliación
            {/if}
          </button>
        </div>
      </div>

      <!-- Wizard Flow Steps -->
      {#if calculatedData}
        <div class="wizard-box glass-panel animate-fade-in">
          <div class="wizard-header">
            <h4>Auditoría del Período: <span class="accent-text">{getNombreMes(calculatedData.mes)} {calculatedData.anio}</span></h4>
            <span class="period-state-badge {calculatedData.cajas[0]?.ya_conciliado ? 'closed-badge' : 'open-badge'}">
              {calculatedData.cajas[0]?.ya_conciliado ? 'CERRADO (Lectura)' : 'ABIERTO (Borrador)'}
            </span>
          </div>

          {#if calculatedData.cajas[0]?.ya_conciliado}
            <div class="alert-box alert-info">
              <svg xmlns="http://www.w3.org/2000/svg" class="alert-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>El período seleccionado ya se encuentra cerrado. Para ver el detalle conciliado histórico, consulta el historial en el panel derecho.</span>
            </div>
          {:else}
            <!-- Inputs Sheet -->
            <div class="inputs-grid">
              <div class="grid-header">
                <span>Caja / Cuenta</span>
                <span class="text-right">Saldo en Sistema</span>
                <span class="text-right">Saldo Físico Real ($)</span>
                <span class="text-right">Diferencia</span>
              </div>

              {#each calculatedData.cajas as caja}
                {@const diffObj = differences.find(d => d.caja_id === caja.caja_id) || { diferencia: 0 }}
                <div class="grid-row glass-panel-hover">
                  <div class="caja-name-cell">
                    <span class="dot-indicator {caja.caja_tipo}"></span>
                    <span>{caja.caja_nombre}</span>
                  </div>
                  <div class="text-right financial-num">{formatCurrency(caja.saldo_calculado)}</div>
                  <div class="text-right input-cell">
                    <input 
                      type="number" 
                      step="0.01" 
                      bind:value={declaredBalances[caja.caja_id]} 
                      class="glass-input financial-num font-sm text-right inline-input" 
                      disabled={submittingAudit}
                    />
                  </div>
                  <div class="text-right financial-num {diffObj.diferencia > 0 ? 'text-emerald' : diffObj.diferencia < 0 ? 'text-rose' : 'text-muted'}">
                    {diffObj.diferencia > 0 ? '+' : ''}{formatCurrency(diffObj.diferencia)}
                  </div>
                </div>
              {/each}
            </div>

            <!-- Discrepancy Warnings -->
            {#if totalDiscrepancies > 0}
              <div class="alert-box alert-warning animate-fade-in">
                <svg xmlns="http://www.w3.org/2000/svg" class="alert-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div class="warning-text">
                  <h5>Advertencia de Discrepancia Financiera</h5>
                  <p>Se detectó una discrepancia total acumulada de {formatCurrency(totalDiscrepancies)}. El sistema registrará de forma automática las transacciones de <strong>Ajuste por Conciliación</strong> para cuadrar tus cuentas perfectamente al cierre de mes.</p>
                </div>
              </div>
            {:else}
              <div class="alert-box alert-success animate-fade-in">
                <svg xmlns="http://www.w3.org/2000/svg" class="alert-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>¡Perfecto! Los saldos físicos coinciden al 100% con los saldos de sistema. No se generarán transacciones de ajuste adicionales.</span>
              </div>
            {/if}

            <div class="wizard-footer">
              <button class="glass-btn glass-btn-secondary" on:click={() => calculatedData = null} disabled={submittingAudit}>
                Cancelar
              </button>
              <button class="glass-btn glass-btn-primary" on:click={handleSubmitAudit} disabled={submittingAudit}>
                {#if submittingAudit}
                  Procesando Cierre...
                {:else}
                  Confirmar y Cerrar Período
                {/if}
              </button>
            </div>
          {/if}
        </div>
      {/if}
    </div>

    <!-- Columna Derecha: Historial de Cierres -->
    <div class="col-4 glass-panel history-panel">
      <div class="panel-header">
        <h3>Historial de Cierres</h3>
        <p class="text-secondary">Consulta los períodos cerrados y las discrepancias ajustadas históricamente</p>
      </div>

      {#if loadingHistory}
        <div class="spinner-small"></div>
      {:else if history.length === 0}
        <div class="empty-state">No se registran cierres de mes en el sistema todavía.</div>
      {:else}
        <div class="history-timeline">
          {#each history as hc}
            <div class="history-card glass-panel-hover">
              <div class="hc-header">
                <span class="hc-period font-sans">{getNombreMes(hc.mes)} {hc.anio}</span>
                <span class="hc-badge">CERRADO</span>
              </div>
              
              <div class="hc-meta font-xs text-secondary">
                Auditoría: {new Date(hc.fecha_conciliacion).toLocaleString()}
              </div>

              <!-- Cajas Conciliadas -->
              <div class="hc-details">
                {#each hc.detalles as d}
                  <div class="hc-row">
                    <span class="hc-caja-name">{d.caja.nombre}</span>
                    <div class="hc-amounts">
                      <span class="financial-num font-sm text-secondary">{formatCurrency(d.saldo_real)}</span>
                      {#if d.diferencia != 0}
                        <span class="dif-mini {d.diferencia > 0 ? 'text-emerald' : 'text-rose'}">
                          ({d.diferencia > 0 ? '+' : ''}{formatCurrency(d.diferencia)})
                        </span>
                      {:else}
                        <span class="dif-mini text-muted">(Ok)</span>
                      {/if}
                    </div>
                  </div>
                {/each}
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>
</div>

<ConfirmDialog
  bind:show={showConfirmAudit}
  title="Cerrar y Conciliar Período"
  message={`¿Estás seguro de que deseas cerrar y conciliar el período ${auditMonth}/${auditYear}? Esta acción es irreversible e inmutabilizará el mes.`}
  confirmLabel="Cerrar Período"
  cancelLabel="Cancelar"
  variant="warning"
  onConfirm={executeSubmitAudit}
/>

<style>
  .audit-wrapper {
    max-width: 96%;
    margin: 0 auto;
    padding: 0 40px 40px 40px;
    width: 100%;
  }

  .audit-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 28px;
    margin-top: 15px;
    width: 100%;
  }

  .header-text h2 {
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #ffffff;
  }

  .col-8 { grid-column: span 8; }
  .col-4 { grid-column: span 4; }

  .audit-panel, .history-panel {
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .panel-header h3 {
    font-size: 1.15rem;
    font-weight: 700;
  }

  /* Formulario Selector */
  .audit-selector-form {
    background: rgba(255, 255, 255, 0.015);
    border: 1px solid rgba(255, 255, 255, 0.03);
    border-radius: 12px;
    padding: 16px;
  }

  .form-row-selector {
    display: flex;
    align-items: flex-end;
    gap: 16px;
  }

  @media (max-width: 580px) {
    .form-row-selector {
      flex-direction: column;
      align-items: stretch;
      gap: 12px;
    }
  }

  .form-group-selector {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .form-group-selector label {
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--text-secondary);
  }

  /* Wizard */
  .wizard-box {
    padding: 20px;
    border-color: rgba(255, 255, 255, 0.08);
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .wizard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    padding-bottom: 12px;
  }

  .wizard-header h4 {
    font-size: 1.05rem;
    font-weight: 700;
  }

  .accent-text {
    background: linear-gradient(135deg, var(--accent-purple) 0%, var(--accent-blue) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .period-state-badge {
    font-size: 0.72rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 9999px;
  }

  .open-badge {
    background: rgba(59, 130, 246, 0.1);
    color: var(--accent-blue);
    border: 1px solid rgba(59, 130, 246, 0.2);
  }

  .closed-badge {
    background: rgba(16, 185, 129, 0.1);
    color: var(--accent-emerald);
    border: 1px solid rgba(16, 185, 129, 0.2);
  }

  /* Alert Box */
  .alert-box {
    display: flex;
    padding: 14px 18px;
    border-radius: 12px;
    gap: 12px;
    align-items: flex-start;
    font-size: 0.85rem;
  }

  .alert-icon {
    width: 20px;
    height: 20px;
    flex-shrink: 0;
  }

  .alert-info {
    background: rgba(59, 130, 246, 0.08);
    border: 1px solid rgba(59, 130, 246, 0.15);
    color: var(--text-secondary);
  }
  .alert-info .alert-icon { color: var(--accent-blue); }

  .alert-warning {
    background: rgba(245, 158, 11, 0.08);
    border: 1px solid rgba(245, 158, 11, 0.15);
    color: var(--text-secondary);
  }
  .alert-warning .alert-icon { color: var(--accent-amber); }
  .warning-text h5 { color: var(--accent-amber); font-weight: 700; margin-bottom: 4px; font-size: 0.88rem; }

  .alert-success {
    background: rgba(16, 185, 129, 0.08);
    border: 1px solid rgba(16, 185, 129, 0.15);
    color: var(--text-secondary);
  }
  .alert-success .alert-icon { color: var(--accent-emerald); }

  /* Inputs Grid */
  .inputs-grid {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .grid-header {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr;
    padding: 8px 12px;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .grid-row {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr;
    align-items: center;
    padding: 10px 12px;
    border-radius: 10px;
    background: rgba(255,255,255,0.01);
    border: 1px solid rgba(255,255,255,0.03);
  }

  .text-right { text-align: right; }

  .caja-name-cell {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 500;
  }

  .dot-indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }
  .dot-indicator.EFECTIVO { background-color: var(--accent-emerald); }
  .dot-indicator.BANCO { background-color: var(--accent-blue); }
  .dot-indicator.TARJETA_DEBITO { background-color: var(--accent-purple); }
  .dot-indicator.OTRO { background-color: var(--accent-amber); }

  .input-cell {
    display: flex;
    justify-content: flex-end;
  }

  .inline-input {
    width: 100px;
    padding: 6px 10px;
  }

  .wizard-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    padding-top: 16px;
  }

  /* History Timeline */
  .history-timeline {
    display: flex;
    flex-direction: column;
    gap: 16px;
    max-height: 480px;
    overflow-y: auto;
    padding-right: 4px;
  }

  .history-card {
    padding: 16px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.015);
    border: 1px solid rgba(255, 255, 255, 0.03);
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .hc-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .hc-period {
    font-size: 0.95rem;
    font-weight: 700;
  }

  .hc-badge {
    font-size: 0.65rem;
    font-weight: 800;
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.2);
    color: var(--accent-emerald);
    padding: 1px 6px;
    border-radius: 4px;
  }

  .font-xs { font-size: 0.75rem; }

  .hc-details {
    display: flex;
    flex-direction: column;
    gap: 6px;
    border-top: 1px dashed rgba(255, 255, 255, 0.05);
    padding-top: 8px;
    margin-top: 4px;
  }

  .hc-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .hc-caja-name {
    font-size: 0.8rem;
    color: var(--text-secondary);
  }

  .hc-amounts {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .dif-mini {
    font-size: 0.72rem;
    font-weight: 600;
  }

  .spinner-small {
    width: 24px;
    height: 24px;
    border: 2px solid rgba(255, 255, 255, 0.05);
    border-top: 2px solid var(--accent-purple);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 20px auto;
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
</style>
