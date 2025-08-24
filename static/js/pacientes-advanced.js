// ===== SISTEMA AVANÇADO DE PACIENTES =====
// Funcionalidades: Validações robustas, máscaras, duplicatas, animações

class PacientesManager {
  constructor() {
    this.initializeElements();
    this.setupEventListeners();
    this.setupMasks();
    this.setupValidations();
    this.setupSearchAndFilters();
    this.setupFormSubmission();
  }

  initializeElements() {
    // Elementos do formulário
    this.form = document.getElementById('pacienteForm');
    this.nomeInput = document.getElementById('nome');
    this.cpfInput = document.getElementById('cpf');
    this.telefoneInput = document.getElementById('telefone');
    this.emailInput = document.getElementById('email');
    this.nascimentoInput = document.getElementById('nascimento');
    this.convenioInput = document.getElementById('convenio');
    this.categoriaInput = document.getElementById('categoria');
    this.observacoesInput = document.getElementById('observacoes');
    this.charCount = document.getElementById('charCount');
    
    // Elementos de busca e filtros
    this.searchInput = document.getElementById('searchInput');
    this.filterConvenio = document.getElementById('filterConvenio');
    this.pacientesGrid = document.getElementById('pacientesGrid');
    this.noResults = document.getElementById('noResults');
    
    // Botões
    this.submitBtn = this.form?.querySelector('button[type="submit"]');
  }

  setupEventListeners() {
    if (!this.form) return;
    
    // Validação em tempo real
    this.nomeInput?.addEventListener('blur', () => this.validarCampo(this.nomeInput, 'nome'));
    this.cpfInput?.addEventListener('blur', () => this.validarCampo(this.cpfInput, 'cpf'));
    this.telefoneInput?.addEventListener('blur', () => this.validarCampo(this.telefoneInput, 'telefone'));
    this.emailInput?.addEventListener('blur', () => this.validarCampo(this.emailInput, 'email'));
    this.nascimentoInput?.addEventListener('blur', () => this.validarCampo(this.nascimentoInput, 'nascimento'));
    this.categoriaInput?.addEventListener('change', () => this.validarCampo(this.categoriaInput, 'categoria'));
    
    // Contador de caracteres
    this.observacoesInput?.addEventListener('input', () => this.atualizarContadorCaracteres());
    
    // Busca e filtros
    this.searchInput?.addEventListener('input', () => this.filterPacientes());
    this.filterConvenio?.addEventListener('change', () => this.filterPacientes());
  }

  setupMasks() {
    // Máscara de CPF
    if (this.cpfInput) {
      this.cpfInput.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length <= 11) {
          value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
          e.target.value = value;
        }
      });
    }

    // Máscara de telefone
    if (this.telefoneInput) {
      this.telefoneInput.addEventListener('input', (e) => {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length <= 11) {
          if (value.length === 11) {
            value = value.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
          } else if (value.length === 10) {
            value = value.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
          }
          e.target.value = value;
        }
      });
    }
  }

  setupValidations() {
    // Validadores
    this.validators = {
      cpf: (cpf) => {
        cpf = cpf.replace(/[^\d]/g, '');
        if (cpf.length !== 11) return false;
        if (/^(\d)\1{10}$/.test(cpf)) return false;
        
        let soma = 0;
        for (let i = 0; i < 9; i++) {
          soma += parseInt(cpf.charAt(i)) * (10 - i);
        }
        let resto = 11 - (soma % 11);
        let dv1 = resto < 2 ? 0 : resto;
        
        soma = 0;
        for (let i = 0; i < 10; i++) {
          soma += parseInt(cpf.charAt(i)) * (11 - i);
        }
        resto = 11 - (soma % 11);
        let dv2 = resto < 2 ? 0 : resto;
        
        return cpf.charAt(9) == dv1 && cpf.charAt(10) == dv2;
      },
      
      telefone: (telefone) => {
        const regex = /^\(\d{2}\)\s\d{4,5}-\d{4}$/;
        return regex.test(telefone);
      },
      
      email: (email) => {
        const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return regex.test(email);
      },
      
      nome: (nome) => {
        return nome.length >= 3 && nome.length <= 100 && /^[A-Za-zÀ-ÿ\s]+$/.test(nome);
      },
      
      nascimento: (data) => {
        const hoje = new Date();
        const dataNasc = new Date(data);
        const idade = hoje.getFullYear() - dataNasc.getFullYear();
        return dataNasc <= hoje && idade >= 0 && idade <= 120;
      }
    };
  }

  setupSearchAndFilters() {
    if (!this.searchInput || !this.filterConvenio) return;
    
    // Debounce para busca
    let searchTimeout;
    this.searchInput.addEventListener('input', () => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => this.filterPacientes(), 300);
    });
    
    // Filtros adicionais
    const filterStatus = document.getElementById('filterStatus');
    const filterIdade = document.getElementById('filterIdade');
    const filterCadastro = document.getElementById('filterCadastro');
    const filterOrdenacao = document.getElementById('filterOrdenacao');
    
    if (filterStatus) filterStatus.addEventListener('change', () => this.filterPacientes());
    if (filterIdade) filterIdade.addEventListener('change', () => this.filterPacientes());
    if (filterCadastro) filterCadastro.addEventListener('change', () => this.filterPacientes());
    if (filterOrdenacao) filterOrdenacao.addEventListener('change', () => this.ordenarPacientes());
  }

  setupFormSubmission() {
    if (!this.form) return;
    
    this.form.addEventListener('submit', async (e) => {
      e.preventDefault();
      await this.handleFormSubmission();
    });
  }

  // ===== VALIDAÇÕES =====
  validarCampo(campo, tipo) {
    if (!campo) return false;
    
    const valor = campo.value.trim();
    const feedback = document.getElementById(campo.id + 'Error');
    let isValid = true;
    let mensagem = '';
    
    // Remove classes de validação anteriores
    campo.classList.remove('is-valid', 'is-invalid');
    
    // Validações específicas por tipo
    switch (tipo) {
      case 'cpf':
        if (!valor) {
          isValid = false;
          mensagem = 'CPF é obrigatório';
        } else if (!this.validators.cpf(valor)) {
          isValid = false;
          mensagem = 'CPF inválido';
        }
        break;
        
      case 'telefone':
        if (!valor) {
          isValid = false;
          mensagem = 'Telefone é obrigatório';
        } else if (!this.validators.telefone(valor)) {
          isValid = false;
          mensagem = 'Formato inválido. Use (11) 99999-9999';
        }
        break;
        
      case 'email':
        if (valor && !this.validators.email(valor)) {
          isValid = false;
          mensagem = 'Email inválido';
        }
        break;
        
      case 'nome':
        if (!valor) {
          isValid = false;
          mensagem = 'Nome é obrigatório';
        } else if (!this.validators.nome(valor)) {
          isValid = false;
          mensagem = 'Nome deve ter entre 3 e 100 caracteres, apenas letras';
        }
        break;
        
      case 'nascimento':
        if (!valor) {
          isValid = false;
          mensagem = 'Data de nascimento é obrigatória';
        } else if (!this.validators.nascimento(valor)) {
          isValid = false;
          mensagem = 'Data de nascimento inválida';
        }
        break;
        
      case 'categoria':
        if (!valor) {
          isValid = false;
          mensagem = 'Categoria é obrigatória';
        }
        break;
    }
    
    // Aplica validação visual
    if (isValid) {
      campo.classList.add('is-valid');
      if (feedback) feedback.textContent = '';
    } else {
      campo.classList.add('is-invalid');
      if (feedback) feedback.textContent = mensagem;
    }
    
    return isValid;
  }

  // ===== VERIFICAÇÃO DE DUPLICATAS =====
  async verificarDuplicatas(cpf, email, telefone) {
    try {
      const response = await fetch('/api/verificar-duplicatas', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ cpf, email, telefone })
      });
      
      if (response.ok) {
        const data = await response.json();
        return data.duplicatas;
      }
      return [];
    } catch (error) {
      console.error('Erro ao verificar duplicatas:', error);
      return [];
    }
  }

  // ===== SUBMISSÃO DO FORMULÁRIO =====
  async handleFormSubmission() {
    // Validar todos os campos
    const campos = [
      { campo: this.nomeInput, tipo: 'nome' },
      { campo: this.cpfInput, tipo: 'cpf' },
      { campo: this.telefoneInput, tipo: 'telefone' },
      { campo: this.nascimentoInput, tipo: 'nascimento' },
      { campo: this.categoriaInput, tipo: 'categoria' }
    ];
    
    let formIsValid = true;
    campos.forEach(({ campo, tipo }) => {
      if (!this.validarCampo(campo, tipo)) {
        formIsValid = false;
      }
    });
    
    if (!formIsValid) {
      this.showNotification('Por favor, corrija os erros no formulário', 'error');
      return;
    }
    
    // Verificar duplicatas antes de enviar
    const cpf = this.cpfInput.value.replace(/\D/g, '');
    const email = this.emailInput.value.trim();
    const telefone = this.telefoneInput.value.replace(/\D/g, '');
    
    const duplicatas = await this.verificarDuplicatas(cpf, email, telefone);
    
    if (duplicatas.length > 0) {
      const result = await this.showDuplicatasDialog(duplicatas);
      if (!result) return; // Não envia o formulário
    }
    
    // Enviar formulário
    await this.submitForm();
  }

  async showDuplicatasDialog(duplicatas) {
    return new Promise((resolve) => {
      Swal.fire({
        title: 'Paciente Duplicado',
        html: `
          <div class="text-start">
            <p class="mb-3">Paciente já cadastrado:</p>
            ${duplicatas.map(d => `
              <div class="alert alert-warning p-2 mb-2">
                <strong>${d.tipo}:</strong> ${d.valor}<br>
                <small>Paciente: ${d.paciente_nome}</small>
              </div>
            `).join('')}
          </div>
        `,
        icon: 'warning',
        confirmButtonText: 'Verificar',
        showCancelButton: true,
        cancelButtonText: 'Continuar mesmo assim',
        width: '500px'
      }).then((result) => {
        resolve(result.isConfirmed);
      });
    });
  }

  async submitForm() {
    if (!this.submitBtn) return;
    
    const originalText = this.submitBtn.innerHTML;
    this.submitBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Salvando...';
    this.submitBtn.disabled = true;
    
    try {
      // Simular envio (substituir por envio real)
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      this.showNotification('Paciente cadastrado com sucesso! 🎉', 'success');
      
      // Collapse form
      const collapse = bootstrap.Collapse.getInstance(document.getElementById('formCollapse'));
      if (collapse) {
        collapse.hide();
      }
      
      // Reset form
      this.form.reset();
      
      // Limpar validações
      const campos = [this.nomeInput, this.cpfInput, this.telefoneInput, this.emailInput, this.nascimentoInput, this.categoriaInput];
      campos.forEach(campo => {
        if (campo) campo.classList.remove('is-valid', 'is-invalid');
      });
      
      // Atualizar contador
      this.atualizarContadorCaracteres();
      
    } catch (error) {
      this.showNotification('Erro ao salvar paciente', 'error');
    } finally {
      this.submitBtn.innerHTML = originalText;
      this.submitBtn.disabled = false;
    }
  }

  // ===== BUSCA E FILTROS =====
  filterPacientes() {
    if (!this.searchInput || !this.filterConvenio) return;
    
    const searchTerm = this.searchInput.value.toLowerCase();
    const convenioFilter = this.filterConvenio.value.toLowerCase();
    const statusFilter = document.getElementById('filterStatus')?.value.toLowerCase() || '';
    const idadeFilter = document.getElementById('filterIdade')?.value || '';
    const cadastroFilter = document.getElementById('filterCadastro')?.value || '';
    
    const cards = document.querySelectorAll('.paciente-card');
    let visibleCount = 0;
    
    cards.forEach(card => {
      const nome = card.dataset.nome || '';
      const telefone = card.dataset.telefone || '';
      const email = card.dataset.email || '';
      const convenio = card.dataset.convenio || '';
      const status = card.dataset.status || 'ativo';
      const idade = this.calcularIdade(card.dataset.nascimento || '');
      const dataCadastro = card.dataset.cadastro || '';
      
      const matchesSearch = nome.includes(searchTerm) || 
                           telefone.includes(searchTerm) || 
                           email.includes(searchTerm);
      
      const matchesConvenio = !convenioFilter || convenio.includes(convenioFilter);
      const matchesStatus = !statusFilter || status.includes(statusFilter);
      const matchesIdade = !idadeFilter || this.matchesIdadeFilter(idade, idadeFilter);
      const matchesCadastro = !cadastroFilter || this.matchesCadastroFilter(dataCadastro, cadastroFilter);
      
      if (matchesSearch && matchesConvenio && matchesStatus && matchesIdade && matchesCadastro) {
        card.style.display = 'block';
        card.classList.add('animate__animated', 'animate__fadeIn');
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });
    
    // Mostrar/esconder mensagem de nenhum resultado
    if (visibleCount === 0) {
      this.noResults?.classList.remove('d-none');
      this.pacientesGrid?.classList.add('d-none');
    } else {
      this.noResults?.classList.add('d-none');
      this.pacientesGrid?.classList.remove('d-none');
    }
  }

  // ===== ORDENAÇÃO =====
  ordenarPacientes() {
    const ordenacao = document.getElementById('filterOrdenacao')?.value || 'nome';
    const grid = this.pacientesGrid;
    if (!grid) return;
    
    const cards = Array.from(grid.querySelectorAll('.paciente-card'));
    
    cards.sort((a, b) => {
      switch (ordenacao) {
        case 'nome':
          return (a.dataset.nome || '').localeCompare(b.dataset.nome || '');
        case 'nome_desc':
          return (b.dataset.nome || '').localeCompare(a.dataset.nome || '');
        case 'cadastro':
          return new Date(b.dataset.cadastro || '') - new Date(a.dataset.cadastro || '');
        case 'cadastro_desc':
          return new Date(a.dataset.cadastro || '') - new Date(b.dataset.cadastro || '');
        default:
          return 0;
      }
    });
    
    // Reordenar visualmente
    cards.forEach((card, index) => {
      card.style.order = index;
      card.style.animationDelay = `${index * 0.1}s`;
    });
  }

  // ===== UTILITÁRIOS DE FILTRO =====
  calcularIdade(dataNascimento) {
    if (!dataNascimento) return 0;
    const hoje = new Date();
    const nascimento = new Date(dataNascimento);
    return hoje.getFullYear() - nascimento.getFullYear();
  }

  matchesIdadeFilter(idade, filtro) {
    switch (filtro) {
      case 'crianca': return idade >= 0 && idade <= 12;
      case 'adolescente': return idade >= 13 && idade <= 17;
      case 'adulto': return idade >= 18 && idade <= 59;
      case 'idoso': return idade >= 60;
      default: return true;
    }
  }

  matchesCadastroFilter(dataCadastro, filtro) {
    if (!dataCadastro) return false;
    
    const hoje = new Date();
    const cadastro = new Date(dataCadastro);
    
    switch (filtro) {
      case 'hoje':
        return cadastro.toDateString() === hoje.toDateString();
      case 'semana':
        const inicioSemana = new Date(hoje.setDate(hoje.getDate() - hoje.getDay()));
        return cadastro >= inicioSemana;
      case 'mes':
        return cadastro.getMonth() === hoje.getMonth() && cadastro.getFullYear() === hoje.getFullYear();
      case 'ano':
        return cadastro.getFullYear() === hoje.getFullYear();
      default:
        return true;
    }
  }

  // ===== UTILITÁRIOS =====
  atualizarContadorCaracteres() {
    if (!this.observacoesInput || !this.charCount) return;
    
    const maxLength = 500;
    const atual = this.observacoesInput.value.length;
    
    this.charCount.textContent = atual;
    
    if (atual > maxLength * 0.8) {
      this.charCount.style.color = atual > maxLength * 0.9 ? '#dc3545' : '#ffc107';
    } else {
      this.charCount.style.color = '#6c757d';
    }
  }

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
}

// ===== FUNÇÕES GLOBAIS =====

// ===== FILTROS AVANÇADOS =====
function toggleAdvancedFilters() {
  const advancedFilters = document.getElementById('advancedFilters');
  const toggleText = document.getElementById('toggleText');
  
  if (advancedFilters.style.display === 'none') {
    advancedFilters.style.display = 'block';
    toggleText.textContent = 'Ocultar Filtros Avançados';
    advancedFilters.classList.add('animate__animated', 'animate__slideInDown');
  } else {
    advancedFilters.style.display = 'none';
    toggleText.textContent = 'Mostrar Filtros Avançados';
  }
}

function limparFiltros() {
  // Limpar campos de busca
  document.getElementById('searchInput').value = '';
  document.getElementById('filterConvenio').value = '';
  document.getElementById('filterStatus').value = '';
  document.getElementById('filterIdade').value = '';
  document.getElementById('filterCadastro').value = '';
  document.getElementById('filterOrdenacao').value = 'nome';
  
  // Aplicar filtros limpos
  if (window.pacientesManager) {
    window.pacientesManager.filterPacientes();
    window.pacientesManager.ordenarPacientes();
  }
  
  // Mostrar notificação
  if (typeof showToast !== 'undefined') {
    showToast('Filtros limpos com sucesso!', 'success');
  }
}

function editarPaciente(id) {
  window.location.href = `/pacientes/editar/${id}`;
}

function agendarConsulta(pacienteId) {
  window.location.href = `/agenda?paciente_id=${pacienteId}`;
}

function excluirPaciente(id, nome) {
  Swal.fire({
    title: 'Confirmar Exclusão?',
    text: `Deseja realmente excluir o paciente "${nome}"?`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#dc3545',
    cancelButtonColor: '#6c757d',
    confirmButtonText: 'Sim, Excluir!',
    cancelButtonText: 'Cancelar'
  }).then((result) => {
    if (result.isConfirmed) {
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = `/pacientes/excluir/${id}`;
      document.body.appendChild(form);
      form.submit();
    }
  });
}

function showQuickActions() {
  Swal.fire({
    title: 'Ações Rápidas',
    html: `
      <div class="row g-3">
        <div class="col-6">
          <button class="btn btn-primary w-100 py-3" data-bs-toggle="collapse" data-bs-target="#formCollapse">
            <i class="bi bi-person-plus fs-4 d-block mb-2"></i>
            <strong>Novo Paciente</strong>
          </button>
        </div>
        <div class="col-6">
          <button class="btn btn-success w-100 py-3" onclick="location.href='/agenda'">
            <i class="bi bi-calendar-plus fs-4 d-block mb-2"></i>
            <strong>Nova Consulta</strong>
          </button>
        </div>
        <div class="col-6">
          <button class="btn btn-info w-100 py-3" onclick="location.href='/calendario'">
            <i class="bi bi-calendar-week fs-4 d-block mb-2"></i>
            <strong>Ver Calendário</strong>
          </button>
        </div>
        <div class="col-6">
          <button class="btn btn-warning w-100 py-3" onclick="location.href='/dashboard'">
            <i class="bi bi-speedometer2 fs-4 d-block mb-2"></i>
            <strong>Dashboard</strong>
          </button>
        </div>
      </div>
    `,
    showConfirmButton: false,
    showCloseButton: true,
    width: '600px'
  });
}

// ===== INICIALIZAÇÃO =====
document.addEventListener('DOMContentLoaded', function() {
  // Inicializar gerenciador de pacientes
  window.pacientesManager = new PacientesManager();
  
  // Adicionar animações aos cards existentes
  const cards = document.querySelectorAll('.paciente-card');
  cards.forEach((card, index) => {
    card.style.animationDelay = `${index * 0.1}s`;
    card.classList.add('animate__animated', 'animate__fadeInUp');
  });
});
