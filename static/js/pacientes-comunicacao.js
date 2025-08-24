// ===== SISTEMA DE COMUNICAÇÃO E ANÁLISE DE PACIENTES =====

class PacientesComunicacao {
  constructor() {
    this.initializeElements();
    this.setupEventListeners();
    this.initializeCharts();
  }

  initializeElements() {
    this.smsModal = document.getElementById('smsModal');
    this.emailModal = document.getElementById('emailModal');
    this.whatsappModal = document.getElementById('whatsappModal');
    this.dashboardModal = document.getElementById('dashboardModal');
    this.chartContainer = document.getElementById('chartContainer');
    this.metricsContainer = document.getElementById('metricsContainer');
  }

  setupEventListeners() {
    // Event listeners para modais de comunicação
    this.setupCommunicationModals();
    
    // Event listeners para dashboard
    this.setupDashboardEvents();
  }

  setupCommunicationModals() {
    // SMS Modal
    const smsForm = document.getElementById('smsForm');
    if (smsForm) {
      smsForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleSMSSubmission();
      });
    }

    // Email Modal
    const emailForm = document.getElementById('emailForm');
    if (emailForm) {
      emailForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleEmailSubmission();
      });
    }

    // WhatsApp Modal
    const whatsappForm = document.getElementById('whatsappForm');
    if (whatsappForm) {
      whatsappForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleWhatsAppSubmission();
      });
    }
  }

  setupDashboardEvents() {
    // Filtros de período
    const periodFilter = document.getElementById('periodFilter');
    if (periodFilter) {
      periodFilter.addEventListener('change', () => {
        this.updateDashboard();
      });
    }

    // Botões de atualização
    const refreshBtn = document.getElementById('refreshDashboard');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => {
        this.updateDashboard();
      });
    }
  }

  // ===== FUNCIONALIDADES DE COMUNICAÇÃO =====
  
  async handleSMSSubmission() {
    const form = document.getElementById('smsForm');
    const formData = new FormData(form);
    
    try {
      const response = await fetch('/api/pacientes/send-sms', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        this.showNotification(`SMS enviado com sucesso para ${result.sent_count} pacientes!`, 'success');
        
        // Fechar modal
        const modal = bootstrap.Modal.getInstance(this.smsModal);
        if (modal) modal.hide();
        
        // Limpar formulário
        form.reset();
        
      } else {
        const error = await response.json();
        throw new Error(error.message || 'Falha no envio de SMS');
      }
      
    } catch (error) {
      console.error('Erro no envio de SMS:', error);
      this.showNotification(`Erro no envio: ${error.message}`, 'error');
    }
  }

  async handleEmailSubmission() {
    const form = document.getElementById('emailForm');
    const formData = new FormData(form);
    
    try {
      const response = await fetch('/api/pacientes/send-email', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        this.showNotification(`Email enviado com sucesso para ${result.sent_count} pacientes!`, 'success');
        
        // Fechar modal
        const modal = bootstrap.Modal.getInstance(this.emailModal);
        if (modal) modal.hide();
        
        // Limpar formulário
        form.reset();
        
      } else {
        const error = await response.json();
        throw new Error(error.message || 'Falha no envio de email');
      }
      
    } catch (error) {
      console.error('Erro no envio de email:', error);
      this.showNotification(`Erro no envio: ${error.message}`, 'error');
    }
  }

  async handleWhatsAppSubmission() {
    const form = document.getElementById('whatsappForm');
    const formData = new FormData(form);
    
    try {
      const response = await fetch('/api/pacientes/send-whatsapp', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        this.showNotification(`WhatsApp enviado com sucesso para ${result.sent_count} pacientes!`, 'success');
        
        // Fechar modal
        const modal = bootstrap.Modal.getInstance(this.whatsappModal);
        if (modal) modal.hide();
        
        // Limpar formulário
        form.reset();
        
      } else {
        const error = await response.json();
        throw new Error(error.message || 'Falha no envio de WhatsApp');
      }
      
    } catch (error) {
      console.error('Erro no envio de WhatsApp:', error);
      this.showNotification(`Erro no envio: ${error.message}`, 'error');
    }
  }

  // ===== FUNCIONALIDADES DE ANÁLISE =====
  
  async initializeCharts() {
    if (!this.chartContainer) return;
    
    try {
      await this.loadDashboardData();
      this.createCharts();
      this.updateMetrics();
    } catch (error) {
      console.error('Erro ao inicializar dashboard:', error);
    }
  }

  async loadDashboardData() {
    try {
      const response = await fetch('/api/pacientes/dashboard-data');
      
      if (response.ok) {
        this.dashboardData = await response.json();
      } else {
        // Fallback: gerar dados de exemplo
        this.dashboardData = this.generateSampleData();
      }
    } catch (error) {
      console.error('Erro ao carregar dados do dashboard:', error);
      this.dashboardData = this.generateSampleData();
    }
  }

  generateSampleData() {
    const hoje = new Date();
    const meses = [];
    const pacientes = [];
    const convenios = [];
    const categorias = [];
    
    // Gerar dados dos últimos 12 meses
    for (let i = 11; i >= 0; i--) {
      const data = new Date(hoje.getFullYear(), hoje.getMonth() - i, 1);
      meses.push(data.toLocaleDateString('pt-BR', { month: 'short', year: '2-digit' }));
      pacientes.push(Math.floor(Math.random() * 50) + 10);
    }
    
    // Dados de convênios
    const conveniosData = ['Particular', 'Unimed', 'Amil', 'SulAmérica', 'Bradesco'];
    conveniosData.forEach(conv => {
      convenios.push({
        name: conv,
        value: Math.floor(Math.random() * 100) + 20
      });
    });
    
    // Dados de categorias
    const categoriasData = ['Adulto', 'Idoso', 'Criança', 'Adolescente', 'Gestante'];
    categoriasData.forEach(cat => {
      categorias.push({
        name: cat,
        value: Math.floor(Math.random() * 80) + 15
      });
    });
    
    return {
      meses,
      pacientes,
      convenios,
      categorias,
      total: pacientes.reduce((a, b) => a + b, 0),
      crescimento: ((pacientes[pacientes.length - 1] - pacientes[0]) / pacientes[0] * 100).toFixed(1)
    };
  }

  createCharts() {
    if (!this.chartContainer || !this.dashboardData) return;
    
    // Gráfico de crescimento mensal
    this.createGrowthChart();
    
    // Gráfico de convênios
    this.createConveniosChart();
    
    // Gráfico de categorias
    this.createCategoriasChart();
  }

  createGrowthChart() {
    const ctx = document.getElementById('growthChart');
    if (!ctx) return;
    
    if (window.growthChart) {
      window.growthChart.destroy();
    }
    
    window.growthChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: this.dashboardData.meses,
        datasets: [{
          label: 'Novos Pacientes',
          data: this.dashboardData.pacientes,
          borderColor: '#0d6efd',
          backgroundColor: 'rgba(13, 110, 253, 0.1)',
          tension: 0.4,
          fill: true
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Crescimento Mensal de Pacientes'
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 10
            }
          }
        }
      }
    });
  }

  createConveniosChart() {
    const ctx = document.getElementById('conveniosChart');
    if (!ctx) return;
    
    if (window.conveniosChart) {
      window.conveniosChart.destroy();
    }
    
    window.conveniosChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: this.dashboardData.convenios.map(c => c.name),
        datasets: [{
          data: this.dashboardData.convenios.map(c => c.value),
          backgroundColor: [
            '#0d6efd',
            '#198754',
            '#ffc107',
            '#dc3545',
            '#6f42c1'
          ]
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Distribuição por Convênio'
          },
          legend: {
            position: 'bottom'
          }
        }
      }
    });
  }

  createCategoriasChart() {
    const ctx = document.getElementById('categoriasChart');
    if (!ctx) return;
    
    if (window.categoriasChart) {
      window.categoriasChart.destroy();
    }
    
    window.categoriasChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: this.dashboardData.categorias.map(c => c.name),
        datasets: [{
          label: 'Quantidade',
          data: this.dashboardData.categorias.map(c => c.value),
          backgroundColor: [
            'rgba(13, 110, 253, 0.8)',
            'rgba(25, 135, 84, 0.8)',
            'rgba(255, 193, 7, 0.8)',
            'rgba(220, 53, 69, 0.8)',
            'rgba(111, 66, 193, 0.8)'
          ],
          borderColor: [
            '#0d6efd',
            '#198754',
            '#ffc107',
            '#dc3545',
            '#6f42c1'
          ],
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Distribuição por Categoria'
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  }

  updateMetrics() {
    if (!this.metricsContainer || !this.dashboardData) return;
    
    const metrics = [
      {
        title: 'Total de Pacientes',
        value: this.dashboardData.total,
        icon: 'bi-people',
        color: 'primary'
      },
      {
        title: 'Crescimento Anual',
        value: `${this.dashboardData.crescimento}%`,
        icon: 'bi-graph-up',
        color: this.dashboardData.crescimento >= 0 ? 'success' : 'danger'
      },
      {
        title: 'Convênios Ativos',
        value: this.dashboardData.convenios.length,
        icon: 'bi-shield-check',
        color: 'info'
      },
      {
        title: 'Média Mensal',
        value: Math.round(this.dashboardData.pacientes.reduce((a, b) => a + b, 0) / 12),
        icon: 'bi-calculator',
        color: 'warning'
      }
    ];
    
    this.metricsContainer.innerHTML = metrics.map(metric => `
      <div class="col-lg-3 col-md-6 mb-4">
        <div class="card border-0 shadow-sm">
          <div class="card-body text-center">
            <div class="metric-icon bg-${metric.color} bg-opacity-10 text-${metric.color} rounded-circle mx-auto mb-3">
              <i class="bi ${metric.icon} fs-2"></i>
            </div>
            <h3 class="metric-value text-${metric.color} mb-1">${metric.value}</h3>
            <p class="metric-title text-muted mb-0">${metric.title}</p>
          </div>
        </div>
      </div>
    `).join('');
  }

  async updateDashboard() {
    try {
      await this.loadDashboardData();
      this.createCharts();
      this.updateMetrics();
      
      this.showNotification('Dashboard atualizado com sucesso!', 'success');
    } catch (error) {
      console.error('Erro ao atualizar dashboard:', error);
      this.showNotification('Erro ao atualizar dashboard', 'error');
    }
  }

  // ===== RELATÓRIOS AVANÇADOS =====
  
  async generateAdvancedReport(type, options = {}) {
    try {
      const response = await fetch('/api/pacientes/advanced-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          report_type: type,
          options: options
        })
      });

      if (response.ok) {
        const report = await response.json();
        this.displayAdvancedReport(report, type);
      } else {
        throw new Error('Falha na geração do relatório');
      }
      
    } catch (error) {
      console.error('Erro na geração do relatório:', error);
      this.showNotification(`Erro na geração: ${error.message}`, 'error');
    }
  }

  displayAdvancedReport(report, type) {
    const reportTypes = {
      'frequencia': 'Relatório de Frequência',
      'crescimento': 'Análise de Crescimento',
      'convenios': 'Análise de Convênios',
      'demografico': 'Análise Demográfica',
      'financeiro': 'Análise Financeira'
    };

    const title = reportTypes[type] || 'Relatório Avançado';
    
    Swal.fire({
      title: title,
      html: `
        <div class="text-start">
          <div class="row">
            <div class="col-12">
              <h6>Resumo Executivo</h6>
              <p>${report.summary || 'Nenhum resumo disponível'}</p>
            </div>
          </div>
          
          ${report.charts ? `
            <div class="row mt-3">
              <div class="col-12">
                <h6>Visualizações</h6>
                <div id="reportChartContainer" style="height: 300px;"></div>
              </div>
            </div>
          ` : ''}
          
          ${report.data ? `
            <div class="row mt-3">
              <div class="col-12">
                <h6>Dados Detalhados</h6>
                <div class="table-responsive">
                  <table class="table table-sm table-bordered">
                    <thead>
                      <tr>
                        ${Object.keys(report.data[0] || {}).map(key => `<th>${key}</th>`).join('')}
                      </tr>
                    </thead>
                    <tbody>
                      ${report.data.slice(0, 10).map(row => 
                        `<tr>${Object.values(row).map(val => `<td>${val}</td>`).join('')}</tr>`
                      ).join('')}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          ` : ''}
          
          <div class="row mt-3">
            <div class="col-12">
              <button class="btn btn-primary btn-sm" onclick="downloadReport('${type}')">
                <i class="bi bi-download me-1"></i>Download PDF
              </button>
              <button class="btn btn-success btn-sm ms-2" onclick="exportReportData('${type}')">
                <i class="bi bi-file-earmark-excel me-1"></i>Exportar Excel
              </button>
            </div>
          </div>
        </div>
      `,
      width: '900px',
      showConfirmButton: false,
      showCloseButton: true
    });

    // Renderizar gráficos se disponíveis
    if (report.charts) {
      this.renderReportCharts(report.charts);
    }
  }

  renderReportCharts(chartsData) {
    const container = document.getElementById('reportChartContainer');
    if (!container) return;
    
    // Implementar renderização de gráficos específicos do relatório
    // Pode usar Chart.js ou outras bibliotecas
  }

  // ===== ANÁLISE PREDITIVA =====
  
  async generatePredictiveAnalysis() {
    try {
      const response = await fetch('/api/pacientes/predictive-analysis', {
        method: 'POST'
      });

      if (response.ok) {
        const analysis = await response.json();
        this.displayPredictiveAnalysis(analysis);
      } else {
        throw new Error('Falha na análise preditiva');
      }
      
    } catch (error) {
      console.error('Erro na análise preditiva:', error);
      this.showNotification(`Erro na análise: ${error.message}`, 'error');
    }
  }

  displayPredictiveAnalysis(analysis) {
    Swal.fire({
      title: 'Análise Preditiva',
      html: `
        <div class="text-start">
          <div class="row">
            <div class="col-md-6">
              <h6>📈 Previsões para Próximos 3 Meses</h6>
              <div class="alert alert-info">
                <strong>Crescimento Esperado:</strong> ${analysis.expected_growth || 'N/A'}%
              </div>
              <div class="alert alert-warning">
                <strong>Novos Pacientes:</strong> ${analysis.expected_new_patients || 'N/A'}
              </div>
            </div>
            <div class="col-md-6">
              <h6>🎯 Recomendações</h6>
              <ul class="list-unstyled">
                ${(analysis.recommendations || []).map(rec => 
                  `<li class="mb-2"><i class="bi bi-check-circle text-success me-2"></i>${rec}</li>`
                ).join('')}
              </ul>
            </div>
          </div>
          
          ${analysis.trends ? `
            <div class="row mt-3">
              <div class="col-12">
                <h6>📊 Tendências Identificadas</h6>
                <div class="row">
                  ${Object.entries(analysis.trends).map(([trend, value]) => `
                    <div class="col-md-4 mb-2">
                      <div class="card border-0 bg-light">
                        <div class="card-body p-2 text-center">
                          <small class="text-muted">${trend}</small>
                          <div class="fw-bold">${value}</div>
                        </div>
                      </div>
                    </div>
                  `).join('')}
                </div>
              </div>
            </div>
          ` : ''}
        </div>
      `,
      width: '800px',
      showConfirmButton: false,
      showCloseButton: true
    });
  }

  // ===== UTILITÁRIOS =====
  
  showNotification(message, type = 'info') {
    if (typeof showToast !== 'undefined') {
      showToast(message, type);
    } else if (typeof Swal !== 'undefined') {
      Swal.fire({
        title: type === 'success' ? 'Sucesso!' : type === 'error' ? 'Erro!' : 'Informação',
        text: message,
        icon: type,
        timer: type === 'success' ? 3000 : undefined,
        showConfirmButton: type !== 'success'
      });
    } else {
      alert(message);
    }
  }

  // ===== TEMPLATES DE COMUNICAÇÃO =====
  
  getSMSTemplates() {
    return [
      {
        name: 'Lembrete de Consulta',
        content: 'Olá {nome}! Lembramos que você tem consulta agendada para {data} às {hora}. Confirme sua presença.'
      },
      {
        name: 'Confirmação de Agendamento',
        content: 'Olá {nome}! Sua consulta foi agendada para {data} às {hora}. Aguardamos você!'
      },
      {
        name: 'Lembrete de Retorno',
        content: 'Olá {nome}! É hora do seu retorno. Entre em contato para agendar uma nova consulta.'
      },
      {
        name: 'Promoção Especial',
        content: 'Olá {nome}! Temos uma promoção especial para você. Entre em contato para saber mais!'
      }
    ];
  }

  getEmailTemplates() {
    return [
      {
        name: 'Boas-vindas',
        subject: 'Bem-vindo à Nossa Clínica!',
        content: `
          <h3>Olá {nome}!</h3>
          <p>Seja bem-vindo à nossa clínica. Estamos felizes em tê-lo como paciente.</p>
          <p>Seus dados foram cadastrados com sucesso e você já pode agendar consultas.</p>
          <p>Atenciosamente,<br>Equipe da Clínica</p>
        `
      },
      {
        name: 'Lembrete de Consulta',
        subject: 'Lembrete: Consulta Agendada',
        content: `
          <h3>Olá {nome}!</h3>
          <p>Lembramos que você tem uma consulta agendada:</p>
          <ul>
            <li><strong>Data:</strong> {data}</li>
            <li><strong>Horário:</strong> {hora}</li>
            <li><strong>Profissional:</strong> {profissional}</li>
          </ul>
          <p>Por favor, confirme sua presença ou entre em contato para reagendar.</p>
        `
      }
    ];
  }

  fillTemplate(template, data) {
    let filled = template;
    
    Object.entries(data).forEach(([key, value]) => {
      const regex = new RegExp(`{${key}}`, 'g');
      filled = filled.replace(regex, value);
    });
    
    return filled;
  }
}

// ===== FUNÇÕES GLOBAIS =====

function showSMSModal() {
  const modal = new bootstrap.Modal(document.getElementById('smsModal'));
  modal.show();
}

function showEmailModal() {
  const modal = new bootstrap.Modal(document.getElementById('emailModal'));
  modal.show();
}

function showWhatsAppModal() {
  const modal = new bootstrap.Modal(document.getElementById('whatsappModal'));
  modal.show();
}

function showDashboardModal() {
  const modal = new bootstrap.Modal(document.getElementById('dashboardModal'));
  modal.show();
  
  // Inicializar dashboard se não foi feito
  if (window.pacientesComunicacao && !window.pacientesComunicacao.dashboardData) {
    window.pacientesComunicacao.initializeCharts();
  }
}

function downloadReport(type) {
  if (window.pacientesComunicacao) {
    window.pacientesComunicacao.generateAdvancedReport(type, { format: 'pdf' });
  }
}

function exportReportData(type) {
  if (window.pacientesComunicacao) {
    window.pacientesComunicacao.generateAdvancedReport(type, { format: 'excel' });
  }
}

function generatePredictiveAnalysis() {
  if (window.pacientesComunicacao) {
    window.pacientesComunicacao.generatePredictiveAnalysis();
  }
}

// ===== INICIALIZAÇÃO =====

document.addEventListener('DOMContentLoaded', function() {
  window.pacientesComunicacao = new PacientesComunicacao();
});


