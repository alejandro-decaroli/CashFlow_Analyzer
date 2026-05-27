const API_BASE = "http://localhost:8000/api";

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };
  
  const response = await fetch(url, { ...options, headers });
  
  if (response.status === 204) {
    return null;
  }
  
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Ha ocurrido un error inesperado en el servidor.");
  }
  
  return data;
}

export const api = {
  // CAJAS
  getCajas: () => request("/cajas"),
  getAllCajas: () => request("/cajas/all"),
  createCaja: (data) => request("/cajas/", { method: "POST", body: JSON.stringify(data) }),
  updateCaja: (id, data) => request(`/cajas/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteCaja: (id) => request(`/cajas/${id}`, { method: "DELETE" }),

  // CATEGORIAS & FUENTES
  getCategorias: () => request("/transacciones/categorias"),
  getAllCategorias: () => request("/transacciones/categorias/all"),
  createCategoria: (data) => request("/transacciones/categorias", { method: "POST", body: JSON.stringify(data) }),
  deleteCategoria: (id) => request(`/transacciones/categorias/${id}`, { method: "DELETE" }),
  
  getFuentes: () => request("/transacciones/fuentes"),
  getAllFuentes: () => request("/transacciones/fuentes/all"),
  createFuente: (data) => request("/transacciones/fuentes", { method: "POST", body: JSON.stringify(data) }),
  deleteFuente: (id) => request(`/transacciones/fuentes/${id}`, { method: "DELETE" }),

  // TRANSACCIONES
  getTransactionsFeed: () => request("/transacciones/feed"),
  createGasto: (data) => request("/transacciones/gastos", { method: "POST", body: JSON.stringify(data) }),
  deleteGasto: (id) => request(`/transacciones/gastos/${id}`, { method: "DELETE" }),
  createIngreso: (data) => request("/transacciones/ingresos", { method: "POST", body: JSON.stringify(data) }),
  deleteIngreso: (id) => request(`/transacciones/ingresos/${id}`, { method: "DELETE" }),

  // CONCILIACIÓN
  getConciliacionesHistory: () => request("/conciliacion/history"),
  calculateConciliacion: (mes, anio) => request(`/conciliacion/calculate?mes=${mes}&anio=${anio}`),
  submitConciliacion: (data) => request("/conciliacion/submit", { method: "POST", body: JSON.stringify(data) }),

  // DASHBOARD
  getDashboardKPIs: (mes, anio) => request(`/dashboard/kpis?mes=${mes}&anio=${anio}`),
  getDashboardMoM: (mes, anio) => request(`/dashboard/mom?mes=${mes}&anio=${anio}`),
  getDashboardAverages: () => request("/dashboard/averages"),
  getDashboardTopExpenses: (mes, anio) => request(`/dashboard/top-expenses?mes=${mes}&anio=${anio}`),
  getDashboardCharts: () => request("/dashboard/charts"),
};
