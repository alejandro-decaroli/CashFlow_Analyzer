import { writable } from 'svelte/store';

export const activeTab = writable('dashboard');

// Por defecto, iniciamos en el mes calendario de Mayo 2026 (según los requerimientos de Alejandro)
export const selectedMonth = writable(5);
export const selectedYear = writable(2026);

// Almacena alertas del sistema: { message: '', type: 'success' | 'error' | 'warning' }
export const notification = writable(null);

// Trigger global para recargar datos cruzados en el dashboard y transacciones
export const triggerRefresh = writable(0);

export function notify(message, type = 'success') {
  notification.set({ message, type });
  setTimeout(() => {
    notification.set(null);
  }, 4000);
}

export function refreshData() {
  triggerRefresh.update(n => n + 1);
}
