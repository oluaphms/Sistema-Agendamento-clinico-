// Configurações do Sistema - JavaScript
class ConfiguracoesSistema {
    constructor() {
        this.configuracoes = {};
        this.init();
    }

    init() {
        this.carregarConfiguracoes();
        this.setupEventListeners();
        this.verificarStatusSistema();
    }

    setupEventListeners() {
        // Formulários
        document.getElementById('configGeralForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.salvarConfiguracoesGerais();
        });

        document.getElementById('configClinicaForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.salvarDadosClinica();
        });



        document.getElementById('configBackupForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.salvarConfiguracoesBackup();
        });

        // Mudanças de tema
        document.getElementById('temaSistema')?.addEventListener('change', (e) => {
            this.aplicarTema(e.target.value);
        });

        // Mudanças de idioma
        document.getElementById('idiomaSistema')?.addEventListener('change', (e) => {
            this.aplicarIdioma(e.target.value);
        });
    }

    async carregarConfiguracoes() {
        try {
            this.showLoading();
            
            // Simular carregamento de configurações do servidor
            const response = await fetch('/api/configuracoes');
            if (response.ok) {
                this.configuracoes = await response.json();
            } else {
                // Carregar configurações padrão se não houver resposta
                this.configuracoes = this.getConfiguracoesPadrao();
            }

            this.aplicarConfiguracoes();
            this.hideLoading();
            
        } catch (error) {
            console.error('Erro ao carregar configurações:', error);
            this.configuracoes = this.getConfiguracoesPadrao();
            this.aplicarConfiguracoes();
            this.hideLoading();
        }
    }

    getConfiguracoesPadrao() {
        return {
            geral: {
                modo: 'desenvolvimento',
                idioma: 'pt-br',
                fusoHorario: 'America/Sao_Paulo',
                formatoData: 'dd/mm/yyyy',
                tema: 'auto',
                tamanhoFonte: 'medium',
                tempoSessao: 8,
                nivelLog: 'warning'
            },
            clinica: {
                nome: 'Clínica Saúde Total',
                cnpj: '',
                telefone: '+55 11 99999-9999',
                email: '',
                endereco: 'Rua das Clínicas, 123 - Centro',
                cidade: 'São Paulo',
                estado: 'SP',
                cep: '',
                horarioAbertura: '08:00',
                horarioFechamento: '18:00',
                diasFuncionamento: ['segunda', 'terca', 'quarta', 'quinta', 'sexta']
            },

            backup: {
                frequencia: 'diario',
                horario: '02:00',
                retencao: 30,
                compressao: true,
                backupNuvem: false,
                notificacao: true
            }
        };
    }

    aplicarConfiguracoes() {
        // Aplicar configurações gerais
        this.aplicarConfiguracao('modoSistema', this.configuracoes.geral?.modo);
        this.aplicarConfiguracao('idiomaSistema', this.configuracoes.geral?.idioma);
        this.aplicarConfiguracao('fusoHorario', this.configuracoes.geral?.fusoHorario);
        this.aplicarConfiguracao('formatoData', this.configuracoes.geral?.formatoData);
        this.aplicarConfiguracao('temaSistema', this.configuracoes.geral?.tema);
        this.aplicarConfiguracao('tamanhoFonte', this.configuracoes.geral?.tamanhoFonte);
        this.aplicarConfiguracao('tempoSessao', this.configuracoes.geral?.tempoSessao);
        this.aplicarConfiguracao('nivelLog', this.configuracoes.geral?.nivelLog);

        // Aplicar configurações da clínica
        this.aplicarConfiguracao('nomeClinica', this.configuracoes.clinica?.nome);
        this.aplicarConfiguracao('cnpjClinica', this.configuracoes.clinica?.cnpj);
        this.aplicarConfiguracao('telefoneClinica', this.configuracoes.clinica?.telefone);
        this.aplicarConfiguracao('emailClinica', this.configuracoes.clinica?.email);
        this.aplicarConfiguracao('enderecoClinica', this.configuracoes.clinica?.endereco);
        this.aplicarConfiguracao('cidadeClinica', this.configuracoes.clinica?.cidade);
        this.aplicarConfiguracao('estadoClinica', this.configuracoes.clinica?.estado);
        this.aplicarConfiguracao('cepClinica', this.configuracoes.clinica?.cep);
        this.aplicarConfiguracao('horarioAbertura', this.configuracoes.clinica?.horarioAbertura);
        this.aplicarConfiguracao('horarioFechamento', this.configuracoes.clinica?.horarioFechamento);

        // Aplicar dias de funcionamento
        if (this.configuracoes.clinica?.diasFuncionamento) {
            this.configuracoes.clinica.diasFuncionamento.forEach(dia => {
                const checkbox = document.getElementById(dia);
                if (checkbox) checkbox.checked = true;
            });
        }



        // Aplicar configurações de backup
        this.aplicarConfiguracao('frequenciaBackup', this.configuracoes.backup?.frequencia);
        this.aplicarConfiguracao('horarioBackup', this.configuracoes.backup?.horario);
        this.aplicarConfiguracao('retencaoBackup', this.configuracoes.backup?.retencao);
        this.aplicarConfiguracao('compressaoBackup', this.configuracoes.backup?.compressao);
        this.aplicarConfiguracao('backupNuvem', this.configuracoes.backup?.backupNuvem);
        this.aplicarConfiguracao('notificacaoBackup', this.configuracoes.backup?.notificacao);
    }

    aplicarConfiguracao(elementId, valor) {
        const element = document.getElementById(elementId);
        if (!element) return;

        if (element.type === 'checkbox') {
            element.checked = Boolean(valor);
        } else if (element.type === 'number') {
            element.value = valor || 0;
        } else {
            element.value = valor || '';
        }
    }

    async salvarConfiguracoesGerais() {
        try {
            this.showLoading();
            
            const configGerais = {
                modo: document.getElementById('modoSistema').value,
                idioma: document.getElementById('idiomaSistema').value,
                fusoHorario: document.getElementById('fusoHorario').value,
                formatoData: document.getElementById('formatoData').value,
                tema: document.getElementById('temaSistema').value,
                tamanhoFonte: document.getElementById('tamanhoFonte').value,
                tempoSessao: parseInt(document.getElementById('tempoSessao').value),
                nivelLog: document.getElementById('nivelLog').value
            };

            // Salvar no servidor
            const response = await fetch('/api/configuracoes/geral', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(configGerais)
            });

            if (response.ok) {
                this.configuracoes.geral = configGerais;
                this.mostrarSucesso('Configurações gerais salvas com sucesso!');
                this.aplicarTema(configGerais.tema);
                this.aplicarIdioma(configGerais.idioma);
            } else {
                throw new Error('Erro ao salvar configurações');
            }

        } catch (error) {
            console.error('Erro ao salvar configurações gerais:', error);
            this.mostrarErro('Erro ao salvar configurações gerais');
        } finally {
            this.hideLoading();
        }
    }

    async salvarDadosClinica() {
        try {
            this.showLoading();
            
            const diasFuncionamento = [];
            ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo'].forEach(dia => {
                if (document.getElementById(dia)?.checked) {
                    diasFuncionamento.push(dia);
                }
            });

            const dadosClinica = {
                nome: document.getElementById('nomeClinica').value,
                cnpj: document.getElementById('cnpjClinica').value,
                telefone: document.getElementById('telefoneClinica').value,
                email: document.getElementById('emailClinica').value,
                endereco: document.getElementById('enderecoClinica').value,
                cidade: document.getElementById('cidadeClinica').value,
                estado: document.getElementById('estadoClinica').value,
                cep: document.getElementById('cepClinica').value,
                horarioAbertura: document.getElementById('horarioAbertura').value,
                horarioFechamento: document.getElementById('horarioFechamento').value,
                diasFuncionamento: diasFuncionamento
            };

            // Salvar no servidor
            const response = await fetch('/api/configuracoes/clinica', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dadosClinica)
            });

            if (response.ok) {
                this.configuracoes.clinica = dadosClinica;
                this.mostrarSucesso('Dados da clínica salvos com sucesso!');
            } else {
                throw new Error('Erro ao salvar dados da clínica');
            }

        } catch (error) {
            console.error('Erro ao salvar dados da clínica:', error);
            this.mostrarErro('Erro ao salvar dados da clínica');
        } finally {
            this.hideLoading();
        }
    }



    async salvarConfiguracoesBackup() {
        try {
            this.showLoading();
            
            const configBackup = {
                frequencia: document.getElementById('frequenciaBackup').value,
                horario: document.getElementById('horarioBackup').value,
                retencao: parseInt(document.getElementById('retencaoBackup').value),
                compressao: document.getElementById('compressaoBackup').checked,
                backupNuvem: document.getElementById('backupNuvem').checked,
                notificacao: document.getElementById('notificacaoBackup').checked
            };

            // Salvar no servidor
            const response = await fetch('/api/configuracoes/backup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(configBackup)
            });

            if (response.ok) {
                this.configuracoes.backup = configBackup;
                this.mostrarSucesso('Configurações de backup salvas com sucesso!');
            } else {
                throw new Error('Erro ao salvar configurações de backup');
            }

        } catch (error) {
            console.error('Erro ao salvar configurações de backup:', error);
            this.mostrarErro('Erro ao salvar configurações de backup');
        } finally {
            this.hideLoading();
        }
    }

    aplicarTema(tema) {
        if (tema === 'auto') {
            // Detectar tema do sistema
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            document.documentElement.setAttribute('data-bs-theme', prefersDark ? 'dark' : 'light');
        } else {
            document.documentElement.setAttribute('data-bs-theme', tema);
        }
        
        // Salvar preferência no localStorage
        localStorage.setItem('tema', tema);
    }

    aplicarIdioma(idioma) {
        // Implementar mudança de idioma
        console.log('Aplicando idioma:', idioma);
        // Aqui você pode implementar a lógica de internacionalização
    }

    async verificarStatusSistema() {
        try {
            // Verificar status do banco de dados
            const statusBanco = await this.verificarBancoDados();
            const statusBancoElement = document.getElementById('statusBanco');
            if (statusBancoElement) {
                statusBancoElement.textContent = statusBanco;
                statusBancoElement.className = `badge ${statusBanco === 'OK' ? 'bg-success' : 'bg-danger'}`;
            }

            // Verificar integrações
            const integracoes = await this.verificarIntegracoes();
            const statusIntegracoesElement = document.getElementById('statusIntegracoes');
            if (statusIntegracoesElement) {
                statusIntegracoesElement.textContent = integracoes;
            }

            // Verificar backup
            const backup = await this.verificarBackup();
            const statusBackupElement = document.getElementById('statusBackup');
            if (statusBackupElement) {
                statusBackupElement.textContent = backup;
            }

        } catch (error) {
            console.error('Erro ao verificar status do sistema:', error);
        }
    }

    async verificarBancoDados() {
        try {
            const response = await fetch('/api/sistema/status-banco');
            if (response.ok) {
                return 'OK';
            } else {
                return 'Erro';
            }
        } catch (error) {
            return 'Erro';
        }
    }

    async verificarIntegracoes() {
        try {
            const response = await fetch('/api/sistema/status-integracoes');
            if (response.ok) {
                const data = await response.json();
                return `${data.ativas}/${data.total}`;
            } else {
                return '0/0';
            }
        } catch (error) {
            return '0/0';
        }
    }

    async verificarBackup() {
        try {
            const response = await fetch('/api/sistema/status-backup');
            if (response.ok) {
                const data = await response.json();
                return data.ultimoBackup || 'Nunca';
            } else {
                return 'Erro';
            }
        } catch (error) {
            return 'Erro';
        }
    }



    // Funções de sistema
    async verificarSistema() {
        try {
            this.showLoading();
            const response = await fetch('/api/sistema/verificar');
            if (response.ok) {
                const data = await response.json();
                this.mostrarSucesso(`Sistema verificado: ${data.status}`);
                this.verificarStatusSistema();
            } else {
                this.mostrarErro('Erro ao verificar sistema');
            }
        } catch (error) {
            this.mostrarErro('Erro ao verificar sistema');
        } finally {
            this.hideLoading();
        }
    }

    async limparCache() {
        try {
            this.showLoading();
            const response = await fetch('/api/sistema/limpar-cache');
            if (response.ok) {
                this.mostrarSucesso('Cache limpo com sucesso!');
            } else {
                this.mostrarErro('Erro ao limpar cache');
            }
        } catch (error) {
            this.mostrarErro('Erro ao limpar cache');
        } finally {
            this.hideLoading();
        }
    }

    async gerarRelatorioSistema() {
        try {
            this.showLoading();
            const response = await fetch('/api/sistema/relatorio');
            
            if (response.ok) {
                // Verificar o tipo de conteúdo da resposta
                const contentType = response.headers.get('content-type');
                const contentDisposition = response.headers.get('content-disposition');
                
                // Determinar o nome do arquivo e extensão
                let fileName = 'relatorio-sistema';
                let fileExtension = 'pdf';
                
                if (contentDisposition) {
                    const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                    if (match && match[1]) {
                        const fullFileName = match[1].replace(/['"]/g, '');
                        const extensionMatch = fullFileName.match(/\.(\w+)$/);
                        if (extensionMatch) {
                            fileExtension = extensionMatch[1];
                        }
                    }
                }
                
                // Gerar nome do arquivo com timestamp
                const timestamp = new Date().toISOString().slice(0, 10);
                const fullFileName = `${fileName}-${timestamp}.${fileExtension}`;
                
                // Criar blob e download
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = fullFileName;
                a.style.display = 'none';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                // Mensagem de sucesso baseada no tipo de arquivo
                if (contentType && contentType.includes('application/pdf')) {
                    this.mostrarSucesso('Relatório PDF gerado com sucesso!');
                } else if (contentType && contentType.includes('text/csv')) {
                    this.mostrarSucesso('Relatório CSV gerado com sucesso!');
                } else {
                    this.mostrarSucesso(`Relatório gerado com sucesso! (${fileExtension.toUpperCase()})`);
                }
            } else {
                const errorData = await response.json().catch(() => ({}));
                const errorMessage = errorData.error || 'Erro ao gerar relatório';
                this.mostrarErro(errorMessage);
            }
        } catch (error) {
            console.error('Erro ao gerar relatório:', error);
            this.mostrarErro(`Erro ao gerar relatório: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }

    // Funções de backup
    async executarBackupManual() {
        try {
            this.showLoading();
            const response = await fetch('/api/backup/executar', { method: 'POST' });
            if (response.ok) {
                this.mostrarSucesso('Backup manual iniciado com sucesso!');
                setTimeout(() => this.verificarStatusSistema(), 5000);
            } else {
                this.mostrarErro('Erro ao executar backup manual');
            }
        } catch (error) {
            this.mostrarErro('Erro ao executar backup manual');
        } finally {
            this.hideLoading();
        }
    }

    async verHistoricoBackups() {
        try {
            this.showLoading();
            const response = await fetch('/api/backup/historico');
            if (response.ok) {
                const data = await response.json();
                this.mostrarHistoricoBackups(data);
            } else {
                this.mostrarErro('Erro ao carregar histórico de backups');
            }
        } catch (error) {
            this.mostrarErro('Erro ao carregar histórico de backups');
        } finally {
            this.hideLoading();
        }
    }

    // Função restaurarBackup desabilitada por segurança
    async restaurarBackup() {
        this.mostrarErro('Função de restauração temporariamente desabilitada por segurança');
        return;
    }



    // Funções utilitárias
    showLoading() {
        document.getElementById('loadingOverlay').classList.remove('d-none');
    }

    hideLoading() {
        document.getElementById('loadingOverlay').classList.add('d-none');
    }

    mostrarSucesso(mensagem) {
        Swal.fire({
            icon: 'success',
            title: 'Sucesso!',
            text: mensagem,
            timer: 3000,
            showConfirmButton: false
        });
    }

    mostrarErro(mensagem) {
        Swal.fire({
            icon: 'error',
            title: 'Erro!',
            text: mensagem,
            confirmButtonText: 'OK'
        });
    }

    mostrarHistoricoBackups(backups) {
        // Mostrar a tabela de histórico
        const historicoDiv = document.getElementById('historicoBackups');
        const tabelaBody = document.getElementById('tabelaBackups');
        
        if (historicoDiv && tabelaBody) {
            // Limpar tabela existente
            tabelaBody.innerHTML = '';
            
            // Preencher com os dados dos backups
            backups.forEach(backup => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${new Date(backup.data_criacao).toLocaleString('pt-BR')}</td>
                    <td>${backup.nome}</td>
                    <td>${backup.tamanho_mb} MB</td>
                    <td>
                        <span class="badge bg-warning">Função Desabilitada</span>
                    </td>
                `;
                tabelaBody.appendChild(row);
            });
            
            // Mostrar a seção
            historicoDiv.style.display = 'block';
            
            this.mostrarSucesso(`Histórico carregado: ${backups.length} backup(s) encontrado(s)`);
        } else {
            // Fallback para SweetAlert se a tabela não existir
            let html = '<div class="table-responsive"><table class="table table-sm">';
            html += '<thead><tr><th>Data</th><th>Arquivo</th><th>Tamanho</th><th>Ações</th></tr></thead><tbody>';
            
            backups.forEach(backup => {
                html += `<tr>
                    <td>${new Date(backup.data_criacao).toLocaleString('pt-BR')}</td>
                    <td>${backup.nome}</td>
                    <td>${backup.tamanho_mb} MB</td>
                    <td>
                        <span class="badge bg-warning">Função Desabilitada</span>
                    </td>
                `;
            });
            
            html += '</tbody></table></div>';

            Swal.fire({
                title: 'Histórico de Backups',
                html: html,
                width: '800px',
                confirmButtonText: 'Fechar'
            });
        }
    }


}

// Funções globais para compatibilidade
function salvarTodasConfiguracoes() {
    if (window.configuracoesSistema) {
        window.configuracoesSistema.salvarConfiguracoesGerais();
        window.configuracoesSistema.salvarDadosClinica();
        window.configuracoesSistema.salvarConfiguracoesBackup();
    }
}

function restaurarPadroes() {
    Swal.fire({
        title: 'Restaurar Padrões?',
        text: 'Todas as configurações serão restauradas para os valores padrão. Esta ação não pode ser desfeita.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sim, Restaurar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed && window.configuracoesSistema) {
            window.configuracoesSistema.configuracoes = window.configuracoesSistema.getConfiguracoesPadrao();
            window.configuracoesSistema.aplicarConfiguracoes();
            window.configuracoesSistema.mostrarSucesso('Configurações restauradas para os padrões!');
        }
    });
}

function carregarConfiguracoes() {
    if (window.configuracoesSistema) {
        window.configuracoesSistema.carregarConfiguracoes();
    }
}

function carregarDadosClinica() {
    if (window.configuracoesSistema) {
        window.configuracoesSistema.carregarConfiguracoes();
    }
}

// Funções de sistema
function verificarSistema() { 
    if (window.configuracoesSistema) window.configuracoesSistema.verificarSistema(); 
}
function limparCache() { 
    if (window.configuracoesSistema) window.configuracoesSistema.limparCache(); 
}
function gerarRelatorioSistema() { 
    if (window.configuracoesSistema) window.configuracoesSistema.gerarRelatorioSistema(); 
}

// Funções de backup
function executarBackupManual() { 
    if (window.configuracoesSistema) window.configuracoesSistema.executarBackupManual(); 
}
function verHistoricoBackups() { 
    if (window.configuracoesSistema) window.configuracoesSistema.verHistoricoBackups(); 
}
function restaurarBackup() { 
    // Função desabilitada por segurança
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            icon: 'warning',
            title: 'Função Desabilitada',
            text: 'A função de restauração de backup foi temporariamente desabilitada por segurança.',
            confirmButtonText: 'OK'
        });
    } else {
        alert('Função de restauração de backup desabilitada por segurança');
    }
}



// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.configuracoesSistema = new ConfiguracoesSistema();
    console.log('ConfiguracoesSistema inicializado:', window.configuracoesSistema);
});

// Também inicializar se o DOM já estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.configuracoesSistema = new ConfiguracoesSistema();
        console.log('ConfiguracoesSistema inicializado (DOM loading):', window.configuracoesSistema);
    });
} else {
    window.configuracoesSistema = new ConfiguracoesSistema();
    console.log('ConfiguracoesSistema inicializado (DOM ready):', window.configuracoesSistema);
}
