/**
 * Sidebar Menu JavaScript - Menu Lateral Inovador e Interativo
 * Funcionalidades: Toggle, Busca Global, Mini Dashboard, Notificações, Partículas
 */

class SidebarMenu {
  constructor() {
    this.isCollapsed = false;
    this.isMobile = window.innerWidth <= 768;
    this.isVisible = true;
    this.searchTimeout = null;
    this.particles = [];
    this.audioContext = null;
    this.audioEnabled = true;
    
    // Elementos DOM
    this.sidebar = null;
    this.overlay = null;
    this.fab = null;
    this.toggle = null;
    this.searchInput = null;
    this.searchClear = null;
    this.themeToggle = null;
    this.miniDashboard = null;
    
    // Dados do dashboard
    this.dashboardData = {
      nextAppointments: 0,
      dailyRevenue: 0
    };
    
    this.init();
  }

  init() {
    this.initAudio();
    this.initElements();
    this.bindEvents();
    this.initParticles();
    this.loadDashboardData();
    this.setActiveRoute();
    this.updateStatusIndicator();
    this.loadNotifications();
    
    // Verificar preferência salva
    this.loadPreferences();
    
    // Emitir evento de inicialização
    window.dispatchEvent(new CustomEvent('sidebarReady'));
    
    console.log('🚀 Sidebar Menu inicializado com sucesso!');
  }

  initAudio() {
    try {
      // Criar contexto de áudio para efeitos sonoros
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      
      // Verificar se o usuário já interagiu com a página
      if (this.audioContext.state === 'suspended') {
        this.audioEnabled = false;
      }
    } catch (error) {
      console.warn('Áudio não suportado:', error);
      this.audioEnabled = false;
    }
  }

  initElements() {
    this.sidebar = document.getElementById('sidebar');
    this.overlay = document.getElementById('sidebarOverlay');
    this.fab = document.getElementById('sidebarFab');
    this.toggle = document.getElementById('sidebarToggle');
    this.searchInput = document.getElementById('globalSearch');
    this.searchClear = document.getElementById('searchClear');
    this.themeToggle = document.getElementById('sidebarThemeToggle');
    this.miniDashboard = document.getElementById('miniDashboard');
    
    if (!this.sidebar) {
      console.error('❌ Sidebar não encontrado!');
      return;
    }
    
    // Configurar estado inicial
    if (this.isMobile) {
      this.sidebar.classList.add('mobile');
      this.hideSidebar();
    }
  }

  bindEvents() {
    // Toggle do sidebar
    if (this.toggle) {
      this.toggle.addEventListener('click', () => this.toggleSidebar());
    }
    
    // Floating Action Button
    if (this.fab) {
      this.fab.addEventListener('click', () => this.showSidebar());
    }
    
    // Overlay para mobile
    if (this.overlay) {
      this.overlay.addEventListener('click', () => this.hideSidebar());
    }
    
    // Busca global
    if (this.searchInput) {
      this.searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
      this.searchInput.addEventListener('focus', () => this.playSound('focus'));
      this.searchInput.addEventListener('keydown', (e) => this.handleSearchKeydown(e));
    }
    
    // Botão limpar busca
    if (this.searchClear) {
      this.searchClear.addEventListener('click', () => this.clearSearch());
    }
    
    // Toggle de tema
    if (this.themeToggle) {
      this.themeToggle.addEventListener('click', () => this.toggleTheme());
    }
    
    // Navegação
    this.bindNavigationEvents();
    
    // Teclas de atalho
    this.bindKeyboardShortcuts();
    
    // Resize da janela
    window.addEventListener('resize', () => this.handleResize());
    
    // Clique fora para fechar (mobile)
    document.addEventListener('click', (e) => this.handleOutsideClick(e));
  }

  bindNavigationEvents() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        this.playSound('click');
        this.addClickEffect(e.currentTarget);
        
        // Marcar como ativo
        navLinks.forEach(l => l.classList.remove('active'));
        link.classList.add('active');
        
        // Em mobile, fechar o sidebar após navegação
        if (this.isMobile) {
          setTimeout(() => this.hideSidebar(), 300);
        }
      });
      
      // Efeito de hover com áudio
      link.addEventListener('mouseenter', () => {
        this.playSound('hover');
        this.addHoverEffect(link);
      });
    });
  }

  bindKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Ctrl/Cmd + K para abrir busca
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        this.focusSearch();
      }
      
      // Escape para fechar sidebar (mobile)
      if (e.key === 'Escape' && this.isMobile && this.isVisible) {
        this.hideSidebar();
      }
      
      // Ctrl/Cmd + B para toggle do sidebar
      if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault();
        this.toggleSidebar();
      }
    });
  }

  toggleSidebar() {
    if (this.isCollapsed) {
      this.expandSidebar();
    } else {
      this.collapseSidebar();
    }
    
    this.playSound('toggle');
    this.savePreferences();
  }

  collapseSidebar() {
    this.sidebar.classList.add('collapsed');
    this.isCollapsed = true;
    
    // Animar elementos
    this.animateCollapse();
  }

  expandSidebar() {
    this.sidebar.classList.remove('collapsed');
    this.isCollapsed = false;
    
    // Animar elementos
    this.animateExpand();
  }

  showSidebar() {
    if (this.isMobile) {
      this.sidebar.classList.add('active');
      this.overlay.classList.add('active');
      this.isVisible = true;
      this.playSound('open');
      
      // Focar no primeiro elemento interativo
      setTimeout(() => {
        const firstLink = this.sidebar.querySelector('.nav-link');
        if (firstLink) firstLink.focus();
      }, 300);
    }
  }

  hideSidebar() {
    if (this.isMobile) {
      this.sidebar.classList.remove('active');
      this.overlay.classList.remove('active');
      this.isVisible = false;
      this.playSound('close');
    }
  }

  animateCollapse() {
    const elements = this.sidebar.querySelectorAll('.nav-text, .user-info, .logout-text');
    
    elements.forEach((el, index) => {
      setTimeout(() => {
        el.style.opacity = '0';
        el.style.transform = 'translateX(-20px)';
      }, index * 50);
    });
  }

  animateExpand() {
    const elements = this.sidebar.querySelectorAll('.nav-text, .user-info, .logout-text');
    
    elements.forEach((el, index) => {
      setTimeout(() => {
        el.style.opacity = '1';
        el.style.transform = 'translateX(0)';
      }, index * 50);
    });
  }

  handleSearch(query) {
    clearTimeout(this.searchTimeout);
    
    this.searchTimeout = setTimeout(() => {
      if (query.length >= 2) {
        this.performSearch(query);
      } else if (query.length === 0) {
        this.clearSearchResults();
      }
    }, 300);
  }

  async performSearch(query) {
    try {
      this.showSearchLoading();
      
      // Simular busca (substituir por API real)
      const results = await this.searchAPI(query);
      this.displaySearchResults(results);
      
      this.playSound('search');
    } catch (error) {
      console.error('Erro na busca:', error);
      this.showSearchError();
    } finally {
      this.hideSearchLoading();
    }
  }

  async searchAPI(query) {
    // Simular API de busca
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const mockResults = [
      { type: 'patient', name: 'João Silva', url: '/pacientes/1' },
      { type: 'professional', name: 'Dr. Maria Santos', url: '/profissionais/1' },
      { type: 'service', name: 'Consulta Médica', url: '/servicos/1' }
    ].filter(item => 
      item.name.toLowerCase().includes(query.toLowerCase())
    );
    
    return mockResults;
  }

  displaySearchResults(results) {
    // Implementar exibição dos resultados
    console.log('Resultados da busca:', results);
  }

  clearSearch() {
    if (this.searchInput) {
      this.searchInput.value = '';
      this.searchInput.focus();
      this.clearSearchResults();
      this.playSound('clear');
    }
  }

  clearSearchResults() {
    // Limpar resultados da busca
  }

  showSearchLoading() {
    this.sidebar.classList.add('loading');
  }

  hideSearchLoading() {
    this.sidebar.classList.remove('loading');
  }

  showSearchError() {
    // Mostrar erro na busca
  }

  focusSearch() {
    if (this.searchInput) {
      this.searchInput.focus();
      this.searchInput.select();
    }
  }

  handleSearchKeydown(e) {
    if (e.key === 'Enter') {
      this.performSearch(e.target.value);
    }
  }

  toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    html.setAttribute('data-bs-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    this.updateThemeIcon(newTheme);
    this.playSound('theme');
    
    // Atualizar partículas para o novo tema
    this.updateParticlesTheme();
  }

  updateThemeIcon(theme) {
    const icon = document.getElementById('sidebarThemeIcon');
    if (icon) {
      icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
    }
  }

  async loadDashboardData() {
    try {
      // Simular carregamento de dados do dashboard
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      this.dashboardData = {
        nextAppointments: Math.floor(Math.random() * 10) + 1,
        dailyRevenue: (Math.random() * 1000 + 100).toFixed(2)
      };
      
      this.updateDashboardDisplay();
    } catch (error) {
      console.error('Erro ao carregar dados do dashboard:', error);
    }
  }

  updateDashboardDisplay() {
    const nextAppointmentsEl = document.getElementById('nextAppointments');
    const dailyRevenueEl = document.getElementById('dailyRevenue');
    
    if (nextAppointmentsEl) {
      nextAppointmentsEl.textContent = this.dashboardData.nextAppointments;
    }
    
    if (dailyRevenueEl) {
      dailyRevenueEl.textContent = `R$ ${this.dashboardData.dailyRevenue}`;
    }
  }

  setActiveRoute() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
      const href = link.getAttribute('href');
      if (href && currentPath.startsWith(href)) {
        link.classList.add('active');
      }
    });
  }

  updateStatusIndicator() {
    const indicator = document.getElementById('statusIndicator');
    if (indicator) {
      // Simular status online/offline
      const isOnline = navigator.onLine;
      indicator.style.background = isOnline ? 'var(--success-color)' : 'var(--danger-color)';
      indicator.title = isOnline ? 'Online' : 'Offline';
    }
  }

  async loadNotifications() {
    try {
      // Simular carregamento de notificações
      const notifications = {
        dashboard: 0,
        patients: Math.floor(Math.random() * 5),
        professionals: Math.floor(Math.random() * 3),
        appointments: Math.floor(Math.random() * 8),
        services: Math.floor(Math.random() * 2),
        reports: Math.floor(Math.random() * 4),
        notifications: Math.floor(Math.random() * 10)
      };
      
      this.updateNotificationBadges(notifications);
    } catch (error) {
      console.error('Erro ao carregar notificações:', error);
    }
  }

  updateNotificationBadges(notifications) {
    Object.entries(notifications).forEach(([route, count]) => {
      const badge = document.getElementById(`${route}Badge`);
      if (badge) {
        if (count > 0) {
          badge.textContent = count;
          badge.style.display = 'flex';
          
          // Animar badge
          badge.style.animation = 'none';
          setTimeout(() => {
            badge.style.animation = 'badgePulse 2s infinite';
          }, 10);
        } else {
          badge.style.display = 'none';
        }
      }
    });
  }

  initParticles() {
    const container = document.getElementById('particlesContainer');
    if (!container) return;
    
    // Criar partículas animadas
    for (let i = 0; i < 20; i++) {
      this.createParticle(container);
    }
    
    // Animar partículas
    this.animateParticles();
  }

  createParticle(container) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    
    // Posição aleatória
    particle.style.left = Math.random() * 100 + '%';
    particle.style.top = Math.random() * 100 + '%';
    particle.style.animationDelay = Math.random() * 6 + 's';
    particle.style.animationDuration = (Math.random() * 3 + 3) + 's';
    
    container.appendChild(particle);
    this.particles.push(particle);
  }

  animateParticles() {
    this.particles.forEach((particle, index) => {
      setInterval(() => {
        if (particle.parentNode) {
          particle.style.left = Math.random() * 100 + '%';
          particle.style.top = Math.random() * 100 + '%';
        }
      }, (index + 1) * 2000);
    });
  }

  updateParticlesTheme() {
    const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    const color = isDark ? '#6366f1' : '#4f46e5';
    
    this.particles.forEach(particle => {
      particle.style.background = color;
    });
  }

  playSound(type) {
    if (!this.audioEnabled || !this.audioContext) return;
    
    try {
      const oscillator = this.audioContext.createOscillator();
      const gainNode = this.audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(this.audioContext.destination);
      
      // Configurar som baseado no tipo
      switch (type) {
        case 'click':
          oscillator.frequency.setValueAtTime(800, this.audioContext.currentTime);
          oscillator.frequency.exponentialRampToValueAtTime(600, this.audioContext.currentTime + 0.1);
          break;
        case 'hover':
          oscillator.frequency.setValueAtTime(600, this.audioContext.currentTime);
          oscillator.frequency.exponentialRampToValueAtTime(800, this.audioContext.currentTime + 0.05);
          break;
        case 'toggle':
          oscillator.frequency.setValueAtTime(400, this.audioContext.currentTime);
          oscillator.frequency.exponentialRampToValueAtTime(600, this.audioContext.currentTime + 0.2);
          break;
        case 'search':
          oscillator.frequency.setValueAtTime(1000, this.audioContext.currentTime);
          oscillator.frequency.exponentialRampToValueAtTime(800, this.audioContext.currentTime + 0.1);
          break;
        case 'theme':
          oscillator.frequency.setValueAtTime(500, this.audioContext.currentTime);
          oscillator.frequency.exponentialRampToValueAtTime(700, this.audioContext.currentTime + 0.15);
          break;
        default:
          oscillator.frequency.setValueAtTime(600, this.audioContext.currentTime);
      }
      
      gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.1);
      
      oscillator.start(this.audioContext.currentTime);
      oscillator.stop(this.audioContext.currentTime + 0.1);
      
    } catch (error) {
      console.warn('Erro ao tocar som:', error);
    }
  }

  addClickEffect(element) {
    element.style.transform = 'scale(0.95)';
    element.style.transition = 'transform 0.1s ease';
    
    setTimeout(() => {
      element.style.transform = '';
      element.style.transition = '';
    }, 100);
  }

  addHoverEffect(element) {
    element.style.transform = 'translateX(4px) scale(1.02)';
    element.style.transition = 'transform 0.2s ease';
    
    setTimeout(() => {
      element.style.transform = '';
      element.style.transition = '';
    }, 200);
  }

  handleResize() {
    const wasMobile = this.isMobile;
    this.isMobile = window.innerWidth <= 768;
    
    if (wasMobile !== this.isMobile) {
      if (this.isMobile) {
        this.sidebar.classList.add('mobile');
        this.hideSidebar();
      } else {
        this.sidebar.classList.remove('mobile');
        this.showSidebar();
      }
    }
  }

  handleOutsideClick(e) {
    if (this.isMobile && this.isVisible) {
      const isClickInside = this.sidebar.contains(e.target);
      const isClickOnFab = this.fab && this.fab.contains(e.target);
      
      if (!isClickInside && !isClickOnFab) {
        this.hideSidebar();
      }
    }
  }

  savePreferences() {
    const preferences = {
      collapsed: this.isCollapsed,
      theme: document.documentElement.getAttribute('data-bs-theme')
    };
    
    localStorage.setItem('sidebarPreferences', JSON.stringify(preferences));
  }

  loadPreferences() {
    try {
      const saved = localStorage.getItem('sidebarPreferences');
      if (saved) {
        const preferences = JSON.parse(saved);
        
        if (preferences.collapsed && !this.isMobile) {
          this.collapseSidebar();
        }
        
        if (preferences.theme) {
          document.documentElement.setAttribute('data-bs-theme', preferences.theme);
          this.updateThemeIcon(preferences.theme);
        }
      }
    } catch (error) {
      console.warn('Erro ao carregar preferências:', error);
    }
  }

  // Métodos públicos para uso externo
  show() {
    this.showSidebar();
  }

  hide() {
    this.hideSidebar();
  }

  collapse() {
    this.collapseSidebar();
  }

  expand() {
    this.expandSidebar();
  }

  search(query) {
    if (this.searchInput) {
      this.searchInput.value = query;
      this.handleSearch(query);
    }
  }

  updateNotifications(notifications) {
    this.updateNotificationBadges(notifications);
  }

  destroy() {
    // Limpar event listeners e timers
    this.particles.forEach(particle => {
      if (particle.parentNode) {
        particle.parentNode.removeChild(particle);
      }
    });
    
    this.particles = [];
    
    if (this.audioContext) {
      this.audioContext.close();
    }
  }
}

// Inicialização global
let sidebarMenu = null;

document.addEventListener('DOMContentLoaded', function() {
  // Aguardar um pouco para garantir que o DOM esteja pronto
  setTimeout(() => {
    sidebarMenu = new SidebarMenu();
    window.sidebarMenu = sidebarMenu;
    
    // Expor métodos globais para compatibilidade
    window.showSidebar = () => sidebarMenu?.show();
    window.hideSidebar = () => sidebarMenu?.hide();
    window.toggleSidebar = () => sidebarMenu?.toggleSidebar();
    
    console.log('🎯 Sidebar Menu disponível globalmente');
  }, 500);
});

// Funções globais para uso em outros módulos
function showSidebar() {
  if (sidebarMenu) {
    sidebarMenu.show();
  }
}

function hideSidebar() {
  if (sidebarMenu) {
    sidebarMenu.hide();
  }
}

function toggleSidebar() {
  if (sidebarMenu) {
    sidebarMenu.toggleSidebar();
  }
}

// Exportar para uso em outros módulos
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SidebarMenu;
}
