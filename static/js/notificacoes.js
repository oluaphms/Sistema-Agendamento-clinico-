/**
 * Sistema de Notificações - JavaScript
 * Gerencia notificações automáticas e integração WhatsApp
 */

class NotificacoesManager {
    constructor() {
        this.configuracoes = {};
        this.templates = {};
        this.historico = [];
        this.tarefas = [];
        this.paginaAtual = 1;
        this.registrosPorPagina = 20;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.carregarDadosIniciais();
        this.atualizarEstatisticas();
    }
    
    setupEventListeners() {
        // Formulário de configurações
        document.getElementById('configForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.salvarConfiguracoes();
        });
        
        // Filtros do histórico
        document.getElementById('filtroTipo')?.addEventListener('change', () => {
            this.filtrarHistorico();
        });
        
        document.getElementById('filtroStatus')?.addEventListener('change', () => {
            this.filtrarHistorico();
        });
        
        document.getElementById('dataInicio')?.addEventListener('change', () => {
            this.filtrarHistorico();
        });
        
        document.getElementById('dataFim')?.addEventListener('change', () => {
            this.filtrarHistorico();
        });
        
        // Seleção de template
        document.getElementById('tipoTemplate')?.addEventListener('change', () => {
            this.carregarTemplate();
        });
        
        // API Type
        document.getElementById('apiType')?.addEventListener('change', () => {
            this.atualizarCamposAPI();
        });
    }
    
    async carregarDadosIniciais() {
        try {
            this.showLoading();
            
            // Carregar configurações
            await this.carregarConfiguracoes();
            
            // Carregar templates
            await this.carregarTemplates();
            
            // Carregar histórico
            await this.carregarHistorico();
            
            // Carregar tarefas
            await this.carregarTarefas();
            
            this.hideLoading();
            
        } catch (error) {
            console.error('Erro ao carregar dados iniciais:', error);
            this.hideLoading();
            this.showToast('Erro ao carregar dados', 'error');
        }
    }
    
    async carregarConfiguracoes() {
        try {
            // TODO: Buscar configurações da API
            // Por enquanto, usar configurações padrão
            this.configuracoes = {
                api_type: 'simulacao',
                sistema_ativo: true,
                lembrete_24h: true,
                lembrete_1h: true,
                lembrete_adicional: true,
                resumo_diario: true,
                horario_lembrete_24h: '18:00',
                horario_resumo: '07:00',
                telefone_clinica: '+55 11 99999-9999',
                nome_clinica: 'Clínica Saúde Total',
                endereco_clinica: 'Rua das Clínicas, 123 - Centro'
            };
            
            this.aplicarConfiguracoes();
            
        } catch (error) {
            console.error('Erro ao carregar configurações:', error);
        }
    }
    
    aplicarConfiguracoes() {
        try {
            // Aplicar valores nos campos
            document.getElementById('apiType').value = this.configuracoes.api_type;
            document.getElementById('sistemaAtivo').checked = this.configuracoes.sistema_ativo;
            document.getElementById('lembrete24h').checked = this.configuracoes.lembrete_24h;
            document.getElementById('lembrete1h').checked = this.configuracoes.lembrete_1h;
            document.getElementById('lembreteAdicional').checked = this.configuracoes.lembrete_adicional;
            document.getElementById('resumoDiario').checked = this.configuracoes.resumo_diario;
            document.getElementById('horarioLembrete24h').value = this.configuracoes.horario_lembrete_24h;
            document.getElementById('horarioResumo').value = this.configuracoes.horario_resumo;
            document.getElementById('telefoneClinica').value = this.configuracoes.telefone_clinica;
            document.getElementById('nomeClinica').value = this.configuracoes.nome_clinica;
            document.getElementById('enderecoClinica').value = this.configuracoes.endereco_clinica;
            
            // Atualizar campos da API
            this.atualizarCamposAPI();
            
        } catch (error) {
            console.error('Erro ao aplicar configurações:', error);
        }
    }
    
    atualizarCamposAPI() {
        try {
            const apiType = document.getElementById('apiType').value;
            const camposTwilio = document.querySelectorAll('[data-api="twilio"]');
            const camposWhatsAppWeb = document.querySelectorAll('[data-api="whatsapp_web"]');
            
            // Mostrar/ocultar campos baseado no tipo de API
            camposTwilio.forEach(campo => {
                campo.style.display = apiType === 'twilio' ? 'block' : 'none';
            });
            
            camposWhatsAppWeb.forEach(campo => {
                campo.style.display = apiType === 'whatsapp_web' ? 'block' : 'none';
            });
            
        } catch (error) {
            console.error('Erro ao atualizar campos da API:', error);
        }
    }
    
    async carregarTemplates() {
        try {
            // TODO: Buscar templates da API
            // Por enquanto, usar templates padrão
            this.templates = {
                confirmacao_agendamento: {
                    ativo: true,
                    conteudo: `🎉 *Agendamento Confirmado!*

Olá {nome_paciente}! 

Sua consulta foi agendada com sucesso:
📅 Data: {data}
🕐 Horário: {horario}
👨‍⚕️ Profissional: {profissional}
🏥 Especialidade: {especialidade}

📍 Local: {endereco_clinica}

Para confirmar sua presença, responda:
✅ SIM - Confirmo presença
🔄 REAGENDAR - Quero outro horário
❌ CANCELAR - Cancelar consulta

Qualquer dúvida, entre em contato: {telefone_clinica}

Agradecemos a confiança! 🙏`
                }
            };
            
            // Carregar primeiro template
            this.carregarTemplate();
            
        } catch (error) {
            console.error('Erro ao carregar templates:', error);
        }
    }
    
    carregarTemplate() {
        try {
            const tipoTemplate = document.getElementById('tipoTemplate').value;
            const template = this.templates[tipoTemplate];
            
            if (template) {
                document.getElementById('conteudoTemplate').value = template.conteudo;
                document.getElementById('templateAtivo').checked = template.ativo;
            } else {
                document.getElementById('conteudoTemplate').value = 'Template não encontrado';
                document.getElementById('templateAtivo').checked = false;
            }
            
        } catch (error) {
            console.error('Erro ao carregar template:', error);
        }
    }
    
    async carregarHistorico() {
        try {
            // TODO: Buscar histórico da API
            // Por enquanto, usar dados mock
            this.historico = [
                {
                    id: 'notif_001',
                    data_hora: '2025-01-19 10:30:00',
                    tipo: 'confirmacao_agendamento',
                    destinatario: '+55 11 99999-9999',
                    status: 'enviada',
                    resposta: 'SIM'
                },
                {
                    id: 'notif_002',
                    data_hora: '2025-01-19 09:15:00',
                    tipo: 'lembrete_24h',
                    destinatario: '+55 11 88888-8888',
                    status: 'entregue',
                    resposta: 'REAGENDAR'
                }
            ];
            
            this.renderizarHistorico();
            
        } catch (error) {
            console.error('Erro ao carregar histórico:', error);
        }
    }
    
    async carregarTarefas() {
        try {
            // TODO: Buscar tarefas da API
            // Por enquanto, usar dados mock
            this.tarefas = [
                {
                    id: 'tarefa_001',
                    nome: 'Lembrete 24h - Agendamento 123',
                    tipo: 'lembrete_24h',
                    proxima_execucao: '2025-01-20 18:00:00',
                    status: 'agendada',
                    tentativas: 0
                }
            ];
            
            this.renderizarTarefas();
            
        } catch (error) {
            console.error('Erro ao carregar tarefas:', error);
        }
    }
    
    renderizarHistorico() {
        try {
            const tbody = document.getElementById('corpoHistorico');
            if (!tbody) return;
            
            const inicio = (this.paginaAtual - 1) * this.registrosPorPagina;
            const fim = inicio + this.registrosPorPagina;
            const registrosPagina = this.historico.slice(inicio, fim);
            
            tbody.innerHTML = registrosPagina.map(registro => `
                <tr>
                    <td>${this.formatarDataHora(registro.data_hora)}</td>
                    <td>
                        <span class="badge bg-primary">${this.formatarTipo(registro.tipo)}</span>
                    </td>
                    <td>${registro.destinatario}</td>
                    <td>
                        <span class="badge bg-${this.getStatusColor(registro.status)}">
                            ${this.formatarStatus(registro.status)}
                        </span>
                    </td>
                    <td>${registro.resposta || '-'}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-info" onclick="verDetalhesNotificacao('${registro.id}')">
                            <i class="bi bi-eye"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
            
            // Atualizar contador
            document.getElementById('totalRegistros').textContent = this.historico.length;
            
            // Renderizar paginação
            this.renderizarPaginacao();
            
        } catch (error) {
            console.error('Erro ao renderizar histórico:', error);
        }
    }
    
    renderizarTarefas() {
        try {
            const tbody = document.getElementById('corpoTarefas');
            if (!tbody) return;
            
            tbody.innerHTML = this.tarefas.map(tarefa => `
                <tr>
                    <td>${tarefa.nome}</td>
                    <td>
                        <span class="badge bg-info">${this.formatarTipo(tarefa.tipo)}</span>
                    </td>
                    <td>${this.formatarDataHora(tarefa.proxima_execucao)}</td>
                    <td>
                        <span class="badge bg-${this.getStatusColor(tarefa.status)}">
                            ${this.formatarStatus(tarefa.status)}
                        </span>
                    </td>
                    <td>${tarefa.tentativas}</td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-warning" onclick="cancelarTarefa('${tarefa.id}')">
                                <i class="bi bi-pause"></i>
                            </button>
                            <button class="btn btn-outline-danger" onclick="excluirTarefa('${tarefa.id}')">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');
            
        } catch (error) {
            console.error('Erro ao renderizar tarefas:', error);
        }
    }
    
    renderizarPaginacao() {
        try {
            const totalPaginas = Math.ceil(this.historico.length / this.registrosPorPagina);
            const paginacao = document.getElementById('paginacaoHistorico');
            
            if (!paginacao || totalPaginas <= 1) return;
            
            let html = '';
            
            // Botão anterior
            if (this.paginaAtual > 1) {
                html += `
                    <li class="page-item">
                        <a class="page-link" href="#" onclick="mudarPagina(${this.paginaAtual - 1})">
                            <i class="bi bi-chevron-left"></i>
                        </a>
                    </li>
                `;
            }
            
            // Páginas
            for (let i = 1; i <= totalPaginas; i++) {
                if (i === this.paginaAtual) {
                    html += `
                        <li class="page-item active">
                            <span class="page-link">${i}</span>
                        </li>
                    `;
                } else {
                    html += `
                        <li class="page-item">
                            <a class="page-link" href="#" onclick="mudarPagina(${i})">${i}</a>
                        </li>
                    `;
                }
            }
            
            // Botão próximo
            if (this.paginaAtual < totalPaginas) {
                html += `
                    <li class="page-item">
                        <a class="page-link" href="#" onclick="mudarPagina(${this.paginaAtual + 1})">
                            <i class="bi bi-chevron-right"></i>
                        </a>
                    </li>
                `;
            }
            
            paginacao.innerHTML = html;
            
        } catch (error) {
            console.error('Erro ao renderizar paginação:', error);
        }
    }
    
    async salvarConfiguracoes() {
        try {
            this.showLoading();
            
            // Coletar dados do formulário
            const config = {
                api_type: document.getElementById('apiType').value,
                sistema_ativo: document.getElementById('sistemaAtivo').checked,
                lembrete_24h: document.getElementById('lembrete24h').checked,
                lembrete_1h: document.getElementById('lembrete1h').checked,
                lembrete_adicional: document.getElementById('lembreteAdicional').checked,
                resumo_diario: document.getElementById('resumoDiario').checked,
                horario_lembrete_24h: document.getElementById('horarioLembrete24h').value,
                horario_resumo: document.getElementById('horarioResumo').value,
                telefone_clinica: document.getElementById('telefoneClinica').value,
                nome_clinica: document.getElementById('nomeClinica').value,
                endereco_clinica: document.getElementById('enderecoClinica').value
            };
            
            // TODO: Salvar na API
            this.configuracoes = config;
            
            this.hideLoading();
            this.showToast('Configurações salvas com sucesso!', 'success');
            
        } catch (error) {
            console.error('Erro ao salvar configurações:', error);
            this.hideLoading();
            this.showToast('Erro ao salvar configurações', 'error');
        }
    }
    
    async salvarTemplate() {
        try {
            const tipoTemplate = document.getElementById('tipoTemplate').value;
            const conteudo = document.getElementById('conteudoTemplate').value;
            const ativo = document.getElementById('templateAtivo').checked;
            
            // TODO: Salvar template na API
            this.templates[tipoTemplate] = {
                ativo: ativo,
                conteudo: conteudo
            };
            
            this.showToast('Template salvo com sucesso!', 'success');
            
        } catch (error) {
            console.error('Erro ao salvar template:', error);
            this.showToast('Erro ao salvar template', 'error');
        }
    }
    
    async testarConectividade() {
        try {
            this.showLoading();
            
            // TODO: Testar conectividade via API
            await new Promise(resolve => setTimeout(resolve, 2000)); // Simular teste
            
            this.hideLoading();
            
            Swal.fire({
                title: 'Teste de Conectividade',
                html: `
                    <div class="text-start">
                        <div class="mb-2">
                            <strong>Twilio:</strong> 
                            <span class="badge bg-success">Conectado</span>
                        </div>
                        <div class="mb-2">
                            <strong>WhatsApp Web:</strong> 
                            <span class="badge bg-warning">Não configurado</span>
                        </div>
                        <div class="mb-2">
                            <strong>Simulação:</strong> 
                            <span class="badge bg-info">Ativo</span>
                        </div>
                    </div>
                `,
                icon: 'success',
                confirmButtonText: 'OK'
            });
            
        } catch (error) {
            console.error('Erro no teste de conectividade:', error);
            this.hideLoading();
            this.showToast('Erro no teste de conectividade', 'error');
        }
    }
    
    async testarTemplate() {
        try {
            const tipoTemplate = document.getElementById('tipoTemplate').value;
            const template = this.templates[tipoTemplate];
            
            if (!template) {
                this.showToast('Template não encontrado', 'error');
                return;
            }
            
            // Preparar dados de teste
            const dadosTeste = {
                nome_paciente: 'João Silva',
                data: '20/01/2025',
                horario: '14:00',
                profissional: 'Dr. Carlos',
                especialidade: 'Clínico Geral',
                endereco_clinica: this.configuracoes.endereco_clinica,
                telefone_clinica: this.configuracoes.telefone_clinica
            };
            
            // Formatar mensagem
            let mensagem = template.conteudo;
            Object.entries(dadosTeste).forEach(([chave, valor]) => {
                mensagem = mensagem.replace(new RegExp(`{${chave}}`, 'g'), valor);
            });
            
            // Mostrar modal de teste
            document.getElementById('dadosTeste').value = JSON.stringify(dadosTeste, null, 2);
            
            const modal = new bootstrap.Modal(document.getElementById('modalTesteTemplate'));
            modal.show();
            
        } catch (error) {
            console.error('Erro ao testar template:', error);
            this.showToast('Erro ao testar template', 'error');
        }
    }
    
    async enviarTeste() {
        try {
            const telefone = document.getElementById('telefoneTeste').value;
            const tipoTemplate = document.getElementById('tipoTemplate').value;
            
            if (!telefone) {
                this.showToast('Informe o telefone de teste', 'error');
                return;
            }
            
            // TODO: Enviar teste via API
            await new Promise(resolve => setTimeout(resolve, 2000)); // Simular envio
            
            // Fechar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalTesteTemplate'));
            modal.hide();
            
            this.showToast('Teste enviado com sucesso!', 'success');
            
        } catch (error) {
            console.error('Erro ao enviar teste:', error);
            this.showToast('Erro ao enviar teste', 'error');
        }
    }
    
    async filtrarHistorico() {
        try {
            const tipo = document.getElementById('filtroTipo').value;
            const status = document.getElementById('filtroStatus').value;
            const dataInicio = document.getElementById('dataInicio').value;
            const dataFim = document.getElementById('dataFim').value;
            
            // TODO: Aplicar filtros na API
            // Por enquanto, apenas recarregar
            await this.carregarHistorico();
            
        } catch (error) {
            console.error('Erro ao filtrar histórico:', error);
        }
    }
    
    async exportarHistorico() {
        try {
            // TODO: Exportar histórico via API
            this.showToast('Exportação iniciada!', 'info');
            
        } catch (error) {
            console.error('Erro ao exportar histórico:', error);
            this.showToast('Erro ao exportar histórico', 'error');
        }
    }
    
    async limparHistorico() {
        try {
            const result = await Swal.fire({
                title: 'Limpar Histórico',
                text: 'Tem certeza que deseja limpar todo o histórico de notificações?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Sim, limpar',
                cancelButtonText: 'Cancelar'
            });
            
            if (result.isConfirmed) {
                // TODO: Limpar histórico via API
                this.historico = [];
                this.renderizarHistorico();
                this.showToast('Histórico limpo com sucesso!', 'success');
            }
            
        } catch (error) {
            console.error('Erro ao limpar histórico:', error);
            this.showToast('Erro ao limpar histórico', 'error');
        }
    }
    
    async atualizarTarefas() {
        try {
            await this.carregarTarefas();
            this.showToast('Tarefas atualizadas!', 'success');
            
        } catch (error) {
            console.error('Erro ao atualizar tarefas:', error);
            this.showToast('Erro ao atualizar tarefas', 'error');
        }
    }
    
    async iniciarAgendador() {
        try {
            // TODO: Iniciar agendador via API
            this.showToast('Agendador iniciado!', 'success');
            
        } catch (error) {
            console.error('Erro ao iniciar agendador:', error);
            this.showToast('Erro ao iniciar agendador', 'error');
        }
    }
    
    async pararAgendador() {
        try {
            // TODO: Parar agendador via API
            this.showToast('Agendador parado!', 'success');
            
        } catch (error) {
            console.error('Erro ao parar agendador:', error);
            this.showToast('Erro ao parar agendador', 'error');
        }
    }
    
    async atualizarEstatisticas() {
        try {
            // TODO: Buscar estatísticas da API
            // Por enquanto, usar dados mock
            const estatisticas = {
                total_enviadas: 150,
                taxa_entrega: 94.7,
                total_respostas: 89,
                tarefas_ativas: 5
            };
            
            // Atualizar cards
            document.getElementById('totalEnviadas').textContent = estatisticas.total_enviadas;
            document.getElementById('taxaEntrega').textContent = `${estatisticas.taxa_entrega}%`;
            document.getElementById('totalRespostas').textContent = estatisticas.total_respostas;
            document.getElementById('tarefasAtivas').textContent = estatisticas.tarefas_ativas;
            
        } catch (error) {
            console.error('Erro ao atualizar estatísticas:', error);
        }
    }
    
    // Funções auxiliares
    formatarDataHora(dataHora) {
        try {
            if (!dataHora) return '-';
            const data = new Date(dataHora);
            return data.toLocaleString('pt-BR');
        } catch (error) {
            return dataHora;
        }
    }
    
    formatarTipo(tipo) {
        const tipos = {
            'confirmacao_agendamento': 'Confirmação',
            'lembrete_24h': 'Lembrete 24h',
            'lembrete_1h': 'Lembrete 1h',
            'agradecimento': 'Agradecimento',
            'lembrete_adicional': 'Lembrete Adicional',
            'sugestao_reagendamento': 'Sugestão Reagendamento',
            'resumo_diario': 'Resumo Diário'
        };
        return tipos[tipo] || tipo;
    }
    
    formatarStatus(status) {
        const statusMap = {
            'enviada': 'Enviada',
            'entregue': 'Entregue',
            'falhou': 'Falhou',
            'pendente': 'Pendente',
            'cancelada': 'Cancelada'
        };
        return statusMap[status] || status;
    }
    
    getStatusColor(status) {
        const cores = {
            'enviada': 'info',
            'entregue': 'success',
            'falhou': 'danger',
            'pendente': 'warning',
            'cancelada': 'secondary'
        };
        return cores[status] || 'secondary';
    }
    
    showLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) overlay.classList.remove('d-none');
    }
    
    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) overlay.classList.add('d-none');
    }
    
    showToast(message, type = 'success') {
        if (window.showToast) {
            window.showToast(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
}

// Funções globais
let notificacoesManager;

document.addEventListener('DOMContentLoaded', function() {
    notificacoesManager = new NotificacoesManager();
});

// Funções para uso externo
function testarConectividade() {
    if (notificacoesManager) {
        notificacoesManager.testarConectividade();
    }
}

function showQuickActions() {
    Swal.fire({
        title: 'Ações Rápidas',
        html: `
            <div class="row g-3">
                <div class="col-6">
                    <button class="btn btn-primary w-100 py-3" onclick="testarConectividade()">
                        <i class="bi bi-wifi fs-4 d-block mb-2"></i>
                        <strong>Testar Conexão</strong>
                    </button>
                </div>
                <div class="col-6">
                    <button class="btn btn-success w-100 py-3" onclick="notificacoesManager?.atualizarEstatisticas()">
                        <i class="bi bi-arrow-clockwise fs-4 d-block mb-2"></i>
                        <strong>Atualizar Dados</strong>
                    </button>
                </div>
                <div class="col-6">
                    <button class="btn btn-info w-100 py-3" onclick="notificacoesManager?.carregarDadosIniciais()">
                        <i class="bi bi-arrow-clockwise fs-4 d-block mb-2"></i>
                        <strong>Recarregar Tudo</strong>
                    </button>
                </div>
                <div class="col-6">
                    <button class="btn btn-warning w-100 py-3" onclick="notificacoesManager?.limparHistorico()">
                        <i class="bi bi-trash fs-4 d-block mb-2"></i>
                        <strong>Limpar Histórico</strong>
                    </button>
                </div>
            </div>
        `,
        showConfirmButton: false,
        showCloseButton: true,
        width: '600px'
    });
}

function editarTemplate() {
    const textarea = document.getElementById('conteudoTemplate');
    if (textarea) {
        textarea.readOnly = false;
        textarea.focus();
        this.showToast('Template em modo de edição', 'info');
    }
}

function salvarTemplate() {
    if (notificacoesManager) {
        notificacoesManager.salvarTemplate();
    }
}

function restaurarTemplate() {
    if (notificacoesManager) {
        notificacoesManager.carregarTemplate();
        this.showToast('Template restaurado', 'info');
    }
}

function testarTemplate() {
    if (notificacoesManager) {
        notificacoesManager.testarTemplate();
    }
}

function enviarTeste() {
    if (notificacoesManager) {
        notificacoesManager.enviarTeste();
    }
}

function carregarConfiguracoes() {
    if (notificacoesManager) {
        notificacoesManager.carregarConfiguracoes();
    }
}

function filtrarHistorico() {
    if (notificacoesManager) {
        notificacoesManager.filtrarHistorico();
    }
}

function exportarHistorico() {
    if (notificacoesManager) {
        notificacoesManager.exportarHistorico();
    }
}

function limparHistorico() {
    if (notificacoesManager) {
        notificacoesManager.limparHistorico();
    }
}

function atualizarTarefas() {
    if (notificacoesManager) {
        notificacoesManager.atualizarTarefas();
    }
}

function iniciarAgendador() {
    if (notificacoesManager) {
        notificacoesManager.iniciarAgendador();
    }
}

function pararAgendador() {
    if (notificacoesManager) {
        notificacoesManager.pararAgendador();
    }
}

function mudarPagina(pagina) {
    if (notificacoesManager) {
        notificacoesManager.paginaAtual = pagina;
        notificacoesManager.renderizarHistorico();
    }
}

function verDetalhesNotificacao(id) {
    // TODO: Implementar visualização de detalhes
    Swal.fire({
        title: 'Detalhes da Notificação',
        text: `ID: ${id}`,
        icon: 'info'
    });
}

function cancelarTarefa(id) {
    // TODO: Implementar cancelamento de tarefa
    Swal.fire({
        title: 'Cancelar Tarefa',
        text: 'Tem certeza que deseja cancelar esta tarefa?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sim, cancelar',
        cancelButtonText: 'Não'
    });
}

function excluirTarefa(id) {
    // TODO: Implementar exclusão de tarefa
    Swal.fire({
        title: 'Excluir Tarefa',
        text: 'Tem certeza que deseja excluir esta tarefa?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sim, excluir',
        cancelButtonText: 'Não'
    });
}

// Funções de webhook (a serem implementadas)
function salvarWebhook() {
    // TODO: Implementar salvamento de webhook
    this.showToast('Webhook salvo com sucesso!', 'success');
}

function testarWebhook() {
    // TODO: Implementar teste de webhook
    this.showToast('Teste de webhook iniciado!', 'info');
}

function verLogsWebhook() {
    // TODO: Implementar visualização de logs
    this.showToast('Logs de webhook carregados!', 'info');
}

function gerarToken() {
    // TODO: Implementar geração de token
    const token = Math.random().toString(36).substring(2) + Date.now().toString(36);
    document.getElementById('webhookToken').value = token;
    this.showToast('Token gerado com sucesso!', 'success');
}

function copiarUrlTeste() {
    // TODO: Implementar cópia de URL
    this.showToast('URL copiada para clipboard!', 'success');
}
