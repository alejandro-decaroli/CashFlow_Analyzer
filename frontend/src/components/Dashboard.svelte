<script>
  import { onMount } from 'svelte';
  import { api } from '../api.js';
  import { selectedMonth, selectedYear, triggerRefresh, notify } from '../store.js';
  import TransactionModal from './TransactionModal.svelte';

  // State variables for dashboard data
  let kpis = {
    ingreso_bruto: 0,
    gasto_total: 0,
    ingreso_neto: 0,
    ahorro_acumulado: 0
  };
  let momExpenses = [];
  let averages = [];
  let topExpenses = [];
  let chartsData = [];
  let loading = true;

  // Transaction Modal triggers
  let showModal = false;
  let modalType = 'GASTO'; // 'GASTO' o 'INGRESO'

  // Reactive updates when global period or refresh trigger changes
  $: {
    if ($selectedMonth && $selectedYear || $triggerRefresh >= 0) {
      loadDashboardData();
    }
  }

  async function loadDashboardData() {
    loading = true;
    try {
      const [kpiRes, momRes, avgRes, topRes, chartRes] = await Promise.all([
        api.getDashboardKPIs($selectedMonth, $selectedYear),
        api.getDashboardMoM($selectedMonth, $selectedYear),
        api.getDashboardAverages(),
        api.getDashboardTopExpenses($selectedMonth, $selectedYear),
        api.getDashboardCharts()
      ]);

      kpis = kpiRes;
      momExpenses = momRes;
      averages = avgRes;
      topExpenses = topRes;
      chartsData = chartRes;
    } catch (e) {
      notify("Error al cargar datos del tablero: " + e.message, "error");
    } finally {
      loading = false;
    }
  }

  function openTransactionModal(type) {
    modalType = type;
    showModal = true;
  }

  function formatCurrency(val) {
    return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' })
      .format(val)
      .replace("ARS", "$");
  }

  // Reactive calculations for custom SVG chart
  let svgWidth = 600;
  let svgHeight = 260;
  let padding = { top: 30, right: 20, bottom: 40, left: 60 };

  $: maxVal = Math.max(
    ...chartsData.map(d => Math.max(d.ingresos, d.gastos, 1000))
  ) * 1.1; // 10% headroom

  $: points = chartsData.map((d, i) => {
    const x = padding.left + (i * (svgWidth - padding.left - padding.right) / Math.max(chartsData.length - 1, 1));
    const yIngresos = svgHeight - padding.bottom - (d.ingresos / maxVal * (svgHeight - padding.top - padding.bottom));
    const yGastos = svgHeight - padding.bottom - (d.gastos / maxVal * (svgHeight - padding.top - padding.bottom));
    return { x, yIngresos, yGastos, label: d.label, raw: d };
  });

  let activeChartIndex = null;
</script>

<div class="dashboard-wrapper animate-fade-in">
  <!-- Cabecera de Acciones -->
  <div class="dashboard-header">
    <div class="header-text">
      <h2>Resumen de Operaciones</h2>
      <p class="text-secondary">Monitorea y audita los movimientos de tu hogar en tiempo real</p>
    </div>
    
    <div class="header-actions">
      <button class="glass-btn btn-income-solid" on:click={() => openTransactionModal('INGRESO')}>
        <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Registrar Ingreso
      </button>
      <button class="glass-btn btn-expense-solid" on:click={() => openTransactionModal('GASTO')}>
        <svg xmlns="http://www.w3.org/2000/svg" class="btn-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
        </svg>
        Registrar Gasto
      </button>
    </div>
  </div>

  {#if loading}
    <div class="loading-state glass-panel">
      <div class="spinner"></div>
      <p>Procesando métricas financieras...</p>
    </div>
  {:else}
    <!-- Grid de Tarjetas KPI -->
    <div class="kpi-grid">
      <!-- Ingreso Bruto -->
      <div class="glass-panel kpi-card border-emerald">
        <div class="kpi-meta">
          <span class="kpi-title">Ingreso Bruto</span>
          <span class="kpi-icon text-emerald">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </span>
        </div>
        <div class="kpi-value financial-num text-emerald">{formatCurrency(kpis.ingreso_bruto)}</div>
        <p class="kpi-desc">Total percibido en el mes seleccionado</p>
        <div class="card-glow glow-emerald"></div>
      </div>

      <!-- Gasto Total -->
      <div class="glass-panel kpi-card border-rose">
        <div class="kpi-meta">
          <span class="kpi-title">Gasto Total</span>
          <span class="kpi-icon text-rose">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0v-8m0 8l-8-8-4 4-6-6" />
            </svg>
          </span>
        </div>
        <div class="kpi-value financial-num text-rose">{formatCurrency(kpis.gasto_total)}</div>
        <p class="kpi-desc">Egresos totales del período actual</p>
        <div class="card-glow glow-rose"></div>
      </div>

      <!-- Ingreso Neto -->
      <div class="glass-panel kpi-card border-blue">
        <div class="kpi-meta">
          <span class="kpi-title">Ingreso Neto</span>
          <span class="kpi-icon text-blue">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 002 2h2a2 2 0 002-2z" />
            </svg>
          </span>
        </div>
        <div class="kpi-value financial-num {kpis.ingreso_neto >= 0 ? 'text-blue' : 'text-rose'}">
          {formatCurrency(kpis.ingreso_neto)}
        </div>
        <p class="kpi-desc">Superávit o déficit del mes (Bruto - Gastos)</p>
        <div class="card-glow glow-blue"></div>
      </div>

      <!-- Ahorro Acumulado -->
      <div class="glass-panel kpi-card border-purple">
        <div class="kpi-meta">
          <span class="kpi-title">Ahorro Acumulado</span>
          <span class="kpi-icon text-purple">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </span>
        </div>
        <div class="kpi-value financial-num text-purple">{formatCurrency(kpis.ahorro_acumulado)}</div>
        <p class="kpi-desc">Saldo consolidado de todas tus cajas activas</p>
        <div class="card-glow glow-purple"></div>
      </div>
    </div>

    <!-- Gráfico Analítico de Tendencias Históricas (SVG Premium) -->
    <div class="glass-panel trend-chart-panel">
      <div class="chart-header">
        <div class="chart-title">
          <h3>Evolución Mensual (Últimos 6 Meses)</h3>
          <p class="text-secondary">Comparativa de ingresos totales frente a egresos registrados</p>
        </div>
        <div class="chart-legend">
          <span class="legend-item"><span class="legend-dot bg-emerald-dot"></span> Ingresos</span>
          <span class="legend-item"><span class="legend-dot bg-rose-dot"></span> Gastos</span>
        </div>
      </div>
      
      {#if chartsData.length === 0}
        <div class="empty-state">No hay suficientes datos históricos para graficar la evolución.</div>
      {:else}
        <div class="svg-container">
          <svg viewBox="0 0 {svgWidth} {svgHeight}" class="interactive-svg">
            <defs>
              <linearGradient id="ingresoGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="var(--accent-emerald)" stop-opacity="0.3"/>
                <stop offset="100%" stop-color="var(--accent-emerald)" stop-opacity="0.0"/>
              </linearGradient>
              <linearGradient id="gastoGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="var(--accent-rose)" stop-opacity="0.3"/>
                <stop offset="100%" stop-color="var(--accent-rose)" stop-opacity="0.0"/>
              </linearGradient>
            </defs>

            <!-- Grid Lines -->
            {#each Array(5) as _, i}
              {@const y = padding.top + (i * (svgHeight - padding.top - padding.bottom) / 4)}
              {@const val = maxVal - (i * maxVal / 4)}
              <line 
                x1={padding.left} 
                y1={y} 
                x2={svgWidth - padding.right} 
                y2={y} 
                stroke="rgba(255, 255, 255, 0.15)" 
                stroke-width="1"
              />
              <text 
                x={padding.left - 12} 
                y={y + 4} 
                fill="#ffffff" 
                font-size="10" 
                font-weight="bold"
                text-anchor="end"
                font-family="var(--font-mono)"
              >
                {formatCurrency(val).split(',')[0]}
              </text>
            {/each}

            <!-- Ejes Baselines (Blanco) -->
            <line 
              x1={padding.left} 
              y1={svgHeight - padding.bottom} 
              x2={svgWidth - padding.right} 
              y2={svgHeight - padding.bottom} 
              stroke="#ffffff" 
              stroke-width="2"
            />
            <line 
              x1={padding.left} 
              y1={padding.top} 
              x2={padding.left} 
              y2={svgHeight - padding.bottom} 
              stroke="#ffffff" 
              stroke-width="2"
            />

            <!-- Área y Línea de Ingresos (Verde Vibrante) -->
            {#if points.length > 1}
              {@const ingPath = points.map(p => `${p.x},${p.yIngresos}`).join(' ')}
              <path 
                d="M {points[0].x} {svgHeight - padding.bottom} L {ingPath} L {points[points.length - 1].x} {svgHeight - padding.bottom} Z" 
                fill="url(#ingresoGrad)" 
              />
              <path 
                d="M {ingPath}" 
                fill="none" 
                stroke="#10b981" 
                stroke-width="3" 
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            {/if}

            <!-- Área y Línea de Gastos (Rojo Vibrante) -->
            {#if points.length > 1}
              {@const gasPath = points.map(p => `${p.x},${p.yGastos}`).join(' ')}
              <path 
                d="M {points[0].x} {svgHeight - padding.bottom} L {gasPath} L {points[points.length - 1].x} {svgHeight - padding.bottom} Z" 
                fill="url(#gastoGrad)" 
              />
              <path 
                d="M {gasPath}" 
                fill="none" 
                stroke="#ef4444" 
                stroke-width="3" 
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            {/if}

            <!-- Nodos Interactivos (Hover Circles) -->
            {#each points as p, i}
              <!-- Eje X Labels (Blanco Negrita) -->
              <text 
                x={p.x} 
                y={svgHeight - padding.bottom + 20} 
                fill="#ffffff" 
                font-size="11" 
                font-weight="bold"
                text-anchor="middle"
              >
                {p.label.split(' ')[0]}
              </text>

              <!-- Elementos interactivos invisibles para facilitar hover -->
              <!-- svelte-ignore a11y-mouse-events-have-key-events -->
              <rect 
                x={p.x - 25} 
                y={padding.top} 
                width="50" 
                height={svgHeight - padding.top - padding.bottom} 
                fill="transparent" 
                style="cursor: pointer;"
                on:mouseover={() => activeChartIndex = i}
                on:mouseout={() => activeChartIndex = null}
              />

              <!-- Nodos circulares -->
              <circle 
                cx={p.x} 
                cy={p.yIngresos} 
                r={activeChartIndex === i ? 6 : 4} 
                fill="#fff" 
                stroke="var(--accent-emerald)" 
                stroke-width={activeChartIndex === i ? 3 : 2} 
                transition:all 
              />
              <circle 
                cx={p.x} 
                cy={p.yGastos} 
                r={activeChartIndex === i ? 6 : 4} 
                fill="#fff" 
                stroke="var(--accent-rose)" 
                stroke-width={activeChartIndex === i ? 3 : 2} 
                transition:all 
              />
            {/each}
          </svg>

          <!-- Floating Tooltip Reactivo -->
          {#if activeChartIndex !== null}
            {@const p = points[activeChartIndex]}
            <div 
              class="chart-tooltip glass-panel animate-fade-in" 
              style="left: {p.x}px; top: {Math.min(p.yIngresos, p.yGastos) - 75}px;"
            >
              <div class="tooltip-month">{p.raw.label}</div>
              <div class="tooltip-row text-emerald">
                <span>Ingresos:</span>
                <span class="financial-num">{formatCurrency(p.raw.ingresos)}</span>
              </div>
              <div class="tooltip-row text-rose">
                <span>Gastos:</span>
                <span class="financial-num">{formatCurrency(p.raw.gastos)}</span>
              </div>
              <div class="tooltip-row border-top text-blue">
                <span>Neto:</span>
                <span class="financial-num">{formatCurrency(p.raw.ingresos - p.raw.gastos)}</span>
              </div>
            </div>
          {/if}
        </div>
      {/if}
    </div>

    <!-- Grillas Detalladas: Top Gastos, Variación MoM y Medias Históricas -->
    <div class="dashboard-grid">
      <!-- Columna Izquierda: Top Gastos y Promedios -->
      <div class="col-8 glass-panel list-panel">
        <div class="panel-header">
          <h3>Top 5 Gastos Mayores</h3>
          <p class="text-secondary">Los egresos de mayor volumen registrados este mes</p>
        </div>

        {#if topExpenses.length === 0}
          <div class="empty-state">No se registraron egresos en este período.</div>
        {:else}
          <div class="expense-list">
            {#each topExpenses as exp, index}
              <div class="expense-item glass-panel-hover">
                <div class="expense-index financial-num">#{index + 1}</div>
                <div class="expense-meta">
                  <div class="expense-desc">{exp.descripcion || 'Sin descripción'}</div>
                  <div class="expense-sub">
                    <span class="category-badge" style="background-color: {exp.color}20; border-color: {exp.color}; color: {exp.color}">
                      {exp.categoria_nombre}
                    </span>
                    <span class="caja-sub">{exp.caja_nombre} • {exp.fecha}</span>
                  </div>
                </div>
                <div class="expense-amount financial-num text-rose">
                  -{formatCurrency(exp.monto)}
                </div>
              </div>
            {/each}
          </div>
        {/if}

        <hr class="panel-divider" />

        <div class="panel-header" style="margin-top: 10px;">
          <h3>Promedios Mensuales Históricos</h3>
          <p class="text-secondary">Gasto promedio histórico acumulado por cada categoría</p>
        </div>

        {#if averages.length === 0}
          <div class="empty-state">Sin datos históricos suficientes.</div>
        {:else}
          <div class="averages-grid">
            {#each averages as avg}
              <div class="average-card">
                <div class="average-meta">
                  <span class="color-dot" style="background-color: {avg.color}"></span>
                  <span class="average-name">{avg.categoria_nombre}</span>
                </div>
                <div class="average-val">
                  <span class="financial-num">{formatCurrency(avg.promedio_mensual)}</span>
                  <span class="text-muted font-xs">/ mes</span>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <!-- Columna Derecha: Variación Mes a Mes (MoM%) -->
      <div class="col-4 glass-panel list-panel">
        <div class="panel-header">
          <h3>Variación Mes a Mes (MoM)</h3>
          <p class="text-secondary">Comparativa de egresos vs el mes anterior</p>
        </div>

        {#if momExpenses.length === 0}
          <div class="empty-state">Registra gastos para calcular la variación.</div>
        {:else}
          <div class="mom-list">
            {#each momExpenses as mom}
              <div class="mom-item">
                <div class="mom-meta">
                  <span class="color-dot" style="background-color: {mom.color}"></span>
                  <span class="mom-name">{mom.categoria_nombre}</span>
                </div>
                
                <div class="mom-values">
                  <div class="mom-amounts">
                    <span class="financial-num font-sm">{formatCurrency(mom.gasto_mes_actual)}</span>
                    <span class="text-muted font-xs">vs {formatCurrency(mom.gasto_mes_anterior)}</span>
                  </div>

                  <!-- Badge de Variación -->
                  {#if mom.variacion_porcentual > 0}
                    <span class="mom-badge bg-rose-badge">
                      <svg xmlns="http://www.w3.org/2000/svg" class="arrow-icon" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clip-rule="evenodd" />
                      </svg>
                      +{mom.variacion_porcentual}%
                    </span>
                  {:else if mom.variacion_porcentual < 0}
                    <span class="mom-badge bg-emerald-badge">
                      <svg xmlns="http://www.w3.org/2000/svg" class="arrow-icon" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                      </svg>
                      {mom.variacion_porcentual}%
                    </span>
                  {:else}
                    <span class="mom-badge bg-gray-badge">
                      0.00%
                    </span>
                  {/if}
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>

<!-- Modal global para transacciones -->
<TransactionModal 
  show={showModal} 
  type={modalType} 
  onClose={() => showModal = false} 
/>

<style>
  .dashboard-wrapper {
    display: flex;
    flex-direction: column;
    gap: 32px;
    max-width: 96%;
    margin: 0 auto;
    padding: 0 40px 40px 40px;
    width: 100%;
  }

  .dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 15px;
    width: 100%;
  }

  @media (max-width: 768px) {
    .dashboard-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 20px;
    }
    
    .header-actions {
      display: flex;
      width: 100%;
      gap: 15px;
    }
    
    .header-actions button {
      flex: 1;
    }
  }

  .header-text h2 {
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #ffffff;
  }

  .header-actions {
    display: flex;
    gap: 16px;
    align-items: center;
  }

  .btn-icon {
    width: 18px;
    height: 18px;
    margin-right: 8px;
  }

  /* Botones Sólidos Identificatorios Premium */
  .btn-income-solid {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    color: #ffffff !important;
    border: 1px solid #10b981 !important;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
    transition: var(--transition-elastic) !important;
  }
  .btn-income-solid:hover {
    box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5) !important;
    filter: brightness(1.15) !important;
    transform: translateY(-2px);
  }

  .btn-expense-solid {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
    color: #ffffff !important;
    border: 1px solid #ef4444 !important;
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3) !important;
    transition: var(--transition-elastic) !important;
  }
  .btn-expense-solid:hover {
    box-shadow: 0 6px 20px rgba(239, 68, 68, 0.5) !important;
    filter: brightness(1.15) !important;
    transform: translateY(-2px);
  }

  /* Spinner de carga */
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

  /* Grid KPIs */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 24px;
    width: 100%;
  }

  @media (max-width: 1024px) {
    .kpi-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  @media (max-width: 580px) {
    .kpi-grid {
      grid-template-columns: 1fr;
    }
  }

  /* Tarjetas KPI Perfectamente Centradas */
  .kpi-card {
    position: relative;
    padding: 24px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    overflow: hidden;
    border-radius: 16px;
    border: 1px solid var(--border-glass);
    background: var(--bg-card);
    transition: var(--transition-smooth);
  }
  .kpi-card:hover {
    transform: translateY(-3px);
    border-color: var(--border-glass-hover);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
  }

  .border-emerald { border-top: 4px solid #10b981; border-left: none; }
  .border-rose { border-top: 4px solid #ef4444; border-left: none; }
  .border-blue { border-top: 4px solid #3b82f6; border-left: none; }
  .border-purple { border-top: 4px solid #8b5cf6; border-left: none; }

  .kpi-meta {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
    width: 100%;
  }

  .kpi-title {
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.8px;
  }

  .kpi-icon {
    width: 24px;
    height: 24px;
    margin-bottom: 4px;
  }

  .kpi-icon svg {
    width: 100%;
    height: 100%;
  }

  .kpi-value {
    font-size: 1.85rem;
    margin-bottom: 8px;
    font-weight: 700;
  }

  .kpi-desc {
    font-size: 0.78rem;
    color: var(--text-muted);
  }

  /* Card Glow Effects */
  .card-glow {
    position: absolute;
    width: 100px;
    height: 100px;
    border-radius: 50%;
    filter: blur(40px);
    opacity: 0.08;
    pointer-events: none;
    top: -30px;
    right: -30px;
  }

  .glow-emerald { background: var(--accent-emerald); }
  .glow-rose { background: var(--accent-rose); }
  .glow-blue { background: var(--accent-blue); }
  .glow-purple { background: var(--accent-purple); }

  /* Panel Gráfico */
  .trend-chart-panel {
    padding: 4%;
    border-color: rgba(255, 255, 255, 0.04);
  }

  .chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }

  @media (max-width: 580px) {
    .chart-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
    }
  }

  .chart-title h3 {
    font-size: 1.15rem;
    font-weight: 700;
  }

  .chart-legend {
    display: flex;
    gap: 16px;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.85rem;
    color: var(--text-secondary);
  }

  .legend-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
  }

  .bg-emerald-dot { background-color: var(--accent-emerald); }
  .bg-rose-dot { background-color: var(--accent-rose); }

  .svg-container {
    position: relative;
    width: 100%;
    margin-top: 10px;
  }

  .interactive-svg {
    width: 100%;
    height: auto;
    overflow: visible;
  }

  /* Custom SVG Tooltip */
  .chart-tooltip {
    position: absolute;
    transform: translateX(-50%);
    padding: 10px 14px;
    min-width: 150px;
    border-color: rgba(255, 255, 255, 0.12);
    pointer-events: none;
    z-index: 10;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
  }

  .tooltip-month {
    font-size: 0.8rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 6px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 4px;
  }

  .tooltip-row {
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
    gap: 12px;
  }

  .border-top {
    border-top: 1px dashed rgba(255, 255, 255, 0.1);
    margin-top: 4px;
    padding-top: 4px;
    font-weight: 600;
  }

  /* List Panes & Grid */
  .list-panel {
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .col-8 {
    grid-column: span 8;
  }

  .col-4 {
    grid-column: span 4;
  }

  .panel-header h3 {
    font-size: 1.15rem;
    font-weight: 700;
  }

  .panel-divider {
    border: none;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    margin: 10px 0;
  }

  .empty-state {
    color: var(--text-muted);
    font-size: 0.9rem;
    text-align: center;
    padding: 30px;
    background: rgba(255, 255, 255, 0.01);
    border: 1px dashed rgba(255,255,255,0.05);
    border-radius: 8px;
  }

  /* Lista de Gastos */
  .expense-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .expense-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 20px;
    gap: 20px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    transition: var(--transition-smooth);
  }
  .expense-item:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.1);
    transform: translateX(6px);
  }

  .expense-index {
    font-size: 1.15rem;
    color: #ef4444;
    font-weight: 800;
    width: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: var(--font-mono);
  }

  .expense-meta {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 6px;
  }

  .expense-desc {
    font-size: 1.05rem;
    font-weight: 600;
    color: #ffffff;
  }

  .expense-sub {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .category-badge {
    font-size: 0.78rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 9999px;
    border: 1px solid transparent;
  }

  .caja-sub {
    font-size: 0.78rem;
    color: var(--text-secondary);
  }

  .expense-amount {
    font-size: 1.2rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    font-family: var(--font-mono);
  }

  /* Promedios Grid */
  .averages-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
  }

  @media (max-width: 640px) {
    .averages-grid {
      grid-template-columns: 1fr;
    }
  }

  .average-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 10px;
    padding: 12px 14px;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .average-meta {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .color-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
  }

  .average-name {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-secondary);
  }

  .average-val {
    font-size: 0.95rem;
  }

  .font-xs { font-size: 0.75rem; }
  .font-sm { font-size: 0.88rem; }

  /* MoM List */
  .mom-list {
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  .mom-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  }

  .mom-item:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }

  .mom-meta {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .mom-name {
    font-size: 0.88rem;
    font-weight: 500;
  }

  .mom-values {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .mom-amounts {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
  }

  .mom-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.78rem;
    font-weight: 700;
  }

  .bg-rose-badge {
    background: rgba(239, 68, 68, 0.12);
    border: 1px solid rgba(239, 68, 68, 0.2);
    color: var(--accent-rose);
  }

  .bg-emerald-badge {
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.2);
    color: var(--accent-emerald);
  }

  .bg-gray-badge {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: var(--text-secondary);
  }

  .arrow-icon {
    width: 12px;
    height: 12px;
  }
</style>
