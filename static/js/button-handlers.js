/**
 * Sistema Clínica - Handlers centralizados para botões
 * Padronização de todas as funções de botões do sistema
 */

class ButtonHandlers {
    constructor() {
        this.init();
    }

    init() {
        this.setupGlobalEventListeners();
    }

    setupGlobalEventListeners() {
        // Event listener global para botões de confirmação
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-confirm]')) {
                e.preventDefault();
                this.handleConfirmAction(e.target);
            }
        });

        // Event listener para botões de loading
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-loading]')) {
                this.showLoadingState(e.target);
            }
        });
    }

    /**
     * Manipula ações que precisam de confirmação
     */
    handleConfirmAction(button) {
        const message = button.getAttribute('data-confirm');
        const action = button.getAttribute('data-action');
        const target = button.getAttribute('data-target');

        Swal.fire({
            title: 'Confirmar Ação',
            text: message,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Sim, Confirmar!',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                this.executeAction(action, target, button);
            }
        });
    }

    /**
     * Executa a ação confirmada
     */
    executeAction(action, target, button) {
        switch (action) {
            case 'delete':
                this.submitForm('POST', target);
                break;
            case 'redirect':
                window.location.href = target;
                break;
            case 'submit-form':
                document.querySelector(target).submit();
                break;
            default:
                console.warn('Ação não reconhecida:', action);
        }
    }

    /**
     * Submete um formulário via POST
     */
    submitForm(method, action) {
        const form = document.createElement('form');
        form.method = method;
        form.action = action;
        document.body.appendChild(form);
        form.submit();
    }

    /**
     * Mostra estado de loading no botão
     */
    showLoadingState(button) {
        const originalText = button.innerHTML;
        const loadingText = button.getAttribute('data-loading') || 'Carregando...';
        
        button.disabled = true;
        button.innerHTML = `<i class="bi bi-hourglass-split me-2"></i>${loadingText}`;
        
        // Restore após 3 segundos (ajustar conforme necessário)
        setTimeout(() => {
            button.disabled = false;
            button.innerHTML = originalText;
        }, 3000);
    }

    /**
     * Mostra toast de sucesso
     */
    showSuccessToast(message) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'success',
                title: 'Sucesso!',
                text: message,
                timer: 3000,
                showConfirmButton: false,
                toast: true,
                position: 'top-end'
            });
        } else if (typeof showToast !== 'undefined') {
            showToast(message, 'success');
        }
    }

    /**
     * Mostra toast de erro
     */
    showErrorToast(message) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'error',
                title: 'Erro!',
                text: message,
                timer: 5000,
                showConfirmButton: false,
                toast: true,
                position: 'top-end'
            });
        } else if (typeof showToast !== 'undefined') {
            showToast(message, 'error');
        }
    }

    /**
     * Valida formulário antes do envio
     */
    validateForm(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    }

    /**
     * Confirma exclusão com detalhes
     */
    confirmDelete(itemName, deleteUrl) {
        return Swal.fire({
            title: 'Confirmar Exclusão',
            text: `Deseja realmente excluir "${itemName}"?`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            cancelButtonColor: '#6c757d',
            confirmButtonText: 'Sim, Excluir!',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                this.submitForm('POST', deleteUrl);
                return true;
            }
            return false;
        });
    }

    /**
     * Redireciona para página de edição
     */
    editItem(editUrl) {
        window.location.href = editUrl;
    }

    /**
     * Exporta dados
     */
    exportData(format, url) {
        this.showSuccessToast(`Iniciando exportação ${format.toUpperCase()}...`);
        window.location.href = url;
    }

    /**
     * Aplica máscara de CPF
     */
    applyCPFMask(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            
            if (value.length <= 11) {
                value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
                value = value.replace(/(\d{3})(\d{3})(\d{3})/, '$1.$2.$3');
                value = value.replace(/(\d{3})(\d{3})/, '$1.$2');
                value = value.replace(/(\d{3})/, '$1');
            }
            
            e.target.value = value;
        });
    }

    /**
     * Aplica máscara de telefone
     */
    applyPhoneMask(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            
            if (value.length <= 11) {
                if (value.length <= 10) {
                    value = value.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
                } else {
                    value = value.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
                }
            }
            
            e.target.value = value;
        });
    }
}

// Funções globais para compatibilidade com códigos existentes
window.ButtonHandlers = ButtonHandlers;

// Instanciar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    window.buttonHandlers = new ButtonHandlers();
    
    // Aplicar máscaras automaticamente
    document.querySelectorAll('input[name="cpf"]').forEach(input => {
        window.buttonHandlers.applyCPFMask(input);
    });
    
    document.querySelectorAll('input[name="telefone"]').forEach(input => {
        window.buttonHandlers.applyPhoneMask(input);
    });
});

// Funções de conveniência globais
function confirmDelete(itemName, deleteUrl) {
    return window.buttonHandlers.confirmDelete(itemName, deleteUrl);
}

function editItem(editUrl) {
    window.buttonHandlers.editItem(editUrl);
}

function exportData(format, url) {
    window.buttonHandlers.exportData(format, url);
}

function showSuccessToast(message) {
    window.buttonHandlers.showSuccessToast(message);
}

function showErrorToast(message) {
    window.buttonHandlers.showErrorToast(message);
}
