/**
 * JavaScript Principal - Sistema Clínica
 * Versão Modernizada - Fase 1: Interface e PWA
 */

class ClinicaApp {
    constructor() {
        this.isOnline = navigator.onLine;
        this.serviceWorker = null;
        this.init();
    }
    
    async init() {
        console.log('🚀 Inicializando Sistema Clínica...');
        
        // Registra service worker
        await this.registerServiceWorker();
        
        // Configura listeners de eventos
        this.setupEventListeners();
        
        // Inicializa componentes
        this.initComponents();
        
        // Configura PWA
        this.setupPWA();
        
        console.log('✅ Sistema Clínica inicializado com sucesso!');
    }
    
    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                this.serviceWorker = await navigator.serviceWorker.register('/static/sw.js');
                console.log('📱 Service Worker registrado:', this.serviceWorker);
                
                // Listener para atualizações
                this.serviceWorker.addEventListener('updatefound', () => {
                    const newWorker = this.serviceWorker.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            this.showUpdateNotification();
                        }
                    });
                });
                
            } catch (error) {
                console.error('❌ Erro ao registrar Service Worker:', error);
            }
        }
    }
    
    setupEventListeners() {
        // Status online/offline
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.showNotification('Conexão restaurada', 'success');
            this.updateOnlineStatus();
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.showNotification('Modo offline ativado', 'warning');
            this.updateOnlineStatus();
        });
        
        // Scroll suave para links internos
        document.addEventListener('click', (e) => {
            if (e.target.matches('a[href^="#"]')) {
                e.preventDefault();
                const target = document.querySelector(e.target.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
        
        // Formulários com validação
        document.addEventListener('submit', (e) => {
            if (e.target.matches('form')) {
                this.handleFormSubmit(e);
            }
        });
        
        // Inputs com validação em tempo real
        document.addEventListener('input', (e) => {
            if (e.target.matches('.form-input, .form-textarea, .form-select')) {
                this.validateInput(e.target);
            }
        });
        
        // Tema escuro/claro
        this.setupThemeToggle();
    }
    
    initComponents() {
        // Inicializa tooltips
        this.initTooltips();
        
        // Inicializa modais
        this.initModals();
        
        // Inicializa dropdowns
        this.initDropdowns();
        
        // Inicializa tabs
        this.initTabs();
        
        // Inicializa accordions
        this.initAccordions();
        
        // Inicializa carrosséis
        this.initCarousels();
        
        // Inicializa notificações toast
        this.initToastNotifications();
    }
    
    setupPWA() {
        // Verifica se é possível instalar como PWA
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            this.showInstallPrompt();
        });
        
        // Listener para instalação
        window.addEventListener('appinstalled', () => {
            console.log('📱 PWA instalado com sucesso!');
            this.showNotification('Aplicativo instalado!', 'success');
        });
    }
    
    showInstallPrompt() {
        const installButton = document.getElementById('install-pwa');
        if (installButton) {
            installButton.style.display = 'block';
            installButton.addEventListener('click', async () => {
                if (deferredPrompt) {
                    deferredPrompt.prompt();
                    const { outcome } = await deferredPrompt.userChoice;
                    if (outcome === 'accepted') {
                        console.log('Usuário aceitou instalação');
                    }
                    deferredPrompt = null;
                    installButton.style.display = 'none';
                }
            });
        }
    }
    
    showUpdateNotification() {
        const notification = document.createElement('div');
        notification.className = 'update-notification';
        notification.innerHTML = `
            <div class="update-content">
                <span>🔄 Nova versão disponível!</span>
                <button class="btn btn-primary btn-sm" onclick="location.reload()">
                    Atualizar
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Remove após 10 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 10000);
    }
    
    updateOnlineStatus() {
        const statusIndicator = document.getElementById('online-status');
        if (statusIndicator) {
            statusIndicator.className = `status-indicator ${this.isOnline ? 'online' : 'offline'}`;
            statusIndicator.textContent = this.isOnline ? '🟢 Online' : '🔴 Offline';
        }
    }
    
    handleFormSubmit(event) {
        const form = event.target;
        const submitButton = form.querySelector('button[type="submit"]');
        
        // Validação do formulário
        if (!this.validateForm(form)) {
            event.preventDefault();
            return false;
        }
        
        // Mostra loading
        if (submitButton) {
            const originalText = submitButton.textContent;
            submitButton.textContent = 'Enviando...';
            submitButton.disabled = true;
            
            // Restaura após envio
            setTimeout(() => {
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            }, 3000);
        }
        
        return true;
    }
    
    validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('.form-input, .form-textarea, .form-select');
        
        inputs.forEach(input => {
            if (!this.validateInput(input)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    validateInput(input) {
        const value = input.value.trim();
        const type = input.type;
        const required = input.hasAttribute('required');
        const minLength = input.getAttribute('minlength');
        const maxLength = input.getAttribute('maxlength');
        const pattern = input.getAttribute('pattern');
        
        // Remove classes de erro anteriores
        input.classList.remove('error', 'success');
        
        // Validação de campo obrigatório
        if (required && !value) {
            this.showInputError(input, 'Este campo é obrigatório');
            return false;
        }
        
        // Validação de comprimento
        if (minLength && value.length < parseInt(minLength)) {
            this.showInputError(input, `Mínimo de ${minLength} caracteres`);
            return false;
        }
        
        if (maxLength && value.length > parseInt(maxLength)) {
            this.showInputError(input, `Máximo de ${maxLength} caracteres`);
            return false;
        }
        
        // Validação de email
        if (type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                this.showInputError(input, 'Email inválido');
                return false;
            }
        }
        
        // Validação de padrão
        if (pattern && value) {
            const regex = new RegExp(pattern);
            if (!regex.test(value)) {
                this.showInputError(input, 'Formato inválido');
                return false;
            }
        }
        
        // Se passou por todas as validações
        if (value) {
            input.classList.add('success');
        }
        
        return true;
    }
    
    showInputError(input, message) {
        input.classList.add('error');
        
        // Remove mensagem de erro anterior
        const existingError = input.parentNode.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
        
        // Adiciona nova mensagem de erro
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        input.parentNode.appendChild(errorDiv);
    }
    
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `toast-notification toast-${type} fade-in`;
        notification.innerHTML = `
            <div class="toast-content">
                <span class="toast-message">${message}</span>
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        // Adiciona ao container de notificações
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        
        container.appendChild(notification);
        
        // Remove automaticamente
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.remove('fade-in');
                notification.classList.add('fade-out');
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }
        }, duration);
    }
    
    // Componentes UI
    initTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', this.showTooltip.bind(this));
            element.addEventListener('mouseleave', this.hideTooltip.bind(this));
        });
    }
    
    showTooltip(event) {
        const element = event.target;
        const text = element.getAttribute('data-tooltip');
        
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = text;
        
        document.body.appendChild(tooltip);
        
        // Posiciona o tooltip
        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
        
        element.tooltip = tooltip;
    }
    
    hideTooltip(event) {
        const element = event.target;
        if (element.tooltip) {
            element.tooltip.remove();
            element.tooltip = null;
        }
    }
    
    initModals() {
        const modalTriggers = document.querySelectorAll('[data-modal]');
        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', this.openModal.bind(this));
        });
        
        // Fecha modal ao clicar fora
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-backdrop')) {
                this.closeModal(e.target);
            }
        });
        
        // Fecha modal com ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const openModal = document.querySelector('.modal.show');
                if (openModal) {
                    this.closeModal(openModal);
                }
            }
        });
    }
    
    openModal(event) {
        const modalId = event.target.getAttribute('data-modal');
        const modal = document.getElementById(modalId);
        
        if (modal) {
            modal.classList.add('show');
            document.body.classList.add('modal-open');
        }
    }
    
    closeModal(modal) {
        modal.classList.remove('show');
        document.body.classList.remove('modal-open');
    }
    
    initDropdowns() {
        const dropdowns = document.querySelectorAll('.dropdown');
        dropdowns.forEach(dropdown => {
            const toggle = dropdown.querySelector('.dropdown-toggle');
            const menu = dropdown.querySelector('.dropdown-menu');
            
            if (toggle && menu) {
                toggle.addEventListener('click', (e) => {
                    e.preventDefault();
                    dropdown.classList.toggle('open');
                });
            }
        });
        
        // Fecha dropdowns ao clicar fora
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown.open').forEach(dropdown => {
                    dropdown.classList.remove('open');
                });
            }
        });
    }
    
    initTabs() {
        const tabContainers = document.querySelectorAll('.tabs');
        tabContainers.forEach(container => {
            const tabs = container.querySelectorAll('.tab');
            const contents = container.querySelectorAll('.tab-content');
            
            tabs.forEach(tab => {
                tab.addEventListener('click', () => {
                    const target = tab.getAttribute('data-tab');
                    
                    // Remove classe ativa de todas as tabs
                    tabs.forEach(t => t.classList.remove('active'));
                    contents.forEach(c => c.classList.remove('active'));
                    
                    // Adiciona classe ativa na tab clicada
                    tab.classList.add('active');
                    const targetContent = container.querySelector(`[data-content="${target}"]`);
                    if (targetContent) {
                        targetContent.classList.add('active');
                    }
                });
            });
        });
    }
    
    initAccordions() {
        const accordions = document.querySelectorAll('.accordion');
        accordions.forEach(accordion => {
            const header = accordion.querySelector('.accordion-header');
            const content = accordion.querySelector('.accordion-content');
            
            if (header && content) {
                header.addEventListener('click', () => {
                    accordion.classList.toggle('open');
                });
            }
        });
    }
    
    initCarousels() {
        const carousels = document.querySelectorAll('.carousel');
        carousels.forEach(carousel => {
            const slides = carousel.querySelectorAll('.carousel-slide');
            const prevBtn = carousel.querySelector('.carousel-prev');
            const nextBtn = carousel.querySelector('.carousel-next');
            let currentSlide = 0;
            
            if (slides.length > 1) {
                // Mostra primeiro slide
                slides[currentSlide].classList.add('active');
                
                // Botão próximo
                if (nextBtn) {
                    nextBtn.addEventListener('click', () => {
                        slides[currentSlide].classList.remove('active');
                        currentSlide = (currentSlide + 1) % slides.length;
                        slides[currentSlide].classList.add('active');
                    });
                }
                
                // Botão anterior
                if (prevBtn) {
                    prevBtn.addEventListener('click', () => {
                        slides[currentSlide].classList.remove('active');
                        currentSlide = (currentSlide - 1 + slides.length) % slides.length;
                        slides[currentSlide].classList.add('active');
                    });
                }
            }
        });
    }
    
    initToastNotifications() {
        // Container já é criado dinamicamente
        console.log('🔔 Sistema de notificações inicializado');
    }
    
    setupThemeToggle() {
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            // Carrega tema salvo
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme) {
                document.documentElement.setAttribute('data-theme', savedTheme);
            }
            
            themeToggle.addEventListener('click', () => {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                
                this.showNotification(`Tema ${newTheme === 'dark' ? 'escuro' : 'claro'} ativado`, 'info');
            });
        }
    }
    
    // Utilitários
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
    
    // API helpers
    async apiCall(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Erro na API:', error);
            this.showNotification('Erro na comunicação com o servidor', 'error');
            throw error;
        }
    }
}

// Inicializa a aplicação quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.clinicaApp = new ClinicaApp();
});

// Exporta para uso em outros módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ClinicaApp;
}
