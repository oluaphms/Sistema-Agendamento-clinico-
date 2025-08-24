/**
 * Relatórios JavaScript - Funções Globais
 * Sistema Clínica - Página de Relatórios
 * 
 * Este arquivo contém todas as funções necessárias para os botões da página de relatórios
 * e resolve os erros de "function not defined" no console.
 */

// ========================================
// VERIFICAÇÃO IMEDIATA DE FUNÇÕES EXISTENTES
// ========================================

console.log('🚀 relatorios.js carregando...');

// Verificar se as funções já existem (para evitar redefinição)
if (typeof window.atualizarRelatorios === 'function') {
    console.log('⚠️ atualizarRelatorios já existe, não redefinindo');
} else {
    console.log('✅ Definindo atualizarRelatorios...');
}

if (typeof window.exportarRelatorio === 'function') {
    console.log('⚠️ exportarRelatorio já existe, não redefinindo');
} else {
    console.log('✅ Definindo exportarRelatorio...');
}

if (typeof window.aplicarFiltrosSelects !== 'function') {
    console.log('✅ Definindo aplicarFiltrosSelects...');
}

// ========================================
// FUNÇÃO SHOWTOAST (DEFINIDA PRIMEIRO)
// ========================================

// Função showToast necessária para as outras funções
if (typeof window.showToast !== 'function') {
    window.showToast = function(message, type = 'success') {
        try {
            // Verificar se SweetAlert2 está disponível
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    icon: type,
                    title: message,
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false,
                    timer: 3000,
                    timerProgressBar: true
                });
            } else {
                // Fallback para alert simples
                alert(message);
            }
        } catch (error) {
            console.error('❌ Erro ao mostrar toast:', error);
            alert(message);
        }
    };
    console.log('✅ showToast definida globalmente');
}

// ========================================
// DEFINIÇÃO IMEDIATA DAS FUNÇÕES GLOBAIS
// ========================================

// Definir funções imediatamente no escopo global para evitar erros
if (typeof window.atualizarRelatorios !== 'function') {
    window.atualizarRelatorios = function() {
        try {
            console.log('🔄 Atualizando relatórios...');
            
            // Atualizar estatísticas
            atualizarEstatisticas();
            
            // Atualizar gráficos
            if (window.relatoriosDashboard) {
                window.relatoriosDashboard.atualizarGraficos();
            }
            
            showToast('Relatórios atualizados!', 'success');
            
        } catch (error) {
            console.error('❌ Erro ao atualizar relatórios:', error);
            showToast('Erro ao atualizar relatórios', 'error');
        }
    };
    console.log('✅ atualizarRelatorios definido globalmente');
}

if (typeof window.exportarRelatorio !== 'function') {
    window.exportarRelatorio = function(formato) {
        try {
            console.log(`📊 Exportando relatório em formato: ${formato}`);
            
            // Obter datas dos filtros
            const dataInicio = document.getElementById('dataInicioExport')?.value;
            const dataFim = document.getElementById('dataFimExport')?.value;
            
            // Construir URL de exportação
            let url = `/exportar?formato=${formato}`;
            
            if (dataInicio) {
                url += `&inicio=${dataInicio}`;
            }
            
            if (dataFim) {
                url += `&fim=${dataFim}`;
            }
            
            // Mostrar loading
            if (window.relatoriosDashboard) {
                window.relatoriosDashboard.showLoading();
            }
            
            // Fazer download
            const link = document.createElement('a');
            link.href = url;
            link.download = `relatorio_agendamentos_${dataInicio || 'todos'}_${dataFim || 'todos'}.${formato === 'pdf' ? 'html' : 'csv'}`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            // Ocultar loading
            if (window.relatoriosDashboard) {
                window.relatoriosDashboard.hideLoading();
            }
            
            // Mostrar mensagem de sucesso
            if (formato === 'pdf') {
                showToast('Relatório HTML gerado! Use a função de impressão do navegador para salvar como PDF.', 'success');
            } else {
                showToast('Relatório CSV exportado com sucesso!', 'success');
            }
            
        } catch (error) {
            console.error('❌ Erro ao exportar relatório:', error);
            showToast('Erro ao exportar relatório. Tente novamente.', 'error');
            
            // Ocultar loading em caso de erro
            if (window.relatoriosDashboard) {
                window.relatoriosDashboard.hideLoading();
            }
        }
    };
    console.log('✅ exportarRelatorio definido globalmente');
}

// Função showToast já foi definida no início do arquivo

// ========================================
// FUNÇÕES GLOBAIS PARA RELATÓRIOS
// ========================================

/**
 * Aplica filtros dos selects de filtro
 * Chamada pelos botões de filtro e selects
 */
function aplicarFiltrosSelects() {
    try {
        const periodo = document.getElementById('periodoFiltro')?.value;
        const profissional = document.getElementById('profissionalFiltro')?.value;
        const servico = document.getElementById('servicoFiltro')?.value;
        const dataInicio = document.getElementById('dataInicioExport')?.value;
        const dataFim = document.getElementById('dataFimExport')?.value;
        
        console.log('🔍 Filtros aplicados:', { periodo, profissional, servico, dataInicio, dataFim });
        
        // Atualizar estatísticas com os novos filtros
        atualizarEstatisticas(periodo, profissional, servico, dataInicio, dataFim);
        
        // Atualizar gráficos
        if (window.relatoriosDashboard) {
            window.relatoriosDashboard.atualizarGraficos();
        }
        
        // Mostrar feedback visual
        showToast('Filtros aplicados com sucesso!', 'success');
        
    } catch (error) {
        console.error('❌ Erro ao aplicar filtros:', error);
        showToast('Erro ao aplicar filtros', 'error');
    }
}

// Garantir que a função seja definida globalmente
if (typeof window.aplicarFiltrosSelects !== 'function') {
    window.aplicarFiltrosSelects = aplicarFiltrosSelects;
    console.log('✅ aplicarFiltrosSelects exposto globalmente');
}

/**
 * Atualiza as estatísticas baseado nos filtros aplicados
 */
async function atualizarEstatisticas(periodo = 30, profissional = '', servico = '', dataInicio = '', dataFim = '') {
    try {
        console.log('📊 Atualizando estatísticas...');
        
        // Construir URL com parâmetros
        let url = `/api/relatorios/estatisticas?periodo=${periodo}`;
        
        if (profissional) {
            url += `&profissional=${profissional}`;
        }
        
        if (servico) {
            url += `&servico=${servico}`;
        }
        
        if (dataInicio) {
            url += `&data_inicio=${dataInicio}`;
        }
        
        if (dataFim) {
            url += `&data_fim=${dataFim}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            atualizarCardsEstatisticas(data.estatisticas);
            showToast('Estatísticas atualizadas!', 'success');
        } else {
            console.error('❌ Erro ao buscar estatísticas:', data.error);
            showToast('Erro ao buscar estatísticas', 'error');
        }
        
    } catch (error) {
        console.error('❌ Erro ao atualizar estatísticas:', error);
        showToast('Erro ao atualizar estatísticas', 'error');
    }
}

/**
 * Atualiza os cards de estatísticas com novos dados
 */
function atualizarCardsEstatisticas(estatisticas) {
    try {
        // Atualizar card de agendamentos
        const agendamentosElement = document.getElementById('agendamentosPeriodo');
        if (agendamentosElement) {
            agendamentosElement.textContent = estatisticas.agendamentos_periodo;
        }
        
        // Atualizar card de receita
        const receitaElement = document.getElementById('receitaPeriodo');
        if (receitaElement) {
            receitaElement.textContent = `R$ ${estatisticas.receita_periodo.toFixed(2)}`;
        }
        
        // Atualizar card de taxa de confirmação
        const confirmacaoElement = document.getElementById('taxaConfirmacao');
        if (confirmacaoElement) {
            confirmacaoElement.textContent = `${estatisticas.taxa_confirmacao}%`;
        }
        
        // Atualizar card de taxa de faltas
        const faltasElement = document.getElementById('taxaFaltas');
        if (faltasElement) {
            faltasElement.textContent = `${estatisticas.taxa_faltas}%`;
        }
        
        // Atualizar informações de período
        const periodoInfo = document.getElementById('periodoInfo');
        if (periodoInfo) {
            periodoInfo.textContent = `${estatisticas.periodo_dias} dias (${estatisticas.data_inicio} a ${estatisticas.data_fim})`;
        }
        
        console.log('✅ Cards de estatísticas atualizados');
        
    } catch (error) {
        console.error('❌ Erro ao atualizar cards:', error);
    }
}

/**
 * Popula os filtros de profissionais e serviços
 */
async function popularFiltros() {
    try {
        console.log('🔍 Populando filtros...');
        
        const response = await fetch('/api/relatorios/filtros');
        const data = await response.json();
        
        if (data.success) {
            // Popular filtro de profissionais
            const profissionalSelect = document.getElementById('profissionalFiltro');
            if (profissionalSelect) {
                profissionalSelect.innerHTML = '<option value="">Todos os Profissionais</option>';
                data.profissionais.forEach(prof => {
                    const option = document.createElement('option');
                    option.value = prof.id;
                    option.textContent = prof.nome;
                    profissionalSelect.appendChild(option);
                });
            }
            
            // Popular filtro de serviços
            const servicoSelect = document.getElementById('servicoFiltro');
            if (servicoSelect) {
                servicoSelect.innerHTML = '<option value="">Todos os Serviços</option>';
                data.servicos.forEach(serv => {
                    const option = document.createElement('option');
                    option.value = serv.id;
                    option.textContent = serv.nome;
                    servicoSelect.appendChild(option);
                });
            }
            
            console.log('✅ Filtros populados com sucesso');
        } else {
            console.error('❌ Erro ao popular filtros:', data.error);
        }
        
    } catch (error) {
        console.error('❌ Erro ao popular filtros:', error);
    }
}

/**
 * Inicializa a página de relatórios
 */
function inicializarRelatorios() {
    try {
        console.log('🚀 Inicializando página de relatórios...');
        
        // Popular filtros
        popularFiltros();
        
        // Definir datas padrão
        const hoje = new Date();
        const dataInicio = new Date();
        dataInicio.setDate(hoje.getDate() - 30);
        
        const dataInicioInput = document.getElementById('dataInicioExport');
        const dataFimInput = document.getElementById('dataFimExport');
        
        if (dataInicioInput) {
            dataInicioInput.value = dataInicio.toISOString().split('T')[0];
        }
        
        if (dataFimInput) {
            dataFimInput.value = hoje.toISOString().split('T')[0];
        }
        
        // Atualizar estatísticas iniciais
        atualizarEstatisticas();
        
        console.log('✅ Página de relatórios inicializada');
        
    } catch (error) {
        console.error('❌ Erro ao inicializar relatórios:', error);
    }
}

/**
 * Altera o período dos gráficos
 * Chamada pelos botões de período (12M, 6M, 3M)
 */
function alterarPeriodoGrafico(periodo) {
    try {
        console.log(`📈 Alterando período do gráfico para: ${periodo} meses`);
        
        // Atualizar botões ativos
        document.querySelectorAll('[data-periodo]').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');
        
        // Atualizar estatísticas com o novo período
        atualizarEstatisticas(periodo * 30);
        
        // Atualizar gráficos
        if (window.relatoriosDashboard) {
            window.relatoriosDashboard.currentPeriod = periodo;
            window.relatoriosDashboard.atualizarGraficos();
        }
        
        showToast(`Período alterado para ${periodo} meses`, 'info');
        
    } catch (error) {
        console.error('❌ Erro ao alterar período:', error);
        showToast('Erro ao alterar período', 'error');
    }
}

/**
 * Mostra ações rápidas
 * Chamada pelo botão flutuante (FAB)
 */
function showQuickActions() {
    try {
        console.log('⚡ Mostrando ações rápidas...');
        
        // Implementar menu de ações rápidas
        const actions = [
            { label: 'Exportar PDF', action: () => exportarRelatorio('pdf') },
            { label: 'Atualizar Dados', action: () => atualizarRelatorios() },
            { label: 'Aplicar Filtros', action: () => aplicarFiltrosSelects() }
        ];
        
        // Criar menu dropdown simples
        const menu = document.createElement('div');
        menu.className = 'quick-actions-menu';
        menu.style.cssText = `
            position: fixed;
            bottom: 80px;
            right: 20px;
            background: var(--bs-dark);
            border-radius: 8px;
            padding: 8px 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 1000;
            min-width: 200px;
        `;
        
        actions.forEach(item => {
            const button = document.createElement('button');
            button.className = 'btn btn-link text-white text-decoration-none w-100 text-start px-3 py-2';
            button.textContent = item.label;
            button.onclick = () => {
                item.action();
                menu.remove();
            };
            menu.appendChild(button);
        });
        
        // Adicionar ao DOM
        document.body.appendChild(menu);
        
        // Remover após 5 segundos ou ao clicar fora
        setTimeout(() => menu.remove(), 5000);
        
        document.addEventListener('click', function removeMenu(e) {
            if (!menu.contains(e.target) && !e.target.closest('.fab')) {
                menu.remove();
                document.removeEventListener('click', removeMenu);
            }
        });
        
    } catch (error) {
        console.error('❌ Erro ao mostrar ações rápidas:', error);
        showToast('Erro ao mostrar ações rápidas', 'error');
    }
}

// Garantir que a função seja definida globalmente
if (typeof window.showQuickActions !== 'function') {
    window.showQuickActions = showQuickActions;
    console.log('✅ showQuickActions exposto globalmente');
}

// Executar inicialização quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    inicializarRelatorios();
});
