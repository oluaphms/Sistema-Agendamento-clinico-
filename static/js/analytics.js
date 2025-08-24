/**
 * Analytics Dashboard - JavaScript Principal
 * Sistema de analytics avançados com gráficos interativos e IA
 */

class AnalyticsDashboard {
    constructor() {
        this.currentPeriod = 'ultimos30dias';
        this.dataInicio = null;
        this.dataFim = null;
        this.charts = {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupDateFilters();
        this.loadInitialData();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Botões de período
        document.getElementById('btnHoje').addEventListener('click', () => this.setPeriod('hoje'));
        document.getElementById('btnUltimos7Dias').addEventListener('click', () => this.setPeriod('ultimos7dias'));
        document.getElementById('btnUltimos30Dias').addEventListener('click', () => this.setPeriod('ultimos30dias'));
        document.getElementById('btnPersonalizado').addEventListener('click', () => this.toggleCustomPeriod());

        // Botões de ação
        document.getElementById('btnGerarInsights').addEventListener('click', () => this.gerarInsights());
        document.getElementById('btnTreinarModelo').addEventListener('click', () => this.treinarModelo());

        // Botões de receita
        document.getElementById('btnMesAtual').addEventListener('click', () => this.carregarReceitaMensal());
        document.getElementById('btnMesAnterior').addEventListener('click', () => this.carregarReceitaMensal('anterior'));

        // Formulário de filtros personalizados
        document.getElementById('dataInicio')?.addEventListener('change', () => this.onDateChange());
        document.getElementById('dataFim')?.addEventListener('change', () => this.onDateChange());
    }

    setupDateFilters() {
        // Definir datas padrão
        const hoje = new Date();
        const dataInicio = new Date();
        dataInicio.setDate(hoje.getDate() - 30);
        
        if (document.getElementById('dataInicio')) {
            document.getElementById('dataInicio').value = dataInicio.toISOString().split('T')[0];
            document.getElementById('dataFim').value = hoje.toISOString().split('T')[0];
        }
    }

    setPeriod(period) {
        this.currentPeriod = period;
        
        // Atualizar botões ativos
        document.querySelectorAll('.btn-group .btn').forEach(btn => btn.classList.remove('active'));
        event.target.classList.add('active');
        
        // Calcular datas baseado no período
        const hoje = new Date();
        let dataInicio = new Date();
        
        switch (period) {
            case 'hoje':
                dataInicio = hoje;
                break;
            case 'ultimos7dias':
                dataInicio.setDate(hoje.getDate() - 7);
                break;
            case 'ultimos30dias':
                dataInicio.setDate(hoje.getDate() - 30);
                break;
        }
        
        this.dataInicio = dataInicio;
        this.dataFim = hoje;
        
        // Ocultar filtros personalizados se não for período personalizado
        if (period !== 'personalizado') {
            document.getElementById('filtrosPeriodo').style.display = 'none';
            this.loadData();
        }
    }

    toggleCustomPeriod() {
        const filtros = document.getElementById('filtrosPeriodo');
        filtros.style.display = filtros.style.display === 'none' ? 'block' : 'none';
        
        if (filtros.style.display === 'block') {
            this.setPeriod('personalizado');
        }
    }

    onDateChange() {
        const dataInicio = document.getElementById('dataInicio').value;
        const dataFim = document.getElementById('dataFim').value;
        
        if (dataInicio && dataFim) {
            this.dataInicio = new Date(dataInicio);
            this.dataFim = new Date(dataFim);
            this.loadData();
        }
    }

    async loadInitialData() {
        this.setPeriod('ultimos30dias');
    }

    async loadData() {
        try {
            // Mostrar loading
            this.showLoading();
            
            // Carregar métricas gerais
            await this.carregarMetricasGerais();
            
            // Carregar gráficos
            await this.carregarGraficoPresenca();
            await this.carregarGraficoStatus();
            await this.carregarGraficoEspecialidade();
            await this.carregarGraficoCrescimento();
            await this.carregarReceitaMensal();
            
            // Carregar insights e previsões
            await this.carregarInsights();
            await this.carregarPrevisoes();
            
            // Ocultar loading
            this.hideLoading();
            
        } catch (error) {
            console.error('Erro ao carregar dados:', error);
            this.showError('Erro ao carregar dados do dashboard');
            this.hideLoading();
        }
    }

    async carregarMetricasGerais() {
        try {
            const params = new URLSearchParams();
            if (this.dataInicio) params.append('data_inicio', this.dataInicio.toISOString().split('T')[0]);
            if (this.dataFim) params.append('data_fim', this.dataFim.toISOString().split('T')[0]);
            
            const response = await fetch(`/analytics/api/metricas-gerais?${params}`);
            const data = await response.json();
            
            if (data.success) {
                this.atualizarKPIs(data.data);
            }
        } catch (error) {
            console.error('Erro ao carregar métricas gerais:', error);
        }
    }

    atualizarKPIs(data) {
        // Atualizar KPIs principais
        document.getElementById('kpiTaxaPresenca').textContent = `${data.presenca.taxa}%`;
        document.getElementById('kpiConsultasRealizadas').textContent = data.presenca.realizados;
        document.getElementById('kpiFaturamento').textContent = `R$ ${data.faturamento.total.toLocaleString('pt-BR')}`;
        document.getElementById('kpiPacientesAtivos').textContent = data.participantes.pacientes_unicos;
        
        // Atualizar cores dos KPIs baseado nos valores
        this.atualizarCoresKPI('kpiTaxaPresenca', data.presenca.taxa, 80, 90);
        this.atualizarCoresKPI('kpiConsultasRealizadas', data.presenca.realizados, 50, 100);
        this.atualizarCoresKPI('kpiFaturamento', data.faturamento.total, 1000, 5000);
        this.atualizarCoresKPI('kpiPacientesAtivos', data.participantes.pacientes_unicos, 20, 50);
    }

    atualizarCoresKPI(elementId, valor, limiarBaixo, limiarAlto) {
        const element = document.getElementById(elementId);
        const card = element.closest('.kpi-card');
        
        // Remover classes de cor anteriores
        card.classList.remove('bg-success', 'bg-warning', 'bg-danger');
        
        // Aplicar cores baseado no valor
        if (valor >= limiarAlto) {
            card.classList.add('bg-success');
        } else if (valor >= limiarBaixo) {
            card.classList.add('bg-warning');
        } else {
            card.classList.add('bg-danger');
        }
    }

    async carregarGraficoPresenca() {
        try {
            const params = new URLSearchParams();
            if (this.dataInicio) params.append('data_inicio', this.dataInicio.toISOString().split('T')[0]);
            if (this.dataFim) params.append('data_fim', this.dataFim.toISOString().split('T')[0]);
            
            const response = await fetch(`/analytics/api/taxa-presenca?${params}`);
            const data = await response.json();
            
            if (data.success) {
                this.criarGraficoPresenca(data.data.por_periodo);
            }
        } catch (error) {
            console.error('Erro ao carregar gráfico de presença:', error);
        }
    }

    criarGraficoPresenca(dados) {
        const trace1 = {
            x: dados.map(d => d.data),
            y: dados.map(d => d.taxa_presenca),
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Taxa de Presença',
            line: { color: '#0d6efd', width: 3 },
            marker: { size: 8, color: '#0d6efd' }
        };

        const trace2 = {
            x: dados.map(d => d.data),
            y: dados.map(d => d.total),
            type: 'bar',
            name: 'Total de Consultas',
            yaxis: 'y2',
            marker: { color: '#6c757d', opacity: 0.7 }
        };

        const layout = {
            title: 'Taxa de Presença ao Longo do Tempo',
            xaxis: { title: 'Data' },
            yaxis: { 
                title: 'Taxa de Presença (%)',
                range: [0, 100]
            },
            yaxis2: {
                title: 'Total de Consultas',
                overlaying: 'y',
                side: 'right'
            },
            legend: { x: 0, y: 1 },
            margin: { l: 50, r: 50, t: 50, b: 50 }
        };

        const config = { responsive: true, displayModeBar: false };

        Plotly.newPlot('graficoPresenca', [trace1, trace2], layout, config);
    }

    async carregarGraficoStatus() {
        try {
            const params = new URLSearchParams();
            if (this.dataInicio) params.append('data_inicio', this.dataInicio.toISOString().split('T')[0]);
            if (this.dataFim) params.append('data_fim', this.dataFim.toISOString().split('T')[0]);
            
            const response = await fetch(`/analytics/api/metricas-gerais?${params}`);
            const data = await response.json();
            
            if (data.success) {
                this.criarGraficoStatus(data.data.agendamentos.por_status);
            }
        } catch (error) {
            console.error('Erro ao carregar gráfico de status:', error);
        }
    }

    criarGraficoStatus(dados) {
        const labels = Object.keys(dados);
        const values = Object.values(dados);
        const colors = ['#28a745', '#ffc107', '#dc3545', '#6c757d', '#17a2b8'];

        const trace = {
            values: values,
            labels: labels,
            type: 'pie',
            marker: { colors: colors },
            textinfo: 'label+percent',
            textposition: 'outside',
            hole: 0.4
        };

        const layout = {
            title: 'Status dos Agendamentos',
            margin: { l: 20, r: 20, t: 40, b: 20 }
        };

        const config = { responsive: true, displayModeBar: false };

        Plotly.newPlot('graficoStatus', [trace], layout, config);
    }

    async carregarGraficoEspecialidade() {
        try {
            const params = new URLSearchParams();
            if (this.dataInicio) params.append('data_inicio', this.dataInicio.toISOString().split('T')[0]);
            if (this.dataFim) params.append('data_fim', this.dataFim.toISOString().split('T')[0]);
            
            const response = await fetch(`/analytics/api/consultas-especialidade?${params}`);
            const data = await response.json();
            
            if (data.success) {
                this.criarGraficoEspecialidade(data.data);
            }
        } catch (error) {
            console.error('Erro ao carregar gráfico de especialidade:', error);
        }
    }

    criarGraficoEspecialidade(dados) {
        const trace = {
            x: dados.map(d => d.especialidade),
            y: dados.map(d => d.total_consultas),
            type: 'bar',
            marker: { 
                color: dados.map(d => d.taxa_realizacao > 80 ? '#28a745' : d.taxa_realizacao > 60 ? '#ffc107' : '#dc3545'),
                opacity: 0.8
            },
            text: dados.map(d => `${d.taxa_realizacao}%`),
            textposition: 'auto'
        };

        const layout = {
            title: 'Consultas por Especialidade',
            xaxis: { title: 'Especialidade' },
            yaxis: { title: 'Total de Consultas' },
            margin: { l: 60, r: 20, t: 50, b: 80 }
        };

        const config = { responsive: true, displayModeBar: false };

        Plotly.newPlot('graficoEspecialidade', [trace], layout, config);
    }

    async carregarGraficoCrescimento() {
        try {
            const response = await fetch('/analytics/api/crescimento-pacientes?meses=12');
            const data = await response.json();
            
            if (data.success) {
                this.criarGraficoCrescimento(data.data);
            }
        } catch (error) {
            console.error('Erro ao carregar gráfico de crescimento:', error);
        }
    }

    criarGraficoCrescimento(dados) {
        const trace1 = {
            x: dados.map(d => d.mes),
            y: dados.map(d => d.pacientes_ativos),
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Pacientes Ativos',
            line: { color: '#0d6efd', width: 3 },
            marker: { size: 8, color: '#0d6efd' }
        };

        const trace2 = {
            x: dados.map(d => d.mes),
            y: dados.map(d => d.novos_pacientes),
            type: 'bar',
            name: 'Novos Pacientes',
            marker: { color: '#28a745', opacity: 0.7 }
        };

        const layout = {
            title: 'Crescimento de Pacientes',
            xaxis: { title: 'Mês' },
            yaxis: { title: 'Quantidade de Pacientes' },
            legend: { x: 0, y: 1 },
            margin: { l: 60, r: 20, t: 50, b: 60 }
        };

        const config = { responsive: true, displayModeBar: false };

        Plotly.newPlot('graficoCrescimento', [trace1, trace2], layout, config);
    }

    async carregarReceitaMensal(mes = 'atual') {
        try {
            const hoje = new Date();
            let ano = hoje.getFullYear();
            let mesNum = hoje.getMonth() + 1;
            
            if (mes === 'anterior') {
                if (mesNum === 1) {
                    ano--;
                    mesNum = 12;
                } else {
                    mesNum--;
                }
            }
            
            const response = await fetch(`/analytics/api/receita-mensal?ano=${ano}&mes=${mesNum}`);
            const data = await response.json();
            
            if (data.success) {
                this.criarGraficoReceita(data.data, ano, mesNum);
            }
        } catch (error) {
            console.error('Erro ao carregar receita mensal:', error);
        }
    }

    criarGraficoReceita(dados, ano, mes) {
        const trace = {
            x: dados.map(d => d.profissional),
            y: dados.map(d => d.receita_total),
            type: 'bar',
            marker: { 
                color: dados.map(d => d.receita_total > 5000 ? '#28a745' : d.receita_total > 2000 ? '#ffc107' : '#dc3545'),
                opacity: 0.8
            },
            text: dados.map(d => `R$ ${d.receita_total.toLocaleString('pt-BR')}`),
            textposition: 'auto'
        };

        const layout = {
            title: `Receita Mensal - ${mes}/${ano}`,
            xaxis: { title: 'Profissional' },
            yaxis: { title: 'Receita (R$)' },
            margin: { l: 80, r: 20, t: 50, b: 100 }
        };

        const config = { responsive: true, displayModeBar: false };

        Plotly.newPlot('graficoReceita', [trace], layout, config);
    }

    async carregarInsights() {
        try {
            const response = await fetch('/analytics/api/insights');
            const data = await response.json();
            
            if (data.success) {
                this.exibirInsights(data.data);
            }
        } catch (error) {
            console.error('Erro ao carregar insights:', error);
        }
    }

    exibirInsights(insights) {
        const container = document.getElementById('insightsContainer');
        
        if (insights.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="bi bi-lightbulb fs-1"></i>
                    <p class="mt-2">Nenhum insight disponível no momento</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = insights.map(insight => `
            <div class="insight-card prioridade-${insight.prioridade} p-3 mb-3">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="mb-1">${insight.titulo}</h6>
                        <p class="mb-2 text-muted">${insight.descricao}</p>
                        <small class="text-muted">Criado em: ${insight.criado_em}</small>
                    </div>
                    <div class="ms-3">
                        <span class="badge bg-${this.getBadgeColor(insight.prioridade)}">${insight.prioridade}</span>
                        ${!insight.lido ? '<span class="badge bg-primary ms-1">Novo</span>' : ''}
                    </div>
                </div>
            </div>
        `).join('');
    }

    getBadgeColor(prioridade) {
        const colors = {
            'baixa': 'success',
            'normal': 'primary',
            'alta': 'warning',
            'critica': 'danger'
        };
        return colors[prioridade] || 'secondary';
    }

    async carregarPrevisoes() {
        // Por enquanto, apenas mostra mensagem de instrução
        // Em uma implementação completa, carregaria previsões reais
        const container = document.getElementById('previsoesContainer');
        container.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="bi bi-robot fs-1"></i>
                <p class="mt-2">Clique em "Treinar Modelo" para ativar as previsões de IA</p>
                <small>O sistema analisará o histórico de agendamentos para prever faltas</small>
            </div>
        `;
    }

    async gerarInsights() {
        try {
            const button = document.getElementById('btnGerarInsights');
            const originalText = button.innerHTML;
            
            button.disabled = true;
            button.innerHTML = '<i class="bi bi-arrow-clockwise spin"></i> Gerando...';
            
            const response = await fetch('/analytics/api/gerar-insights', { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess(`Insights gerados com sucesso! ${data.message}`);
                await this.carregarInsights();
            } else {
                this.showError(data.error || 'Erro ao gerar insights');
            }
        } catch (error) {
            console.error('Erro ao gerar insights:', error);
            this.showError('Erro ao gerar insights');
        } finally {
            const button = document.getElementById('btnGerarInsights');
            button.disabled = false;
            button.innerHTML = originalText;
        }
    }

    async treinarModelo() {
        try {
            const button = document.getElementById('btnTreinarModelo');
            const originalText = button.innerHTML;
            
            button.disabled = true;
            button.innerHTML = '<i class="bi bi-arrow-clockwise spin"></i> Treinando...';
            
            const response = await fetch('/analytics/api/treinar-modelo', { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('Modelo treinado com sucesso!');
                await this.carregarPrevisoes();
            } else {
                this.showError(data.error || 'Erro ao treinar modelo');
            }
        } catch (error) {
            console.error('Erro ao treinar modelo:', error);
            this.showError('Erro ao treinar modelo');
        } finally {
            const button = document.getElementById('btnTreinarModelo');
            button.disabled = false;
            button.innerHTML = originalText;
        }
    }

    startAutoRefresh() {
        // Atualizar métricas a cada 5 minutos
        setInterval(() => {
            this.carregarMetricasGerais();
        }, 5 * 60 * 1000);
    }

    showLoading() {
        // Implementar indicador de loading
        document.body.style.cursor = 'wait';
    }

    hideLoading() {
        document.body.style.cursor = 'default';
    }

    showSuccess(message) {
        // Usar SweetAlert2 ou toast do sistema
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

// Inicializar dashboard quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    new AnalyticsDashboard();
});

// Adicionar classe CSS para animação de rotação
const style = document.createElement('style');
style.textContent = `
    .spin {
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);
