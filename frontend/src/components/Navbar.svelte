<script>
  import { activeTab } from '../store.js';

  let currentTab;
  activeTab.subscribe(value => {
    currentTab = value;
  });

  const menuItems = [
    { id: 'dashboard', label: 'Tablero', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
    { id: 'transacciones', label: 'Movimientos', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01' },
    { id: 'cajas', label: 'Cajas', icon: 'M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z' },
    { id: 'conciliacion', label: 'Auditoría', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
    { id: 'catalogos', label: 'Catálogos', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z' }
  ];

  function setTab(tab) {
    activeTab.set(tab);
  }
</script>

<!-- Top Navbar (Desktop) -->
<header class="desktop-nav glass-panel">
  <div class="logo">
    <svg xmlns="http://www.w3.org/2000/svg" class="logo-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
    <span class="logo-text">CashFlow <span class="accent-text">Analyzer</span></span>
  </div>
  
  <nav class="nav-links">
    {#each menuItems as item}
      <button 
        class="nav-btn {currentTab === item.id ? 'active' : ''}" 
        on:click={() => setTab(item.id)}
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={item.icon} />
        </svg>
        {item.label}
      </button>
    {/each}
  </nav>
</header>

<!-- Mobile Bottom Navigation (Mobile) -->
<nav class="mobile-nav glass-panel">
  {#each menuItems as item}
    <button 
      class="mobile-nav-btn {currentTab === item.id ? 'active' : ''}" 
      on:click={() => setTab(item.id)}
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="mobile-nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={item.icon} />
      </svg>
      <span class="mobile-nav-label">{item.label}</span>
    </button>
  {/each}
</nav>

<style>
  /* Estilos Desktop */
  .desktop-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 28px;
    margin: 20px auto;
    max-width: 1200px;
    width: calc(100% - 40px);
    z-index: 100;
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .logo-icon {
    width: 28px;
    height: 28px;
    color: var(--accent-purple);
    filter: drop-shadow(0 0 8px rgba(139, 92, 246, 0.5));
  }

  .logo-text {
    font-size: 1.25rem;
    font-weight: 800;
    letter-spacing: -0.5px;
  }

  .accent-text {
    background: linear-gradient(135deg, var(--accent-purple) 0%, var(--accent-blue) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .nav-links {
    display: flex;
    gap: 8px;
  }

  .nav-btn {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 0.95rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    transition: var(--transition-smooth);
  }

  .nav-icon {
    width: 18px;
    height: 18px;
  }

  .nav-btn:hover {
    color: var(--text-primary);
    background: rgba(255, 255, 255, 0.04);
  }

  .nav-btn.active {
    color: #fff;
    background: rgba(139, 92, 246, 0.15);
    border: 1px solid rgba(139, 92, 246, 0.25);
  }

  /* Estilos Mobile */
  .mobile-nav {
    display: none;
  }

  @media (max-width: 768px) {
    .desktop-nav {
      display: none;
    }

    .mobile-nav {
      display: flex;
      justify-content: space-around;
      align-items: center;
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      height: 70px;
      border-radius: 20px 20px 0 0;
      border-bottom: none;
      border-left: none;
      border-right: none;
      padding: 0 10px;
      z-index: 1000;
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
    }

    .mobile-nav-btn {
      background: transparent;
      border: none;
      color: var(--text-secondary);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 4px;
      flex: 1;
      height: 100%;
      cursor: pointer;
      transition: var(--transition-smooth);
    }

    .mobile-nav-icon {
      width: 20px;
      height: 20px;
    }

    .mobile-nav-label {
      font-size: 0.75rem;
      font-weight: 500;
    }

    .mobile-nav-btn.active {
      color: var(--accent-purple);
      transform: scale(1.08);
      filter: drop-shadow(0 0 6px rgba(139, 92, 246, 0.4));
    }
  }
</style>
