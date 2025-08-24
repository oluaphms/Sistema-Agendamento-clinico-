// ===== FUNCIONALIDADES PRINCIPAIS DO SISTEMA =====

// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    initializeSystem();
    setupEventListeners();
    loadDashboardData();
});

// ===== INICIALIZAÇÃO DO SISTEMA =====
function initializeSystem() {
    console.log('Sistema de Gestão Clínica inicializado');
    
    // Verificar se o usuário está logado
    checkAuthStatus();
    
    // Configurar tooltips do Bootstrap
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Configurar notificações toast
    setupToastNotifications();
}

// ===== CONFIGURAÇÃO DE EVENTOS =====
function setupEventListeners() {
    // Logout
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    
    // Pesquisa global
    const searchInput = document.getElementById('global-search');
    if (searchInput) {
        searchInput.addEventListener('input', handleGlobalSearch);
    }
    
    // Filtros de data
    const dateFilters = document.querySelectorAll('.date-filter');
    dateFilters.forEach(filter => {
        filter.addEventListener('change', handleDateFilter);
    });
    
    // Botões de ação
    setupActionButtons();
}

// ===== VERIFICAÇÃO DE AUTENTICAÇÃO =====
function checkAuthStatus() {
    // Verificar se há token de sessão
    const token = localStorage.getItem('auth_token');
    if (!token) {
        // Redirecionar para login se não estiver autenticado
        if (window.location.pathname !== '/login') {
            window.location.href = '/login';
        }
    }
}

// ===== MANIPULAÇÃO DE LOGOUT =====
function handleLogout() {
    if (confirm('Tem certeza que deseja sair?')) {
        // Limpar dados de sessão
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
        
        // Redirecionar para login
        window.location.href = '/login';
    }
}

// ===== PESQUISA GLOBAL =====
function handleGlobalSearch(event) {
    const searchTerm = event.target.value.toLowerCase();
    const searchableElements = document.querySelectorAll('.searchable');
    
    searchableElements.forEach(element => {
        const text = element.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            element.style.display = '';
        } else {
            element.style.display = 'none';
        }
    });
}

// ===== FILTROS DE DATA =====
function handleDateFilter(event) {
    const filterType = event.target.dataset.filter;
    const filterValue = event.target.value;
    
    // Aplicar filtro baseado no tipo
    switch(filterType) {
        case 'date-range':
            filterByDateRange(filterValue);
            break;
        case 'month':
            filterByMonth(filterValue);
            break;
        case 'year':
            filterByYear(filterValue);
            break;
    }
}

// ===== FILTROS ESPECÍFICOS =====
function filterByDateRange(range) {
    const today = new Date();
    let startDate = new Date();
    
    switch(range) {
        case 'today':
            startDate = today;
            break;
        case 'week':
            startDate.setDate(today.getDate() - 7);
            break;
        case 'month':
            startDate.setMonth(today.getMonth() - 1);
            break;
        case 'year':
            startDate.setFullYear(today.getFullYear() - 1);
            break;
    }
    
    // Aplicar filtro na tabela ou lista
    applyDateFilter(startDate, today);
}

function filterByMonth(month) {
    // Implementar filtro por mês
    console.log('Filtrando por mês:', month);
}

function filterByYear(year) {
    // Implementar filtro por ano
    console.log('Filtrando por ano:', year);
}

function applyDateFilter(startDate, endDate) {
    // Implementar aplicação do filtro
    console.log('Aplicando filtro de data:', startDate, 'até', endDate);
}

// ===== CONFIGURAÇÃO DE BOTÕES DE AÇÃO =====
function setupActionButtons() {
    // Botões de editar
    const editButtons = document.querySelectorAll('.btn-edit');
    editButtons.forEach(btn => {
        btn.addEventListener('click', handleEdit);
    });
    
    // Botões de deletar
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', handleDelete);
    });
    
    // Botões de confirmar
    const confirmButtons = document.querySelectorAll('.btn-confirm');
    confirmButtons.forEach(btn => {
        btn.addEventListener('click', handleConfirm);
    });
}

// ===== MANIPULAÇÃO DE AÇÕES =====
function handleEdit(event) {
    const itemId = event.target.dataset.id;
    const itemType = event.target.dataset.type;
    
    // Redirecionar para página de edição
    window.location.href = `/${itemType}/editar/${itemId}`;
}

function handleDelete(event) {
    const itemId = event.target.dataset.id;
    const itemType = event.target.dataset.type;
    
    if (confirm(`Tem certeza que deseja excluir este ${itemType}?`)) {
        // Fazer requisição de exclusão
        deleteItem(itemId, itemType);
    }
}

function handleConfirm(event) {
    const itemId = event.target.dataset.id;
    const itemType = event.target.dataset.type;
    
    // Confirmar item (agendamento, etc.)
    confirmItem(itemId, itemType);
}

// ===== REQUISIÇÕES AJAX =====
async function deleteItem(id, type) {
    try {
        const response = await fetch(`/api/${type}/${id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
            }
        });
        
        if (response.ok) {
            showToast('Item excluído com sucesso!', 'success');
            // Recarregar página ou remover elemento
            location.reload();
        } else {
            showToast('Erro ao excluir item', 'error');
        }
    } catch (error) {
        console.error('Erro na requisição:', error);
        showToast('Erro de conexão', 'error');
    }
}

async function confirmItem(id, type) {
    try {
        const response = await fetch(`/api/${type}/${id}/confirmar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
            }
        });
        
        if (response.ok) {
            showToast('Item confirmado com sucesso!', 'success');
            location.reload();
        } else {
            showToast('Erro ao confirmar item', 'error');
        }
    } catch (error) {
        console.error('Erro na requisição:', error);
        showToast('Erro de conexão', 'error');
    }
}

// ===== CARREGAMENTO DE DADOS DO DASHBOARD =====
function loadDashboardData() {
    // Carregar estatísticas se estiver na página de dashboard
    if (window.location.pathname === '/dashboard') {
        loadDashboardStats();
        loadRecentAppointments();
        loadCharts();
    }
}

async function loadDashboardStats() {
    try {
        const response = await fetch('/api/analytics/estatisticas-gerais');
        const data = await response.json();
        
        // Atualizar cards de estatísticas
        updateStatsCards(data);
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

function updateStatsCards(data) {
    // Atualizar números nas cards
    const elements = {
        'agendamentos-mes': data.agendamentos_mes,
        'receita-mes': `R$ ${data.receita_mes.toFixed(2)}`,
        'agendamentos-semana': data.agendamentos_semana,
        'taxa-faltas': `${data.taxa_faltas}%`
    };
    
    Object.keys(elements).forEach(key => {
        const element = document.getElementById(key);
        if (element) {
            element.textContent = elements[key];
        }
    });
}

// ===== NOTIFICAÇÕES TOAST =====
function setupToastNotifications() {
    // Criar container de toasts se não existir
    if (!document.getElementById('toast-container')) {
        const toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Mostrar toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remover toast após ser fechado
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// ===== UTILITÁRIOS =====
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR');
}

// ===== EXPORTAÇÃO DE FUNÇÕES =====
window.SistemaClinica = {
    showToast,
    formatCurrency,
    formatDate,
    formatDateTime,
    deleteItem,
    confirmItem
};
