/**
 * Analytics Relatórios - JavaScript
 * Sistema de relatórios avançados com exportação e agendamento
 */

class AnalyticsRelatorios {
    constructor() {
        this.currentView = 'rapidos';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.carregarHistoricoRelatorios();
    }

    setupEventListeners() {
        // Botões de navegação
        document.getElementById('btnRelatoriosRapidos').addEventListener('click', () => this.showView('rapidos'));
        document.getElementById('btnRelatoriosPersonalizados').addEventListener('click', () => this.showView('personalizados'));
        document.getElementById('btnAgendamento').addEventListener('click', () => this.showView('agendamento'));

        // Formulários
        document.getElementById('formRelatorioPersonalizado')?.addEventListener('submit', (e) => this.gerarRelatorioPersonalizado(e));
        document.getElementById('formAgendamentoRelatorio')?.addEventListener('click', (e) => this.agendarRelatorio(e));

        // Botões de ação
        document.getElementById('btnLimparFormulario')?.addEventListener('click', () => this.limparFormularioRelatorio());
        document.getElementById('btnLimparFormularioAgendamento')?.addEventListener('click', () => this.limparFormularioAgendamento());
    }

    showView(view) {
        this.currentView = view;
        
        // Atualizar botões ativos
        document.querySelectorAll('.btn-group .btn').forEach(btn => btn.classList.remove('active'));
        event.target.classList.add('active');
        
        // Ocultar todas as seções
        document.getElementById('relatoriosRapidos').style.display = 'none';
        document.getElementById('relatoriosPersonalizados').style.display = 'none';
        document.getElementById('agendamentoRelatorios').style.display = 'none';
        
        // Mostrar seção selecionada
        switch (view) {
            case 'rapidos':
                document.getElementById('relatoriosRapidos').style.display = 'block';
                break;
            case 'personalizados':
                document.getElementById('relatoriosPersonalizados').style.display = 'block';
                break;
            case 'agendamento':
                document.getElementById('agendamentoRelatorios').style.display = 'block';
                break;
        }
    }

    async gerarRelatorioRapido(tipo) {
        try {
            const button = event.target;
            const originalText = button.innerHTML;
            
            button.disabled = true;
            button.innerHTML = '<i class="bi bi-arrow-clockwise spin"></i> Gerando...';
            
            // Definir período padrão (últimos 30 dias)
            const hoje = new Date();
            const dataInicio = new Date();
            dataInicio.setDate(hoje.getDate() - 30);
            
            const data = {
                tipo: tipo,
                formato: 'pdf',
                data_inicio: dataInicio.toISOString().split('T')[0],
                data_fim: hoje.toISOString().split('T')[0]
            };
            
            const response = await fetch('/analytics/api/exportar-relatorio', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess(`Relatório ${tipo} gerado com sucesso!`);
                this.mostrarPreviewRelatorio(result.dados, tipo);
            } else {
                this.showError(result.error || 'Erro ao gerar relatório');
            }
            
        } catch (error) {
            console.error('Erro ao gerar relatório rápido:', error);
            this.showError('Erro ao gerar relatório');
        } finally {
            const button = event.target;
            button.disabled = false;
            button.innerHTML = originalText;
        }
    }

    async gerarRelatorioPersonalizado(event) {
        event.preventDefault();
        
        try {
            const formData = new FormData(event.target);
            const data = {
                tipo: document.getElementById('tipoRelatorio').value,
                formato: document.getElementById('formatoRelatorio').value,
                data_inicio: document.getElementById('dataInicioPersonalizado').value,
                data_fim: document.getElementById('dataFimPersonalizado').value,
                profissional: document.getElementById('filtroProfissional').value,
                especialidade: document.getElementById('filtroEspecialidade').value,
                observacoes: document.getElementById('observacoesRelatorio').value
            };
            
            const response = await fetch('/analytics/api/exportar-relatorio', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess('Relatório personalizado gerado com sucesso!');
                this.mostrarPreviewRelatorio(result.dados, data.tipo);
            } else {
                this.showError(result.error || 'Erro ao gerar relatório');
            }
            
        } catch (error) {
            console.error('Erro ao gerar relatório personalizado:', error);
            this.showError('Erro ao gerar relatório');
        }
    }

    async agendarRelatorio(event) {
        event.preventDefault();
        
        try {
            const data = {
                nome: document.getElementById('nomeRelatorioAgendado').value,
                tipo: document.getElementById('tipoAgendamento').value,
                frequencia: this.calcularFrequencia(),
                formato: document.getElementById('formatoAgendado').value,
                destinatarios: document.getElementById('emailsDestinatarios').value
            };
            
            // Aqui você implementaria a API para agendar relatórios
            // Por enquanto, apenas simula o sucesso
            this.showSuccess('Relatório agendado com sucesso!');
            this.limparFormularioAgendamento();
            this.carregarHistoricoRelatorios();
            
        } catch (error) {
            console.error('Erro ao agendar relatório:', error);
            this.showError('Erro ao agendar relatório');
        }
    }

    calcularFrequencia() {
        const tipo = document.getElementById('tipoAgendamento').value;
        const hora = document.getElementById('horaEnvio').value;
        
        switch (tipo) {
            case 'diario':
                return `0 ${hora.split(':')[1]} ${hora.split(':')[0]} * * *`;
            case 'semanal':
                const diaSemana = document.getElementById('diaSemana').value;
                return `0 ${hora.split(':')[1]} ${hora.split(':')[0]} * * ${diaSemana}`;
            case 'mensal':
                const diaMes = document.getElementById('diaMes').value;
                return `0 ${hora.split(':')[1]} ${hora.split(':')[0]} ${diaMes} * *`;
            default:
                return `0 ${hora.split(':')[1]} ${hora.split(':')[0]} * * *`;
        }
    }

    mostrarPreviewRelatorio(dados, tipo) {
        const modal = new bootstrap.Modal(document.getElementById('modalPreviewRelatorio'));
        const modalBody = document.getElementById('modalPreviewBody');
        
        let html = `<h6>Preview do Relatório: ${this.getTipoRelatorioNome(tipo)}</h6>`;
        
        switch (tipo) {
            case 'presenca':
                html += this.gerarPreviewPresenca(dados);
                break;
            case 'especialidade':
                html += this.gerarPreviewEspecialidade(dados);
                break;
            case 'receita':
                html += this.gerarPreviewReceita(dados);
                break;
            case 'crescimento':
                html += this.gerarPreviewCrescimento(dados);
                break;
            default:
                html += '<p>Preview não disponível para este tipo de relatório.</p>';
        }
        
        modalBody.innerHTML = html;
        modal.show();
    }

    gerarPreviewPresenca(dados) {
        let html = '<div class="table-responsive"><table class="table table-sm">';
        html += '<thead><tr><th>Data</th><th>Total</th><th>Realizados</th><th>Faltas</th><th>Taxa (%)</th></tr></thead><tbody>';
        
        dados.por_periodo.slice(0, 10).forEach(item => {
            html += `<tr>
                <td>${item.data}</td>
                <td>${item.total}</td>
                <td>${item.realizados}</td>
                <td>${item.faltas}</td>
                <td><span class="badge bg-${item.taxa_presenca >= 80 ? 'success' : item.taxa_presenca >= 60 ? 'warning' : 'danger'}">${item.taxa_presenca}%</span></td>
            </tr>`;
        });
        
        html += '</tbody></table></div>';
        return html;
    }

    gerarPreviewEspecialidade(dados) {
        let html = '<div class="table-responsive"><table class="table table-sm">';
        html += '<thead><tr><th>Especialidade</th><th>Total</th><th>Realizadas</th><th>Taxa (%)</th><th>Valor Médio</th></tr></thead><tbody>';
        
        dados.slice(0, 10).forEach(item => {
            html += `<tr>
                <td>${item.especialidade}</td>
                <td>${item.total_consultas}</td>
                <td>${item.realizadas}</td>
                <td><span class="badge bg-${item.taxa_realizacao >= 80 ? 'success' : item.taxa_realizacao >= 60 ? 'warning' : 'danger'}">${item.taxa_realizacao}%</span></td>
                <td>R$ ${item.valor_medio.toLocaleString('pt-BR')}</td>
            </tr>`;
        });
        
        html += '</tbody></table></div>';
        return html;
    }

    gerarPreviewReceita(dados) {
        let html = '<div class="table-responsive"><table class="table table-sm">';
        html += '<thead><tr><th>Profissional</th><th>Especialidade</th><th>Receita</th><th>Consultas</th></tr></thead><tbody>';
        
        dados.slice(0, 10).forEach(item => {
            html += `<tr>
                <td>${item.profissional}</td>
                <td>${item.especialidade}</td>
                <td><strong>R$ ${item.receita_total.toLocaleString('pt-BR')}</strong></td>
                <td>${item.consultas_realizadas}</td>
            </tr>`;
        });
        
        html += '</tbody></table></div>';
        return html;
    }

    gerarPreviewCrescimento(dados) {
        let html = '<div class="table-responsive"><table class="table table-sm">';
        html += '<thead><tr><th>Mês</th><th>Pacientes Ativos</th><th>Novos</th><th>Crescimento (%)</th></tr></thead><tbody>';
        
        dados.slice(0, 10).forEach(item => {
            const crescimentoClass = item.crescimento > 0 ? 'success' : item.crescimento < 0 ? 'danger' : 'secondary';
            html += `<tr>
                <td>${item.mes}</td>
                <td>${item.pacientes_ativos}</td>
                <td>${item.novos_pacientes}</td>
                <td><span class="badge bg-${crescimentoClass}">${item.crescimento > 0 ? '+' : ''}${item.crescimento}%</span></td>
            </tr>`;
        });
        
        html += '</tbody></table></div>';
        return html;
    }

    getTipoRelatorioNome(tipo) {
        const nomes = {
            'presenca': 'Taxa de Presença',
            'especialidade': 'Consultas por Especialidade',
            'receita': 'Receita Mensal',
            'crescimento': 'Crescimento de Pacientes'
        };
        return nomes[tipo] || tipo;
    }

    async carregarHistoricoRelatorios() {
        try {
            // Aqui você implementaria a API para carregar histórico
            // Por enquanto, mostra dados de exemplo
            const dados = [
                {
                    nome: 'Relatório Semanal de Presença',
                    tipo: 'semanal',
                    frequencia: 'Semanal',
                    ultimo_envio: '2024-01-15 08:00',
                    proximo_envio: '2024-01-22 08:00',
                    status: 'Ativo'
                }
            ];
            
            this.exibirHistoricoRelatorios(dados);
            
        } catch (error) {
            console.error('Erro ao carregar histórico:', error);
        }
    }

    exibirHistoricoRelatorios(dados) {
        const tbody = document.getElementById('historicoRelatorios');
        
        if (dados.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-muted py-4">
                        <i class="bi bi-inbox fs-1"></i>
                        <p class="mt-2">Nenhum relatório agendado encontrado</p>
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = dados.map(item => `
            <tr>
                <td>${item.nome}</td>
                <td>${item.tipo}</td>
                <td>${item.frequencia}</td>
                <td>${item.ultimo_envio}</td>
                <td>${item.proximo_envio}</td>
                <td><span class="badge bg-${item.status === 'Ativo' ? 'success' : 'secondary'}">${item.status}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="this.editarRelatorio('${item.nome}')">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="this.excluirRelatorio('${item.nome}')">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    limparFormularioRelatorio() {
        document.getElementById('formRelatorioPersonalizado').reset();
    }

    limparFormularioAgendamento() {
        document.getElementById('formAgendamentoRelatorio').reset();
        document.getElementById('horaEnvio').value = '08:00';
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
    new AnalyticsRelatorios();
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
