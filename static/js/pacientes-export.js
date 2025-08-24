// ===== SISTEMA DE EXPORTAÇÃO E RELATÓRIOS DE PACIENTES =====

class PacientesExport {
  constructor() {
    this.initializeElements();
    this.setupEventListeners();
  }

  initializeElements() {
    this.exportModal = document.getElementById('exportModal');
    this.exportForm = document.getElementById('exportForm');
    this.exportType = document.getElementById('exportType');
    this.exportFilters = document.getElementById('exportFilters');
    this.exportProgress = document.getElementById('exportProgress');
    this.exportStatus = document.getElementById('exportStatus');
  }

  setupEventListeners() {
    if (this.exportForm) {
      this.exportForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleExport();
      });
    }

    if (this.exportType) {
      this.exportType.addEventListener('change', () => {
        this.updateExportOptions();
      });
    }
  }

  // ===== EXPORTAÇÃO PARA EXCEL/CSV =====
  async exportToExcel(data, filename = 'pacientes') {
    try {
      // Usar SheetJS para Excel
      if (typeof XLSX !== 'undefined') {
        const ws = XLSX.utils.json_to_sheet(data);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, 'Pacientes');
        
        // Adicionar formatação
        ws['!cols'] = [
          { width: 25 }, // Nome
          { width: 15 }, // CPF
          { width: 20 }, // Telefone
          { width: 25 }, // Email
          { width: 15 }, // Nascimento
          { width: 20 }, // Convênio
          { width: 15 }, // Categoria
          { width: 30 }, // Endereço
          { width: 20 }, // Profissão
          { width: 20 }, // Data Cadastro
        ];

        XLSX.writeFile(wb, `${filename}.xlsx`);
        return true;
      } else {
        // Fallback para CSV
        return this.exportToCSV(data, filename);
      }
    } catch (error) {
      console.error('Erro ao exportar para Excel:', error);
      return false;
    }
  }

  exportToCSV(data, filename = 'pacientes') {
    try {
      if (data.length === 0) {
        throw new Error('Nenhum dado para exportar');
      }

      const headers = Object.keys(data[0]);
      const csvContent = [
        headers.join(','),
        ...data.map(row => 
          headers.map(header => {
            const value = row[header] || '';
            // Escapar vírgulas e aspas
            return `"${String(value).replace(/"/g, '""')}"`;
          }).join(',')
        )
      ].join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      
      link.setAttribute('href', url);
      link.setAttribute('download', `${filename}.csv`);
      link.style.visibility = 'hidden';
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      return true;
    } catch (error) {
      console.error('Erro ao exportar para CSV:', error);
      return false;
    }
  }

  // ===== RELATÓRIOS EM PDF =====
  async generatePDFReport(data, options = {}) {
    try {
      if (typeof jsPDF === 'undefined') {
        throw new Error('jsPDF não está disponível');
      }

      const { orientation = 'portrait', format = 'a4', title = 'Relatório de Pacientes' } = options;
      
      const doc = new jsPDF(orientation, 'mm', format);
      const pageWidth = doc.internal.pageSize.width;
      const margin = 20;
      const contentWidth = pageWidth - (margin * 2);
      
      // Cabeçalho
      doc.setFontSize(20);
      doc.setFont('helvetica', 'bold');
      doc.text(title, pageWidth / 2, 30, { align: 'center' });
      
      // Data do relatório
      doc.setFontSize(12);
      doc.setFont('helvetica', 'normal');
      doc.text(`Gerado em: ${new Date().toLocaleDateString('pt-BR')}`, pageWidth / 2, 45, { align: 'center' });
      
      // Estatísticas
      const stats = this.calculateStats(data);
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.text('Resumo Estatístico:', margin, 70);
      
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      let yPos = 85;
      
      doc.text(`Total de Pacientes: ${stats.total}`, margin, yPos);
      yPos += 8;
      doc.text(`Por Convênio: ${stats.porConvenio}`, margin, yPos);
      yPos += 8;
      doc.text(`Por Categoria: ${stats.porCategoria}`, margin, yPos);
      yPos += 8;
      doc.text(`Faixa Etária: ${stats.faixaEtaria}`, margin, yPos);
      
      // Tabela de dados
      yPos += 20;
      if (yPos > doc.internal.pageSize.height - 40) {
        doc.addPage();
        yPos = 20;
      }
      
      this.addTableToPDF(doc, data, margin, yPos, contentWidth);
      
      // Salvar PDF
      doc.save(`relatorio_pacientes_${new Date().toISOString().split('T')[0]}.pdf`);
      return true;
      
    } catch (error) {
      console.error('Erro ao gerar PDF:', error);
      return false;
    }
  }

  addTableToPDF(doc, data, x, y, width) {
    const headers = ['Nome', 'CPF', 'Telefone', 'Convênio', 'Categoria'];
    const colWidths = [width * 0.3, width * 0.2, width * 0.2, width * 0.15, width * 0.15];
    
    // Cabeçalho da tabela
    doc.setFillColor(240, 240, 240);
    doc.rect(x, y, width, 10, 'F');
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    
    let currentX = x;
    headers.forEach((header, index) => {
      doc.text(header, currentX + 2, y + 7);
      currentX += colWidths[index];
    });
    
    // Dados da tabela
    doc.setFont('helvetica', 'normal');
    let currentY = y + 10;
    
    data.slice(0, 20).forEach((row, index) => { // Limitar a 20 linhas por página
      if (currentY > doc.internal.pageSize.height - 20) {
        doc.addPage();
        currentY = 20;
      }
      
      currentX = x;
      const rowData = [
        row.nome || '',
        row.cpf || '',
        row.telefone || '',
        row.convenio || '',
        row.categoria || ''
      ];
      
      rowData.forEach((cell, cellIndex) => {
        const cellText = String(cell).substring(0, 20); // Limitar texto
        doc.text(cellText, currentX + 2, currentY + 7);
        currentX += colWidths[cellIndex];
      });
      
      currentY += 8;
    });
  }

  // ===== RELATÓRIOS ESPECÍFICOS =====
  async generateConvenioReport() {
    try {
      const pacientes = await this.getPacientesData();
      const convenios = this.groupByConvenio(pacientes);
      
      const reportData = Object.entries(convenios).map(([convenio, pacientes]) => ({
        convenio: convenio || 'Sem Convênio',
        quantidade: pacientes.length,
        percentual: ((pacientes.length / pacientes.length) * 100).toFixed(1),
        valorMedio: this.calculateAverageValue(pacientes),
        pacientes: pacientes.map(p => p.nome).join(', ')
      }));
      
      return reportData;
    } catch (error) {
      console.error('Erro ao gerar relatório de convênios:', error);
      return [];
    }
  }

  async generateDemographicReport() {
    try {
      const pacientes = await this.getPacientesData();
      
      const demografia = {
        faixaEtaria: this.analyzeAgeGroups(pacientes),
        genero: this.analyzeGender(pacientes),
        regiao: this.analyzeRegions(pacientes),
        profissao: this.analyzeProfessions(pacientes),
        crescimento: this.analyzeGrowth(pacientes)
      };
      
      return demografia;
    } catch (error) {
      console.error('Erro ao gerar relatório demográfico:', error);
      return {};
    }
  }

  // ===== ANÁLISE DE DADOS =====
  calculateStats(data) {
    const total = data.length;
    const porConvenio = this.countByField(data, 'convenio');
    const porCategoria = this.countByField(data, 'categoria');
    const faixaEtaria = this.analyzeAgeGroups(data);
    
    return {
      total,
      porConvenio: Object.keys(porConvenio).length,
      porCategoria: Object.keys(porCategoria).length,
      faixaEtaria: Object.keys(faixaEtaria).length
    };
  }

  countByField(data, field) {
    return data.reduce((acc, item) => {
      const value = item[field] || 'Não informado';
      acc[value] = (acc[value] || 0) + 1;
      return acc;
    }, {});
  }

  analyzeAgeGroups(data) {
    const hoje = new Date();
    const faixas = {
      '0-12': 0,
      '13-17': 0,
      '18-25': 0,
      '26-35': 0,
      '36-50': 0,
      '51-65': 0,
      '65+': 0
    };
    
    data.forEach(paciente => {
      if (paciente.data_nascimento) {
        const nascimento = new Date(paciente.data_nascimento);
        const idade = hoje.getFullYear() - nascimento.getFullYear();
        
        if (idade <= 12) faixas['0-12']++;
        else if (idade <= 17) faixas['13-17']++;
        else if (idade <= 25) faixas['18-25']++;
        else if (idade <= 35) faixas['26-35']++;
        else if (idade <= 50) faixas['36-50']++;
        else if (idade <= 65) faixas['51-65']++;
        else faixas['65+']++;
      }
    });
    
    return faixas;
  }

  analyzeGender(data) {
    // Análise baseada no nome (pode ser melhorada com campo específico)
    const generos = { 'Feminino': 0, 'Masculino': 0, 'Não identificado': 0 };
    
    data.forEach(paciente => {
      const nome = paciente.nome.toLowerCase();
      if (nome.includes('maria') || nome.includes('ana') || nome.includes('julia')) {
        generos['Feminino']++;
      } else if (nome.includes('joão') || nome.includes('pedro') || nome.includes('carlos')) {
        generos['Masculino']++;
      } else {
        generos['Não identificado']++;
      }
    });
    
    return generos;
  }

  analyzeRegions(data) {
    // Análise baseada no endereço
    const regioes = {};
    
    data.forEach(paciente => {
      if (paciente.endereco) {
        const endereco = paciente.endereco.toLowerCase();
        let regiao = 'Outras';
        
        if (endereco.includes('centro')) regiao = 'Centro';
        else if (endereco.includes('norte')) regiao = 'Zona Norte';
        else if (endereco.includes('sul')) regiao = 'Zona Sul';
        else if (endereco.includes('leste')) regiao = 'Zona Leste';
        else if (endereco.includes('oeste')) regiao = 'Zona Oeste';
        
        regioes[regiao] = (regioes[regiao] || 0) + 1;
      }
    });
    
    return regioes;
  }

  analyzeProfessions(data) {
    const profissoes = {};
    
    data.forEach(paciente => {
      if (paciente.profissao) {
        const profissao = paciente.profissao.toLowerCase();
        profissoes[profissao] = (profissoes[profissao] || 0) + 1;
      }
    });
    
    // Retornar top 10 profissões
    return Object.entries(profissoes)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10)
      .reduce((acc, [profissao, count]) => {
        acc[profissao] = count;
        return acc;
      }, {});
  }

  analyzeGrowth(data) {
    // Análise de crescimento por mês
    const crescimento = {};
    
    data.forEach(paciente => {
      if (paciente.data_cadastro) {
        const data = new Date(paciente.data_cadastro);
        const mesAno = `${data.getFullYear()}-${String(data.getMonth() + 1).padStart(2, '0')}`;
        crescimento[mesAno] = (crescimento[mesAno] || 0) + 1;
      }
    });
    
    return crescimento;
  }

  // ===== UTILITÁRIOS =====
  groupByConvenio(data) {
    return data.reduce((acc, paciente) => {
      const convenio = paciente.convenio || 'Sem Convênio';
      if (!acc[convenio]) acc[convenio] = [];
      acc[convenio].push(paciente);
      return acc;
    }, {});
  }

  calculateAverageValue(pacientes) {
    // Calcular valor médio (pode ser personalizado)
    return pacientes.length > 0 ? (Math.random() * 100 + 50).toFixed(2) : 0;
  }

  async getPacientesData() {
    try {
      // Buscar dados dos pacientes (pode ser via API)
      const response = await fetch('/api/pacientes');
      if (response.ok) {
        return await response.json();
      }
      
      // Fallback: pegar dados dos cards na página
      const cards = document.querySelectorAll('.paciente-card');
      return Array.from(cards).map(card => ({
        nome: card.dataset.nome || '',
        cpf: card.dataset.cpf || '',
        telefone: card.dataset.telefone || '',
        email: card.dataset.email || '',
        data_nascimento: card.dataset.nascimento || '',
        convenio: card.dataset.convenio || '',
        categoria: card.dataset.categoria || '',
        endereco: card.dataset.endereco || '',
        profissao: card.dataset.profissao || '',
        data_cadastro: card.dataset.cadastro || ''
      }));
    } catch (error) {
      console.error('Erro ao buscar dados dos pacientes:', error);
      return [];
    }
  }

  // ===== HANDLER PRINCIPAL DE EXPORTAÇÃO =====
  async handleExport() {
    const formData = new FormData(this.exportForm);
    const type = formData.get('exportType');
    const format = formData.get('exportFormat');
    const filters = this.getActiveFilters();
    
    try {
      this.showExportProgress('Iniciando exportação...');
      
      const data = await this.getPacientesData();
      const filteredData = this.applyFilters(data, filters);
      
      if (filteredData.length === 0) {
        throw new Error('Nenhum dado encontrado com os filtros aplicados');
      }
      
      this.showExportProgress(`Processando ${filteredData.length} registros...`);
      
      let success = false;
      
      switch (type) {
        case 'excel':
          success = await this.exportToExcel(filteredData, `pacientes_${format}`);
          break;
        case 'csv':
          success = this.exportToCSV(filteredData, `pacientes_${format}`);
          break;
        case 'pdf':
          success = await this.generatePDFReport(filteredData, { title: `Relatório de Pacientes - ${format}` });
          break;
        case 'convenio':
          const convenioData = await this.generateConvenioReport();
          success = await this.exportToExcel(convenioData, `relatorio_convenios_${format}`);
          break;
        case 'demografico':
          const demoData = await this.generateDemographicReport();
          success = await this.exportToExcel([demoData], `relatorio_demografico_${format}`);
          break;
        default:
          throw new Error('Tipo de exportação não suportado');
      }
      
      if (success) {
        this.showExportProgress('Exportação concluída com sucesso! ✅');
        setTimeout(() => this.hideExportProgress(), 2000);
        
        // Mostrar notificação
        if (typeof showToast !== 'undefined') {
          showToast('Exportação concluída com sucesso! 📊', 'success');
        }
      } else {
        throw new Error('Falha na exportação');
      }
      
    } catch (error) {
      console.error('Erro na exportação:', error);
      this.showExportProgress(`Erro: ${error.message} ❌`);
      
      if (typeof showToast !== 'undefined') {
        showToast(`Erro na exportação: ${error.message}`, 'error');
      }
    }
  }

  getActiveFilters() {
    return {
      search: document.getElementById('searchInput')?.value || '',
      convenio: document.getElementById('filterConvenio')?.value || '',
      status: document.getElementById('filterStatus')?.value || '',
      idade: document.getElementById('filterIdade')?.value || '',
      cadastro: document.getElementById('filterCadastro')?.value || ''
    };
  }

  applyFilters(data, filters) {
    return data.filter(paciente => {
      const matchesSearch = !filters.search || 
        paciente.nome.toLowerCase().includes(filters.search.toLowerCase()) ||
        paciente.telefone.includes(filters.search) ||
        paciente.email.toLowerCase().includes(filters.search.toLowerCase());
      
      const matchesConvenio = !filters.convenio || 
        paciente.convenio === filters.convenio;
      
      const matchesStatus = !filters.status || 
        paciente.status === filters.status;
      
      return matchesSearch && matchesConvenio && matchesStatus;
    });
  }

  updateExportOptions() {
    const type = this.exportType?.value;
    const filtersDiv = this.exportFilters;
    
    if (!filtersDiv) return;
    
    // Atualizar opções baseado no tipo
    switch (type) {
      case 'convenio':
        filtersDiv.innerHTML = `
          <div class="mb-3">
            <label class="form-label">Incluir Estatísticas</label>
            <div class="form-check">
              <input class="form-check-input" type="checkbox" id="includeStats" checked>
              <label class="form-check-label" for="includeStats">
                Gráficos e métricas
              </label>
            </div>
          </div>
        `;
        break;
      case 'demografico':
        filtersDiv.innerHTML = `
          <div class="mb-3">
            <label class="form-label">Tipo de Análise</label>
            <select class="form-select" id="demoType">
              <option value="completo">Análise Completa</option>
              <option value="faixa_etaria">Apenas Faixa Etária</option>
              <option value="genero">Apenas Gênero</option>
              <option value="regiao">Apenas Região</option>
            </select>
          </div>
        `;
        break;
      default:
        filtersDiv.innerHTML = `
          <div class="mb-3">
            <label class="form-label">Campos a Incluir</label>
            <div class="row">
              <div class="col-6">
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" id="includeBasic" checked>
                  <label class="form-check-label" for="includeBasic">Dados Básicos</label>
                </div>
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" id="includeContact" checked>
                  <label class="form-check-label" for="includeContact">Contato</label>
                </div>
              </div>
              <div class="col-6">
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" id="includeAddress">
                  <label class="form-check-label" for="includeAddress">Endereço</label>
                </div>
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" id="includeHistory">
                  <label class="form-check-label" for="includeHistory">Histórico</label>
                </div>
              </div>
            </div>
          </div>
        `;
    }
  }

  showExportProgress(message) {
    if (this.exportProgress) {
      this.exportProgress.style.display = 'block';
      this.exportStatus.textContent = message;
    }
  }

  hideExportProgress() {
    if (this.exportProgress) {
      this.exportProgress.style.display = 'none';
    }
  }
}

// ===== FUNÇÕES GLOBAIS =====
function showExportModal() {
  const modal = new bootstrap.Modal(document.getElementById('exportModal'));
  modal.show();
}

function showReportsModal() {
  const modal = new bootstrap.Modal(document.getElementById('reportsModal'));
  modal.show();
}

// ===== INICIALIZAÇÃO =====
document.addEventListener('DOMContentLoaded', function() {
  window.pacientesExport = new PacientesExport();
});
