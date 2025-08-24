/**
 * MODERN UI - FASE 2
 * Sistema de busca, filtros e melhorias de UX
 */

class ModernUI {
    constructor() {
        this.init();
    }

    init() {
        this.initSearchAndFilters();
        this.initResponsiveTables();
        this.initSmoothAnimations();
        this.initLoadingStates();
        this.initTooltips();
        this.initFormEnhancements();
    }

    /**
     * Sistema de Busca e Filtros
     */
    initSearchAndFilters() {
        // Busca em tempo real
        const searchInputs = document.querySelectorAll('.search-box input');
        searchInputs.forEach(input => {
            input.addEventListener('input', (e) => {
                this.performSearch(e.target.value, e.target.dataset.target);
            });
        });

        // Filtros por tags
        const filterTags = document.querySelectorAll('.filter-tag');
        filterTags.forEach(tag => {
            tag.addEventListener('click', (e) => {
                this.toggleFilter(e.target);
            });
        });

        // Filtros avançados
        const advancedFilters = document.querySelectorAll('.advanced-filter');
        advancedFilters.forEach(filter => {
            filter.addEventListener('change', (e) => {
                this.applyAdvancedFilters();
            });
        });
    }

    /**
     * Executa busca em tempo real
     */
    performSearch(query, targetSelector) {
        const targetTable = document.querySelector(targetSelector || '.table');
        if (!targetTable) return;

        const rows = targetTable.querySelectorAll('tbody tr');
        const searchTerm = query.toLowerCase().trim();

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const isVisible = text.includes(searchTerm);
            
            row.style.display = isVisible ? '' : 'none';
            
            if (isVisible) {
                row.classList.add('animate-fade-in-up');
            }
        });

        // Atualizar contador de resultados
        this.updateResultCount(rows, searchTerm);
    }

    /**
     * Atualiza contador de resultados
     */
    updateResultCount(rows, searchTerm) {
        const visibleRows = Array.from(rows).filter(row => 
            row.style.display !== 'none'
        );
        
        const counter = document.querySelector('.result-counter');
        if (counter) {
            const total = rows.length;
            const visible = visibleRows.length;
            
            if (searchTerm) {
                counter.textContent = `${visible} de ${total} resultados`;
                counter.classList.add('text-primary');
            } else {
                counter.textContent = `${total} resultados`;
                counter.classList.remove('text-primary');
            }
        }
    }

    /**
     * Alterna filtros por tags
     */
    toggleFilter(tag) {
        tag.classList.toggle('active');
        this.applyFilters();
    }

    /**
     * Aplica todos os filtros ativos
     */
    applyFilters() {
        const activeFilters = document.querySelectorAll('.filter-tag.active');
        const filterValues = Array.from(activeFilters).map(tag => tag.dataset.value);
        
        const rows = document.querySelectorAll('.table tbody tr');
        
        rows.forEach(row => {
            const shouldShow = this.rowMatchesFilters(row, filterValues);
            row.style.display = shouldShow ? '' : 'none';
        });
    }

    /**
     * Verifica se uma linha corresponde aos filtros
     */
    rowMatchesFilters(row, filters) {
        if (filters.length === 0) return true;
        
        return filters.some(filter => {
            const cell = row.querySelector(`[data-${filter}]`);
            return cell && cell.dataset[filter] === filter;
        });
    }

    /**
     * Aplica filtros avançados
     */
    applyAdvancedFilters() {
        const filters = {};
        
        document.querySelectorAll('.advanced-filter').forEach(filter => {
            if (filter.value) {
                filters[filter.name] = filter.value;
            }
        });

        this.filterTableByAdvanced(filters);
    }

    /**
     * Filtra tabela por filtros avançados
     */
    filterTableByAdvanced(filters) {
        const rows = document.querySelectorAll('.table tbody tr');
        
        rows.forEach(row => {
            const matches = Object.entries(filters).every(([key, value]) => {
                const cell = row.querySelector(`[data-${key}]`);
                return cell && cell.dataset[key].toLowerCase().includes(value.toLowerCase());
            });
            
            row.style.display = matches ? '' : 'none';
        });
    }

    /**
     * Tabelas responsivas
     */
    initResponsiveTables() {
        const tables = document.querySelectorAll('.modern-table');
        
        tables.forEach(table => {
            this.makeTableResponsive(table);
        });
    }

    /**
     * Torna tabela responsiva
     */
    makeTableResponsive(table) {
        const wrapper = document.createElement('div');
        wrapper.className = 'table-responsive';
        wrapper.style.overflowX = 'auto';
        
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
        
        // Adicionar indicador de scroll horizontal
        this.addScrollIndicator(wrapper);
    }

    /**
     * Adiciona indicador de scroll horizontal
     */
    addScrollIndicator(wrapper) {
        const indicator = document.createElement('div');
        indicator.className = 'scroll-indicator';
        indicator.innerHTML = '<i class="bi bi-arrow-left-right"></i> Arraste para ver mais colunas';
        indicator.style.cssText = `
            text-align: center;
            padding: 0.5rem;
            color: var(--gray-500);
            font-size: 0.875rem;
            background: var(--gray-100);
            border-top: 1px solid var(--gray-200);
            display: none;
        `;
        
        wrapper.appendChild(indicator);
        
        // Mostrar/ocultar indicador baseado no scroll
        wrapper.addEventListener('scroll', () => {
            const hasOverflow = wrapper.scrollWidth > wrapper.clientWidth;
            indicator.style.display = hasOverflow ? 'block' : 'none';
        });
    }

    /**
     * Animações suaves
     */
    initSmoothAnimations() {
        // Intersection Observer para animações
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in-up');
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        // Observar elementos para animação
        document.querySelectorAll('.modern-card, .search-filter-container, .modern-table').forEach(el => {
            observer.observe(el);
        });
    }

    /**
     * Estados de carregamento
     */
    initLoadingStates() {
        // Skeleton loading para tabelas
        this.initSkeletonLoading();
        
        // Loading states para botões
        this.initButtonLoading();
    }

    /**
     * Inicializa skeleton loading
     */
    initSkeletonLoading() {
        const skeletonRows = document.querySelectorAll('.loading-skeleton');
        
        skeletonRows.forEach(row => {
            // Simular carregamento
            setTimeout(() => {
                row.classList.remove('loading-skeleton');
                row.classList.add('animate-fade-in-up');
            }, Math.random() * 1000 + 500);
        });
    }

    /**
     * Inicializa loading states para botões
     */
    initButtonLoading() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('.btn-modern[data-loading]')) {
                this.setButtonLoading(e.target, true);
                
                // Simular operação
                setTimeout(() => {
                    this.setButtonLoading(e.target, false);
                }, 2000);
            }
        });
    }

    /**
     * Define estado de loading para botão
     */
    setButtonLoading(button, isLoading) {
        if (isLoading) {
            button.disabled = true;
            button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Carregando...';
        } else {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText || 'Confirmar';
        }
    }

    /**
     * Tooltips modernos
     */
    initTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                this.showTooltip(e.target);
            });
            
            element.addEventListener('mouseleave', (e) => {
                this.hideTooltip(e.target);
            });
        });
    }

    /**
     * Mostra tooltip
     */
    showTooltip(element) {
        const tooltip = document.createElement('div');
        tooltip.className = 'modern-tooltip-popup';
        tooltip.textContent = element.dataset.tooltip;
        tooltip.style.cssText = `
            position: absolute;
            background: var(--gray-800);
            color: white;
            padding: 0.5rem 0.75rem;
            border-radius: var(--radius);
            font-size: 0.875rem;
            z-index: 1000;
            pointer-events: none;
            opacity: 0;
            transition: opacity var(--transition-fast);
        `;
        
        document.body.appendChild(tooltip);
        
        // Posicionar tooltip
        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
        
        // Animar entrada
        setTimeout(() => tooltip.style.opacity = '1', 10);
        
        // Armazenar referência
        element._tooltip = tooltip;
    }

    /**
     * Esconde tooltip
     */
    hideTooltip(element) {
        if (element._tooltip) {
            element._tooltip.style.opacity = '0';
            setTimeout(() => {
                if (element._tooltip && element._tooltip.parentNode) {
                    element._tooltip.parentNode.removeChild(element._tooltip);
                }
                element._tooltip = null;
            }, 150);
        }
    }

    /**
     * Melhorias em formulários
     */
    initFormEnhancements() {
        // Validação em tempo real
        this.initRealTimeValidation();
        
        // Auto-save para formulários longos
        this.initAutoSave();
        
        // Melhorias de acessibilidade
        this.initAccessibility();
    }

    /**
     * Validação em tempo real
     */
    initRealTimeValidation() {
        const formInputs = document.querySelectorAll('.modern-form input, .modern-form select, .modern-form textarea');
        
        formInputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateField(input);
            });
            
            input.addEventListener('input', () => {
                if (input.classList.contains('is-invalid')) {
                    this.validateField(input);
                }
            });
        });
    }

    /**
     * Valida campo individual
     */
    validateField(field) {
        const isValid = field.checkValidity();
        
        if (isValid) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
        }
    }

    /**
     * Auto-save para formulários
     */
    initAutoSave() {
        const forms = document.querySelectorAll('.modern-form form[data-autosave]');
        
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            const formKey = form.dataset.autosave || 'form_data';
            
            // Restaurar dados salvos
            this.restoreFormData(form, formKey);
            
            // Salvar dados automaticamente
            inputs.forEach(input => {
                input.addEventListener('input', () => {
                    this.saveFormData(form, formKey);
                });
            });
        });
    }

    /**
     * Salva dados do formulário
     */
    saveFormData(form, key) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [name, value] of formData.entries()) {
            data[name] = value;
        }
        
        localStorage.setItem(key, JSON.stringify(data));
    }

    /**
     * Restaura dados do formulário
     */
    restoreFormData(form, key) {
        const saved = localStorage.getItem(key);
        if (saved) {
            const data = JSON.parse(saved);
            
            Object.entries(data).forEach(([name, value]) => {
                const field = form.querySelector(`[name="${name}"]`);
                if (field) {
                    field.value = value;
                }
            });
        }
    }

    /**
     * Melhorias de acessibilidade
     */
    initAccessibility() {
        // Navegação por teclado
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });
        
        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });
        
        // Foco visível para navegação por teclado
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });
    }
}

/**
 * Utilitários para busca e filtros
 */
class SearchUtils {
    /**
     * Debounce para busca em tempo real
     */
    static debounce(func, wait) {
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

    /**
     * Highlight de texto encontrado
     */
    static highlightText(text, searchTerm) {
        if (!searchTerm) return text;
        
        const regex = new RegExp(`(${searchTerm})`, 'gi');
        return text.replace(regex, '<mark class="highlight">$1</mark>');
    }

    /**
     * Filtro fuzzy para busca mais flexível
     */
    static fuzzySearch(text, query) {
        const textLower = text.toLowerCase();
        const queryLower = query.toLowerCase();
        
        let queryIndex = 0;
        for (let i = 0; i < textLower.length && queryIndex < queryLower.length; i++) {
            if (textLower[i] === queryLower[queryIndex]) {
                queryIndex++;
            }
        }
        
        return queryIndex === queryLower.length;
    }
}

/**
 * Inicializar quando DOM estiver pronto
 */
document.addEventListener('DOMContentLoaded', () => {
    window.modernUI = new ModernUI();
    
    // Expor utilitários globalmente
    window.SearchUtils = SearchUtils;
});

/**
 * Exportar para uso em módulos
 */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ModernUI, SearchUtils };
}
