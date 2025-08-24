/**
 * Relatórios JavaScript - Funções Globais
 * Sistema Clínica - Página de Relatórios
 * 
 * Este arquivo contém todas as funções necessárias para os botões da página de relatórios
 * e resolve os erros de "function not defined" no console.
 */

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
        
        console.log('🔍 Filtros aplicados:', { periodo, profissional, servico });
        
        // Verificar se o dashboard está disponível
        if (window.relatoriosDashboard) {
            window.relatoriosDashboard.atualizarGraficos();
        } else {
            console.log('⚠️ Dashboard ainda não inicializado, aguardando...');
            // Aguardar um pouco e tentar novamente
            setTimeout(() => {
                if (window.relatoriosDashboard) {
                    window.relatoriosDashboard.atualizarGraficos();
                }
            }, 1000);
        }
        
        // Mostrar feedback visual
        showToast('Filtros aplicados com sucesso!', 'success');
        
    } catch (error) {
        console.error('❌ Erro ao aplicar filtros:', error);
        showToast('Erro ao aplicar filtros', 'error');
    }
}

/**
 * Atualiza todos os relatórios e gráficos
 * Chamada pelo botão "Atualizar"
 */
function atualizarRelatorios() {
    try {
        console.log('🔄 Atualizando relatórios...');
        
        if (window.relatoriosDashboard) {
            window.relatoriosDashboard.carregarDadosIniciais();
            showToast('Relatórios atualizados!', 'success');
        } else {
            console.log('⚠️ Dashboard ainda não inicializado, aguardando...');
            // Aguardar um pouco e tentar novamente
            setTimeout(() => {
                if (window.relatoriosDashboard) {
                    window.relatoriosDashboard.carregarDadosIniciais();
                    showToast('Relatórios atualizados!', 'success');
                }
            }, 1000);
        }
        
    } catch (error) {
        console.error('❌ Erro ao atualizar relatórios:', error);
        showToast('Erro ao atualizar relatórios', 'error');
    }
}

/**
 * Exporta relatórios em diferentes formatos
 * Chamada pelos botões de exportação (PDF, CSV)
 */
function exportarRelatorio(formato) {
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
}

/**
 * Altera o período dos gráficos
 * Chamada pelos botões de período (12M, 6M, 3M)
 */
function alterarPeriodoGrafico(periodo) {
    try {
        console.log(`📈 Alterando período do gráfico para: ${periodo} meses`);
        
        if (window.relatoriosDashboard) {
            window.relatoriosDashboard.currentPeriod = periodo;
            window.relatoriosDashboard.atualizarGraficos();
            showToast(`Período alterado para ${periodo} meses`, 'info');
        } else {
            console.log('⚠️ Dashboard ainda não inicializado, aguardando...');
            // Aguardar um pouco e tentar novamente
            setTimeout(() => {
                if (window.relatoriosDashboard) {
                    window.relatoriosDashboard.currentPeriod = periodo;
                    window.relatoriosDashboard.atualizarGraficos();
                    showToast(`Período alterado para ${periodo} meses`, 'info');
                }
            }, 1000);
        }
        
    } catch (error) {
        console.error('❌ Erro ao alterar período:', error);
        showToast('Erro ao alterar período', 'error');
    }
}

/**
 * Aplica filtros gerais
 * Função auxiliar para filtros
 */
function aplicarFiltros() {
    try {
        if (window.relatoriosDashboard) {
            window.relatoriosDashboard.atualizarGraficos();
        }
    } catch (error) {
        console.error('❌ Erro ao aplicar filtros:', error);
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
            { label: 'Exportar CSV', action: () => exportarRelatorio('csv') },
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

// ========================================
// FUNÇÃO DE TOAST (NOTIFICAÇÃO)
// ========================================

/**
 * Mostra uma notificação toast
 * @param {string} message - Mensagem a ser exibida
 * @param {string} type - Tipo da notificação (success, error, warning, info)
 */
function showToast(message, type = 'success') {
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
}

// ========================================
// VERIFICAÇÃO DE FUNÇÕES
// ========================================

// Verificar se as funções foram definidas corretamente
console.log('🔍 Verificando funções de relatórios...');
console.log('✅ aplicarFiltrosSelects:', typeof aplicarFiltrosSelects);
console.log('✅ atualizarRelatorios:', typeof atualizarRelatorios);
console.log('✅ exportarRelatorio:', typeof exportarRelatorio);
console.log('✅ alterarPeriodoGrafico:', typeof alterarPeriodoGrafico);
console.log('✅ showQuickActions:', typeof showQuickActions);
console.log('✅ aplicarFiltros:', typeof aplicarFiltros);

// Verificação adicional para debug
console.log('🔍 Debug - Funções individuais:');
console.log('  - aplicarFiltrosSelects:', aplicarFiltrosSelects);
console.log('  - atualizarRelatorios:', atualizarRelatorios);
console.log('  - exportarRelatorio:', exportarRelatorio);
console.log('  - alterarPeriodoGrafico:', alterarPeriodoGrafico);
console.log('  - showQuickActions:', showQuickActions);
console.log('  - aplicarFiltros:', aplicarFiltros);
console.log('  - showToast:', showToast);

// ========================================
// EXPOSIÇÃO GLOBAL DAS FUNÇÕES
// ========================================

// Garantir que todas as funções estejam disponíveis globalmente
try {
    window.aplicarFiltrosSelects = aplicarFiltrosSelects;
    window.atualizarRelatorios = atualizarRelatorios;
    window.exportarRelatorio = exportarRelatorio;
    window.alterarPeriodoGrafico = alterarPeriodoGrafico;
    window.showQuickActions = showQuickActions;
    window.aplicarFiltros = aplicarFiltros;
    window.showToast = showToast;
    
    console.log('🌐 Funções expostas globalmente com sucesso!');
    
    // Verificação final
    console.log('🔍 Verificação final das funções no window:');
    console.log('  - window.aplicarFiltrosSelects:', typeof window.aplicarFiltrosSelects);
    console.log('  - window.atualizarRelatorios:', typeof window.atualizarRelatorios);
    console.log('  - window.exportarRelatorio:', typeof window.exportarRelatorio);
    console.log('  - window.alterarPeriodoGrafico:', typeof window.alterarPeriodoGrafico);
    console.log('  - window.showQuickActions:', typeof window.showQuickActions);
    console.log('  - window.aplicarFiltros:', typeof window.aplicarFiltros);
    console.log('  - window.showToast:', typeof window.showToast);
    
} catch (error) {
    console.error('❌ Erro ao expor funções globalmente:', error);
}
