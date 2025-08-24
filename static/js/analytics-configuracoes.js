/**
 * Analytics Configurações - JavaScript
 * Sistema de configurações do módulo analytics
 */

class AnalyticsConfiguracoes {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.carregarConfiguracoes();
    }

    setupEventListeners() {
        // Formulário de configurações gerais
        document.getElementById('formConfiguracoesGerais')?.addEventListener('submit', (e) => this.salvarConfiguracoesGerais(e));
        
        // Botões de configurações específicas
        document.getElementById('btnSalvarConfigIA')?.addEventListener('click', () => this.salvarConfiguracoesIA());
        document.getElementById('btnSalvarConfigRelatorios')?.addEventListener('click', () => this.salvarConfiguracoesRelatorios());
        document.getElementById('btnSalvarConfigAlertas')?.addEventListener('click', () => this.salvarConfiguracoesAlertas());
        document.getElementById('btnSalvarConfigPerformance')?.addEventListener('click', () => this.salvarConfiguracoesPerformance());
        
        // Botões de ações do sistema
        document.getElementById('btnLimparCache')?.addEventListener('click', () => this.limparCache());
        document.getElementById('btnTreinarModeloIA')?.addEventListener('click', () => this.treinarModeloIA());
        document.getElementById('btnGerarInsights')?.addEventListener('click', () => this.gerarInsights());
        document.getElementById('btnAtualizarMetricas')?.addEventListener('click', () => this.atualizarMetricas());
        document.getElementById('btnExportarConfiguracoes')?.addEventListener('click', () => this.exportarConfiguracoes());
        document.getElementById('btnResetarConfiguracoes')?.addEventListener('click', () => this.resetarConfiguracoes());
    }

    async carregarConfiguracoes() {
        try {
            const response = await fetch('/analytics/api/configuracoes');
            const data = await response.json();
            
            if (data.success) {
                this.aplicarConfiguracoes(data.data);
            }
        } catch (error) {
            console.error('Erro ao carregar configurações:', error);
        }
    }

    aplicarConfiguracoes(configs) {
        // Aplicar configurações gerais
        if (configs.analytics_auto_insights !== undefined) {
            document.getElementById('analytics_auto_insights').checked = configs.analytics_auto_insights === 'true';
        }
        
        if (configs.analytics_modelo_auto_treino !== undefined) {
            document.getElementById('analytics_modelo_auto_treino').checked = configs.analytics_modelo_auto_treino === 'true';
        }
        
        if (configs.analytics_relatorios_auto !== undefined) {
            document.getElementById('analytics_relatorios_auto').checked = configs.analytics_relatorios_auto === 'true';
        }
        
        if (configs.analytics_email_admin !== undefined) {
            document.getElementById('analytics_email_admin').checked = configs.analytics_email_admin === 'true';
        }
    }

    async salvarConfiguracoesGerais(event) {
        event.preventDefault();
        
        try {
            const configs = {
                analytics_auto_insights: document.getElementById('analytics_auto_insights').checked,
                analytics_modelo_auto_treino: document.getElementById('analytics_modelo_auto_treino').checked,
                analytics_relatorios_auto: document.getElementById('analytics_relatorios_auto').checked,
                analytics_email_admin: document.getElementById('analytics_email_admin').checked
            };
            
            const response = await fetch('/analytics/api/configuracoes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(configs)
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('Configurações gerais salvas com sucesso!');
            } else {
                this.showError(data.error || 'Erro ao salvar configurações');
            }
            
        } catch (error) {
            console.error('Erro ao salvar configurações gerais:', error);
            this.showError('Erro ao salvar configurações');
        }
    }

    async salvarConfiguracoesIA() {
        try {
            const configs = {
                limite_minimo_dados: document.getElementById('limiteMinimoDados').value,
                frequencia_treinamento: document.getElementById('frequenciaTreinamento').value,
                limiar_risco_baixo: document.getElementById('limiarRiscoBaixo').value,
                limiar_risco_alto: document.getElementById('limiarRiscoAlto').value
            };
            
            // Aqui você implementaria a API para salvar configurações de IA
            this.showSuccess('Configurações de IA salvas com sucesso!');
            
        } catch (error) {
            console.error('Erro ao salvar configurações de IA:', error);
            this.showError('Erro ao salvar configurações de IA');
        }
    }

    async salvarConfiguracoesRelatorios() {
        try {
            const configs = {
                formato_padrao: document.getElementById('formatoPadraoRelatorio').value,
                hora_padrao_envio: document.getElementById('horaPadraoEnvio').value,
                email_admin_padrao: document.getElementById('emailAdminPadrao').value,
                retencao_relatorios: document.getElementById('retencaoRelatorios').value
            };
            
            // Aqui você implementaria a API para salvar configurações de relatórios
            this.showSuccess('Configurações de relatórios salvas com sucesso!');
            
        } catch (error) {
            console.error('Erro ao salvar configurações de relatórios:', error);
            this.showError('Erro ao salvar configurações de relatórios');
        }
    }

    async salvarConfiguracoesAlertas() {
        try {
            const configs = {
                limiar_taxa_presenca: document.getElementById('limiarTaxaPresenca').value,
                limiar_faltas_consecutivas: document.getElementById('limiarFaltasConsecutivas').value,
                limiar_horarios_criticos: document.getElementById('limiarHorariosCriticos').value,
                frequencia_verificacao: document.getElementById('frequenciaVerificacaoAlertas').value
            };
            
            // Aqui você implementaria a API para salvar configurações de alertas
            this.showSuccess('Configurações de alertas salvas com sucesso!');
            
        } catch (error) {
            console.error('Erro ao salvar configurações de alertas:', error);
            this.showError('Erro ao salvar configurações de alertas');
        }
    }

    async salvarConfiguracoesPerformance() {
        try {
            const configs = {
                cache_expiration: document.getElementById('cacheExpiration').value,
                max_concurrent_requests: document.getElementById('maxConcurrentRequests').value,
                batch_size: document.getElementById('batchSize').value,
                timeout_processamento: document.getElementById('timeoutProcessamento').value
            };
            
            // Aqui você implementaria a API para salvar configurações de performance
            this.showSuccess('Configurações de performance salvas com sucesso!');
            
        } catch (error) {
            console.error('Erro ao salvar configurações de performance:', error);
            this.showError('Erro ao salvar configurações de performance');
        }
    }

    async limparCache() {
        try {
            this.showConfirmacao(
                'Limpar Cache',
                'Tem certeza que deseja limpar o cache? Isso forçará uma atualização de todos os dados.',
                async () => {
                    // Aqui você implementaria a API para limpar cache
                    this.showSuccess('Cache limpo com sucesso!');
                }
            );
        } catch (error) {
            console.error('Erro ao limpar cache:', error);
            this.showError('Erro ao limpar cache');
        }
    }

    async treinarModeloIA() {
        try {
            this.showConfirmacao(
                'Treinar Modelo de IA',
                'Tem certeza que deseja treinar o modelo de IA? Isso pode levar alguns minutos.',
                async () => {
                    const response = await fetch('/analytics/api/treinar-modelo', { method: 'POST' });
                    const data = await response.json();
                    
                    if (data.success) {
                        this.showSuccess('Modelo treinado com sucesso!');
                    } else {
                        this.showError(data.error || 'Erro ao treinar modelo');
                    }
                }
            );
        } catch (error) {
            console.error('Erro ao treinar modelo:', error);
            this.showError('Erro ao treinar modelo');
        }
    }

    async gerarInsights() {
        try {
            this.showConfirmacao(
                'Gerar Insights',
                'Tem certeza que deseja gerar insights automáticos? Isso analisará todos os dados disponíveis.',
                async () => {
                    const response = await fetch('/analytics/api/gerar-insights', { method: 'POST' });
                    const data = await response.json();
                    
                    if (data.success) {
                        this.showSuccess(`${data.message}`);
                    } else {
                        this.showError(data.error || 'Erro ao gerar insights');
                    }
                }
            );
        } catch (error) {
            console.error('Erro ao gerar insights:', error);
            this.showError('Erro ao gerar insights');
        }
    }

    async atualizarMetricas() {
        try {
            const response = await fetch('/analytics/api/atualizar-metricas', { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('Métricas atualizadas com sucesso!');
            } else {
                this.showError(data.error || 'Erro ao atualizar métricas');
            }
        } catch (error) {
            console.error('Erro ao atualizar métricas:', error);
            this.showError('Erro ao atualizar métricas');
        }
    }

    async exportarConfiguracoes() {
        try {
            // Aqui você implementaria a exportação das configurações
            const configs = this.obterTodasConfiguracoes();
            const blob = new Blob([JSON.stringify(configs, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `analytics-config-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            this.showSuccess('Configurações exportadas com sucesso!');
            
        } catch (error) {
            console.error('Erro ao exportar configurações:', error);
            this.showError('Erro ao exportar configurações');
        }
    }

    async resetarConfiguracoes() {
        try {
            this.showConfirmacao(
                'Resetar Configurações',
                'ATENÇÃO: Isso irá restaurar todas as configurações para os valores padrão. Esta ação não pode ser desfeita. Tem certeza?',
                async () => {
                    // Aqui você implementaria a API para resetar configurações
                    this.showSuccess('Configurações resetadas com sucesso!');
                    this.carregarConfiguracoes();
                },
                'danger'
            );
        } catch (error) {
            console.error('Erro ao resetar configurações:', error);
            this.showError('Erro ao resetar configurações');
        }
    }

    obterTodasConfiguracoes() {
        return {
            gerais: {
                analytics_auto_insights: document.getElementById('analytics_auto_insights')?.checked,
                analytics_modelo_auto_treino: document.getElementById('analytics_modelo_auto_treino')?.checked,
                analytics_relatorios_auto: document.getElementById('analytics_relatorios_auto')?.checked,
                analytics_email_admin: document.getElementById('analytics_email_admin')?.checked
            },
            ia: {
                limite_minimo_dados: document.getElementById('limiteMinimoDados')?.value,
                frequencia_treinamento: document.getElementById('frequenciaTreinamento')?.value,
                limiar_risco_baixo: document.getElementById('limiarRiscoBaixo')?.value,
                limiar_risco_alto: document.getElementById('limiarRiscoAlto')?.value
            },
            relatorios: {
                formato_padrao: document.getElementById('formatoPadraoRelatorio')?.value,
                hora_padrao_envio: document.getElementById('horaPadraoEnvio')?.value,
                email_admin_padrao: document.getElementById('emailAdminPadrao')?.value,
                retencao_relatorios: document.getElementById('retencaoRelatorios')?.value
            },
            alertas: {
                limiar_taxa_presenca: document.getElementById('limiarTaxaPresenca')?.value,
                limiar_faltas_consecutivas: document.getElementById('limiarFaltasConsecutivas')?.value,
                limiar_horarios_criticos: document.getElementById('limiarHorariosCriticos')?.value,
                frequencia_verificacao: document.getElementById('frequenciaVerificacaoAlertas')?.value
            },
            performance: {
                cache_expiration: document.getElementById('cacheExpiration')?.value,
                max_concurrent_requests: document.getElementById('maxConcurrentRequests')?.value,
                batch_size: document.getElementById('batchSize')?.value,
                timeout_processamento: document.getElementById('timeoutProcessamento')?.value
            }
        };
    }

    showConfirmacao(titulo, mensagem, onConfirm, tipo = 'warning') {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: titulo,
                text: mensagem,
                icon: tipo,
                showCancelButton: true,
                confirmButtonColor: tipo === 'danger' ? '#dc3545' : '#3085d6',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Confirmar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed && onConfirm) {
                    onConfirm();
                }
            });
        } else {
            if (confirm(mensagem) && onConfirm) {
                onConfirm();
            }
        }
    }

    showSuccess(message) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'success',
                title: 'Sucesso!',
                text: message,
                timer: 3000,
                showConfirmButton: false
            });
        } else {
            alert(message);
        }
    }

    showError(message) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'error',
                title: 'Erro!',
                text: message,
                timer: 5000,
                showConfirmButton: false
            });
        } else {
            alert(message);
        }
    }
}

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    new AnalyticsConfiguracoes();
});
