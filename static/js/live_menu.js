/**
 * 🚀 MENU ORBITAL - Sistema de Navegação Circular 3D
 * Funcionalidades: Menu orbital, rotação 3D, partículas animadas, sons, touch/mouse
 */

class OrbitalMenu {
  constructor() {
    this.isOpen = false;
    this.isRotating = false;
    this.rotationAngle = 0;
    this.rotationSpeed = 0.5;
    this.touchStartX = 0;
    this.touchStartY = 0;
    this.mouseStartX = 0;
    this.mouseStartY = 0;
    this.audioContext = null;
    this.audioEnabled = true;
    
    // Elementos DOM
    this.menu = null;
    this.overlay = null;
    this.trigger = null;
    this.center = null;
    this.items = null;
    this.closeBtn = null;
    this.particles = null;
    
    // Configurações
    this.config = {
      rotationSpeed: 0.5,
      maxRotationSpeed: 2.0,
      minRotationSpeed: 0.1,
      touchSensitivity: 1.5,
      mouseSensitivity: 0.8,
      autoRotation: true,
      autoRotationSpeed: 0.1
    };
    
    this.init();
  }

  init() {
    console.log('🚀 Iniciando Menu Orbital...');
    
    this.initAudio();
    this.initElements();
    this.bindEvents();
    this.setupUserInfo();
    this.setActiveRoute();
    this.startAutoRotation();
    
    console.log('🚀 Menu Orbital inicializado com sucesso!');
    
    // Disparar evento para notificar que o menu está pronto
    window.dispatchEvent(new CustomEvent('orbitalMenuReady'));
  }

  initAudio() {
    try {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      if (this.audioContext.state === 'suspended') {
        this.audioEnabled = false;
      }
    } catch (error) {
      console.warn('Áudio não suportado:', error);
      this.audioEnabled = false;
    }
  }

  initElements() {
    console.log('🔍 Inicializando elementos do Menu Orbital...');
    
    this.menu = document.getElementById('orbitalMenu');
    this.overlay = document.getElementById('orbitalMenuOverlay');
    this.trigger = document.getElementById('orbitalMenuTrigger');
    this.center = document.getElementById('orbitalCenter');
    this.items = document.querySelectorAll('.orbital-item');
    this.closeBtn = document.getElementById('closeMenuBtn');
    this.particles = document.querySelectorAll('.particle');
    
    console.log('📋 Elementos encontrados:');
    console.log('- menu:', this.menu);
    console.log('- overlay:', this.overlay);
    console.log('- trigger:', this.trigger);
    console.log('- center:', this.center);
    console.log('- items:', this.items);
    console.log('- closeBtn:', this.closeBtn);
    console.log('- particles:', this.particles);
    
    // Debug: verificar se o botão foi encontrado
    if (this.trigger) {
      console.log('✅ Botão do Menu Orbital encontrado no cabeçalho');
      console.log('Posição:', this.trigger.getBoundingClientRect());
      console.log('Estilos:', window.getComputedStyle(this.trigger));
    } else {
      console.error('❌ Botão do Menu Orbital NÃO encontrado!');
    }
    
    if (!this.menu) {
      console.error('❌ Menu Orbital não encontrado!');
      return;
    }
    
    // Configurar índices para animações
    this.items.forEach((item, index) => {
      item.style.setProperty('--item-index', index);
    });
    
    console.log('✅ Elementos do Menu Orbital inicializados com sucesso!');
  }

  bindEvents() {
    // Botão de abertura
    if (this.trigger) {
      this.trigger.addEventListener('click', () => this.openMenu());
    }
    
    // Botão de fechamento
    if (this.closeBtn) {
      this.closeBtn.addEventListener('click', () => this.closeMenu());
    }
    
    // Overlay para fechar
    if (this.overlay) {
      this.overlay.addEventListener('click', () => this.closeMenu());
    }
    
    // Itens orbitais
    console.log(`🎯 Configurando ${this.items.length} itens orbitais`);
    this.items.forEach((item, index) => {
      const route = item.getAttribute('data-route');
      const url = item.getAttribute('data-url');
      console.log(`  ${index + 1}. ${route} -> ${url}`);
      
      item.addEventListener('click', (e) => this.handleItemClick(e, item));
      item.addEventListener('mouseenter', () => this.handleItemHover(item, true));
      item.addEventListener('mouseleave', () => this.handleItemHover(item, false));
    });
    
    // Controles de rotação
    this.bindRotationControls();
    
    // Teclas de atalho
    this.bindKeyboardShortcuts();
    
    // Integração com botão do header
    this.integrateWithHeader();
  }

  bindRotationControls() {
    // Touch events
    this.menu.addEventListener('touchstart', (e) => this.handleTouchStart(e));
    this.menu.addEventListener('touchmove', (e) => this.handleTouchMove(e));
    this.menu.addEventListener('touchend', () => this.handleTouchEnd());
    
    // Mouse events
    this.menu.addEventListener('mousedown', (e) => this.handleMouseDown(e));
    this.menu.addEventListener('mousemove', (e) => this.handleMouseMove(e));
    this.menu.addEventListener('mouseup', () => this.handleMouseUp());
    this.menu.addEventListener('mouseleave', () => this.handleMouseUp());
    
    // Wheel events
    this.menu.addEventListener('wheel', (e) => this.handleWheel(e));
  }

  bindKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // ESC: Fechar menu
      if (e.key === 'Escape' && this.isOpen) {
        this.closeMenu();
      }
      
      // Barra de espaço: Toggle rotação automática
      if (e.key === ' ' && this.isOpen) {
        e.preventDefault();
        this.toggleAutoRotation();
      }
      
      // R: Resetar rotação
      if (e.key === 'r' && this.isOpen) {
        e.preventDefault();
        this.resetRotation();
      }
    });
  }

  integrateWithHeader() {
    // Conectar com o botão do Menu Orbital no cabeçalho
    const headerMenuButton = document.getElementById('orbitalMenuTrigger');
    if (headerMenuButton) {
      console.log('✅ Botão do Menu Orbital encontrado no cabeçalho');
      headerMenuButton.addEventListener('click', () => {
        console.log('🎯 Botão do cabeçalho clicado - abrindo Menu Orbital');
        this.openMenu();
        this.playSound('open');
      });
    } else {
      console.error('❌ Botão do Menu Orbital não encontrado no cabeçalho');
    }
    
    // Atualizar estado do botão do header
    this.updateHeaderButtonState();
  }

  updateHeaderButtonState() {
    const headerMenuButton = document.getElementById('orbitalMenuTrigger');
    if (headerMenuButton) {
      if (this.isOpen) {
        headerMenuButton.classList.add('active');
        headerMenuButton.setAttribute('title', 'Fechar Menu Orbital');
      } else {
        headerMenuButton.classList.remove('active');
        headerMenuButton.setAttribute('title', 'Abrir Menu Orbital');
      }
    }
  }

  openMenu() {
    if (this.isOpen) return;
    
    this.isOpen = true;
    this.menu.classList.add('active');
    this.overlay.classList.add('active');
    
    // Animar entrada dos itens
    this.animateItemsEntrance();
    
    // Ativar partículas
    this.activateParticles();
    
    this.updateHeaderButtonState();
    this.playSound('open');
    
    // Focar no primeiro item para acessibilidade
    setTimeout(() => {
      this.items[0].focus();
    }, 600);
  }

  closeMenu() {
    if (!this.isOpen) return;
    
    this.isOpen = false;
    this.menu.classList.add('closing');
    
    // Animar saída dos itens
    this.animateItemsExit();
    
    // Desativar partículas
    this.deactivateParticles();
    
    setTimeout(() => {
      this.menu.classList.remove('active', 'closing');
      this.overlay.classList.remove('active');
    }, 600);
    
    this.updateHeaderButtonState();
    this.playSound('close');
  }

  animateItemsEntrance() {
    this.items.forEach((item, index) => {
      item.style.animationDelay = `${index * 0.1}s`;
      item.style.animation = 'itemEntrance 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards';
    });
  }

  animateItemsExit() {
    this.items.forEach((item, index) => {
      item.style.animationDelay = `${index * 0.05}s`;
      item.style.animation = 'itemExit 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards';
    });
  }

  activateParticles() {
    this.particles.forEach(particle => {
      particle.style.animationPlayState = 'running';
    });
  }

  deactivateParticles() {
    this.particles.forEach(particle => {
      particle.style.animationPlayState = 'paused';
    });
  }

  handleItemClick(e, item) {
    e.preventDefault();
    e.stopPropagation();
    
    // Efeito visual de clique
    this.animateItemClick(item);
    
    // Tocar som
    this.playSound('click');
    
    // Obter URL do item
    const url = item.getAttribute('data-url');
    const route = item.getAttribute('data-route');
    
    console.log(`🎯 Clique no item: ${route} -> ${url}`);
    
    if (route === 'logout') {
      this.handleLogout();
    } else if (url) {
      // Navegar para a página
      this.navigateToPage(url);
    } else {
      console.error(`❌ URL não encontrada para o item: ${route}`);
    }
  }

  animateItemClick(item) {
    // Adicionar classe de clique
    item.classList.add('clicking');
    
    // Efeito de salto
    item.style.transform = 'translate(-50%, -50%) scale(1.2) translateZ(40px)';
    
    setTimeout(() => {
      item.classList.remove('clicking');
      item.style.transform = '';
    }, 300);
  }

  handleItemHover(item, isHovering) {
    if (isHovering) {
      item.classList.add('hovering');
      this.playSound('hover');
    } else {
      item.classList.remove('hovering');
    }
  }

  handleTouchStart(e) {
    e.preventDefault();
    this.touchStartX = e.touches[0].clientX;
    this.touchStartY = e.touches[0].clientY;
    this.isRotating = true;
  }

  handleTouchMove(e) {
    if (!this.isRotating) return;
    
    e.preventDefault();
    
    const touchX = e.touches[0].clientX;
    const touchY = e.touches[0].clientY;
    
    const deltaX = touchX - this.touchStartX;
    const deltaY = touchY - this.touchStartY;
    
    // Calcular rotação baseada no movimento horizontal
    const rotationDelta = deltaX * this.config.touchSensitivity * 0.01;
    this.rotateOrbital(rotationDelta);
    
    this.touchStartX = touchX;
    this.touchStartY = touchY;
  }

  handleTouchEnd() {
    this.isRotating = false;
  }

  handleMouseDown(e) {
    e.preventDefault();
    this.mouseStartX = e.clientX;
    this.mouseStartY = e.clientY;
    this.isRotating = true;
    
    // Pausar rotação automática
    this.pauseAutoRotation();
  }

  handleMouseMove(e) {
    if (!this.isRotating) return;
    
    e.preventDefault();
    
    const mouseX = e.clientX;
    const mouseY = e.clientY;
    
    const deltaX = mouseX - this.mouseStartX;
    const deltaY = mouseY - this.mouseStartY;
    
    // Calcular rotação baseada no movimento horizontal
    const rotationDelta = deltaX * this.config.mouseSensitivity * 0.01;
    this.rotateOrbital(rotationDelta);
    
    this.mouseStartX = mouseX;
    this.mouseStartY = mouseY;
  }

  handleMouseUp() {
    this.isRotating = false;
    
    // Retomar rotação automática
    this.resumeAutoRotation();
  }

  handleWheel(e) {
    e.preventDefault();
    
    // Rotação baseada na roda do mouse
    const rotationDelta = e.deltaY * 0.01;
    this.rotateOrbital(rotationDelta);
    
    // Pausar rotação automática temporariamente
    this.pauseAutoRotation();
    setTimeout(() => this.resumeAutoRotation(), 2000);
  }

  rotateOrbital(delta) {
    this.rotationAngle += delta;
    
    // Aplicar rotação aos itens
    this.items.forEach((item, index) => {
      const angle = (index * (360 / this.items.length) + this.rotationAngle) * (Math.PI / 180);
      const radius = getComputedStyle(document.documentElement)
        .getPropertyValue('--orbital-radius')
        .replace('px', '');
      
      const x = Math.cos(angle) * radius;
      const y = Math.sin(angle) * radius;
      
      item.style.transform = `translate(${x}px, ${y}px)`;
    });
  }

  startAutoRotation() {
    if (!this.config.autoRotation) return;
    
    setInterval(() => {
      if (!this.isRotating && this.isOpen) {
        this.rotateOrbital(this.config.autoRotationSpeed);
      }
    }, 50);
  }

  pauseAutoRotation() {
    this.config.autoRotation = false;
  }

  resumeAutoRotation() {
    this.config.autoRotation = true;
  }

  toggleAutoRotation() {
    this.config.autoRotation = !this.config.autoRotation;
    
    if (this.config.autoRotation) {
      this.playSound('toggle');
    }
  }

  resetRotation() {
    this.rotationAngle = 0;
    this.rotateOrbital(0);
    this.playSound('reset');
  }

  setupUserInfo() {
    // Usar informações dinâmicas do usuário do template
    const userName = document.getElementById('userName');
    const userRole = document.getElementById('userRole');
    const statusIndicator = document.getElementById('statusIndicator');
    
    console.log('🔍 Debug setupUserInfo:');
    console.log('- userName element:', userName);
    console.log('- userRole element:', userRole);
    console.log('- statusIndicator element:', statusIndicator);
    
    if (userName) {
      console.log('- userName textContent:', userName.textContent);
      console.log('- userName innerHTML:', userName.innerHTML);
    }
    
    if (userRole) {
      console.log('- userRole textContent:', userRole.textContent);
      console.log('- userRole innerHTML:', userRole.innerHTML);
    }
    
    // Verificar se o usuário está logado baseado no conteúdo do nome
    const isLoggedIn = userName && userName.textContent.trim() !== 'Visitante';
    
    if (userName && userRole) {
      // As informações já estão sendo renderizadas pelo template Jinja2
      // Apenas atualizar o status visual
      if (statusIndicator) {
        if (isLoggedIn) {
          statusIndicator.style.background = '#10b981'; // Online (verde)
          statusIndicator.title = 'Usuário Online';
        } else {
          statusIndicator.style.background = '#6b7280'; // Offline (cinza)
          statusIndicator.title = 'Usuário Offline';
        }
      }
      
      console.log(`👤 Usuário: ${userName.textContent} | Role: ${userRole.textContent} | Status: ${isLoggedIn ? 'Online' : 'Offline'}`);
    }
  }

  setActiveRoute() {
    const currentPath = window.location.pathname;
    
    this.items.forEach(item => {
      const itemUrl = item.getAttribute('data-url');
      if (itemUrl === currentPath) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });
  }

  navigateToPage(url) {
    console.log(`🚀 Navegando para: ${url}`);
    
    // Fechar menu antes de navegar
    this.closeMenu();
    
    // Pequeno delay para permitir a animação de fechamento
    setTimeout(() => {
      try {
        // Verificar se a URL é válida
        if (url && url.startsWith('/')) {
          console.log(`✅ Redirecionando para: ${url}`);
          window.location.href = url;
        } else {
          console.error(`❌ URL inválida: ${url}`);
        }
      } catch (error) {
        console.error(`❌ Erro ao navegar:`, error);
        // Fallback: tentar navegar diretamente
        window.location.href = url;
      }
    }, 300);
  }

  handleLogout() {
    console.log(`🚪 Tentando fazer logout...`);
    
    if (confirm('Tem certeza que deseja sair do sistema?')) {
      this.playSound('logout');
      
      // Fechar menu
      this.closeMenu();
      
      setTimeout(() => {
        try {
          console.log(`✅ Redirecionando para logout`);
          window.location.href = '/logout';
        } catch (error) {
          console.error(`❌ Erro ao fazer logout:`, error);
          // Fallback
          window.location.href = '/logout';
        }
      }, 500);
    } else {
      console.log(`❌ Logout cancelado pelo usuário`);
    }
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
        case 'open':
          oscillator.frequency.setValueAtTime(800, this.audioContext.currentTime);
          break;
        case 'close':
          oscillator.frequency.setValueAtTime(600, this.audioContext.currentTime);
          break;
        case 'click':
          oscillator.frequency.setValueAtTime(1200, this.audioContext.currentTime);
          break;
        case 'hover':
          oscillator.frequency.setValueAtTime(1000, this.audioContext.currentTime);
          break;
        case 'toggle':
          oscillator.frequency.setValueAtTime(900, this.audioContext.currentTime);
          break;
        case 'reset':
          oscillator.frequency.setValueAtTime(700, this.audioContext.currentTime);
          break;
        case 'logout':
          oscillator.frequency.setValueAtTime(500, this.audioContext.currentTime);
          break;
        default:
          oscillator.frequency.setValueAtTime(800, this.audioContext.currentTime);
      }
      
      gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.1);
      
      oscillator.start(this.audioContext.currentTime);
      oscillator.stop(this.audioContext.currentTime + 0.1);
    } catch (error) {
      console.warn('Erro ao tocar som:', error);
    }
  }

  destroy() {
    // Limpar event listeners se necessário
    console.log('🗑️ Menu Orbital destruído');
  }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
  window.orbitalMenu = new OrbitalMenu();
});

// Exportar para uso global
window.OrbitalMenu = OrbitalMenu;
