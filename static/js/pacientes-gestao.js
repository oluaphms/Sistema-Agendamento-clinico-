// ===== SISTEMA DE GESTÃO AVANÇADA DE PACIENTES =====

class PacientesGestao {
  constructor() {
    this.initializeElements();
    this.setupEventListeners();
    this.selectedPatients = new Set();
  }

  initializeElements() {
    this.bulkActionsBar = document.getElementById('bulkActionsBar');
    this.selectAllCheckbox = document.getElementById('selectAllPatients');
    this.patientCheckboxes = document.querySelectorAll('.patient-checkbox');
    this.importModal = document.getElementById('importModal');
    this.importForm = document.getElementById('importForm');
    this.csvFileInput = document.getElementById('csvFileInput');
    this.backupModal = document.getElementById('backupModal');
    this.historyModal = document.getElementById('historyModal');
  }

  setupEventListeners() {
    // Bulk actions
    if (this.selectAllCheckbox) {
      this.selectAllCheckbox.addEventListener('change', (e) => {
        this.toggleSelectAll(e.target.checked);
      });
    }

    // Patient checkboxes
    this.patientCheckboxes.forEach(checkbox => {
      checkbox.addEventListener('change', (e) => {
        this.handlePatientSelection(e.target);
      });
    });

    // Import form
    if (this.importForm) {
      this.importForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleImport();
      });
    }

    // CSV file input
    if (this.csvFileInput) {
      this.csvFileInput.addEventListener('change', (e) => {
        this.handleFileSelection(e.target.files[0]);
      });
    }
  }

  // ===== BULK ACTIONS =====
  toggleSelectAll(checked) {
    this.patientCheckboxes.forEach(checkbox => {
      checkbox.checked = checked;
      this.handlePatientSelection(checkbox);
    });
  }

  handlePatientSelection(checkbox) {
    const patientId = checkbox.value;
    
    if (checkbox.checked) {
      this.selectedPatients.add(patientId);
    } else {
      this.selectedPatients.delete(patientId);
    }
    
    this.updateBulkActionsBar();
  }

  updateBulkActionsBar() {
    if (!this.bulkActionsBar) return;
    
    if (this.selectedPatients.size > 0) {
      this.bulkActionsBar.style.display = 'block';
      this.bulkActionsBar.classList.add('animate__animated', 'animate__slideInUp');
      
      // Atualizar contador
      const counter = this.bulkActionsBar.querySelector('.selected-count');
      if (counter) {
        counter.textContent = this.selectedPatients.size;
      }
    } else {
      this.bulkActionsBar.style.display = 'none';
    }
  }

  async executeBulkAction(action) {
    if (this.selectedPatients.size === 0) {
      this.showNotification('Nenhum paciente selecionado', 'warning');
      return;
    }

    const actionNames = {
      'delete': 'excluir',
      'export': 'exportar',
      'send_sms': 'enviar SMS',
      'send_email': 'enviar email',
      'change_status': 'alterar status',
      'change_convenio': 'alterar convênio',
      'add_tag': 'adicionar tag'
    };

    const actionName = actionNames[action] || action;
    
    try {
      switch (action) {
        case 'delete':
          await this.bulkDelete();
          break;
        case 'export':
          await this.bulkExport();
          break;
        case 'send_sms':
          await this.bulkSendSMS();
          break;
        case 'send_email':
          await this.bulkSendEmail();
          break;
        case 'change_status':
          await this.bulkChangeStatus();
          break;
        case 'change_convenio':
          await this.bulkChangeConvenio();
          break;
        case 'add_tag':
          await this.bulkAddTag();
          break;
        default:
          throw new Error(`Ação não suportada: ${action}`);
      }
    } catch (error) {
      console.error(`Erro na ação em lote ${actionName}:`, error);
      this.showNotification(`Erro ao ${actionName}: ${error.message}`, 'error');
    }
  }

  async bulkDelete() {
    const result = await Swal.fire({
      title: 'Confirmar Exclusão em Lote?',
      text: `Deseja realmente excluir ${this.selectedPatients.size} pacientes?`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#dc3545',
      cancelButtonColor: '#6c757d',
      confirmButtonText: 'Sim, Excluir Todos!',
      cancelButtonText: 'Cancelar'
    });

    if (result.isConfirmed) {
      try {
        const response = await fetch('/api/pacientes/bulk-delete', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            patient_ids: Array.from(this.selectedPatients)
          })
        });

        if (response.ok) {
          this.showNotification(`${this.selectedPatients.size} pacientes excluídos com sucesso!`, 'success');
          this.clearSelection();
          this.reloadPage();
        } else {
          throw new Error('Falha na exclusão em lote');
        }
      } catch (error) {
        throw new Error(`Erro na exclusão: ${error.message}`);
      }
    }
  }

  async bulkExport() {
    try {
      const response = await fetch('/api/pacientes/bulk-export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          patient_ids: Array.from(this.selectedPatients),
          format: 'excel'
        })
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `pacientes_selecionados_${new Date().toISOString().split('T')[0]}.xlsx`;
        a.click();
        window.URL.revokeObjectURL(url);
        
        this.showNotification('Exportação em lote concluída!', 'success');
      } else {
        throw new Error('Falha na exportação em lote');
      }
    } catch (error) {
      throw new Error(`Erro na exportação: ${error.message}`);
    }
  }

  async bulkSendSMS() {
    const { value: message } = await Swal.fire({
      title: 'Enviar SMS em Lote',
      input: 'textarea',
      inputLabel: 'Mensagem para todos os pacientes selecionados',
      inputPlaceholder: 'Digite sua mensagem aqui...',
      inputValue: 'Olá! Lembramos que você tem uma consulta agendada.',
      showCancelButton: true,
      confirmButtonText: 'Enviar SMS',
      cancelButtonText: 'Cancelar',
      inputValidator: (value) => {
        if (!value) {
          return 'Digite uma mensagem!';
        }
        if (value.length > 160) {
          return 'Mensagem muito longa! Máximo 160 caracteres.';
        }
      }
    });

    if (message) {
      try {
        const response = await fetch('/api/pacientes/bulk-sms', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            patient_ids: Array.from(this.selectedPatients),
            message: message
          })
        });

        if (response.ok) {
          this.showNotification(`SMS enviado para ${this.selectedPatients.size} pacientes!`, 'success');
        } else {
          throw new Error('Falha no envio de SMS');
        }
      } catch (error) {
        throw new Error(`Erro no envio: ${error.message}`);
      }
    }
  }

  async bulkSendEmail() {
    const { value: formValues } = await Swal.fire({
      title: 'Enviar Email em Lote',
      html: `
        <div class="mb-3">
          <label class="form-label">Assunto</label>
          <input id="emailSubject" class="form-control" value="Lembrete de Consulta">
        </div>
        <div class="mb-3">
          <label class="form-label">Mensagem</label>
          <textarea id="emailMessage" class="form-control" rows="4">Olá! Lembramos que você tem uma consulta agendada.</textarea>
        </div>
        <div class="form-check">
          <input id="emailTemplate" class="form-check-input" type="checkbox" checked>
          <label class="form-check-label" for="emailTemplate">
            Usar template personalizado
          </label>
        </div>
      `,
      showCancelButton: true,
      confirmButtonText: 'Enviar Email',
      cancelButtonText: 'Cancelar',
      preConfirm: () => {
        return {
          subject: document.getElementById('emailSubject').value,
          message: document.getElementById('emailMessage').value,
          useTemplate: document.getElementById('emailTemplate').checked
        };
      }
    });

    if (formValues) {
      try {
        const response = await fetch('/api/pacientes/bulk-email', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            patient_ids: Array.from(this.selectedPatients),
            subject: formValues.subject,
            message: formValues.message,
            use_template: formValues.useTemplate
          })
        });

        if (response.ok) {
          this.showNotification(`Email enviado para ${this.selectedPatients.size} pacientes!`, 'success');
        } else {
          throw new Error('Falha no envio de email');
        }
      } catch (error) {
        throw new Error(`Erro no envio: ${error.message}`);
      }
    }
  }

  async bulkChangeStatus() {
    const { value: newStatus } = await Swal.fire({
      title: 'Alterar Status em Lote',
      input: 'select',
      inputOptions: {
        'ativo': 'Ativo',
        'inativo': 'Inativo',
        'pendente': 'Pendente',
        'suspenso': 'Suspenso'
      },
      inputLabel: 'Novo status para todos os pacientes selecionados',
      showCancelButton: true,
      confirmButtonText: 'Alterar Status',
      cancelButtonText: 'Cancelar'
    });

    if (newStatus) {
      try {
        const response = await fetch('/api/pacientes/bulk-status', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            patient_ids: Array.from(this.selectedPatients),
            new_status: newStatus
          })
        });

        if (response.ok) {
          this.showNotification(`Status alterado para ${newStatus} em ${this.selectedPatients.size} pacientes!`, 'success');
          this.reloadPage();
        } else {
          throw new Error('Falha na alteração de status');
        }
      } catch (error) {
        throw new Error(`Erro na alteração: ${error.message}`);
      }
    }
  }

  async bulkChangeConvenio() {
    const { value: newConvenio } = await Swal.fire({
      title: 'Alterar Convênio em Lote',
      input: 'select',
      inputOptions: {
        'particular': 'Particular',
        'unimed': 'Unimed',
        'amil': 'Amil',
        'sulamerica': 'SulAmérica',
        'bradesco': 'Bradesco Saúde',
        'porto_seguro': 'Porto Seguro'
      },
      inputLabel: 'Novo convênio para todos os pacientes selecionados',
      showCancelButton: true,
      confirmButtonText: 'Alterar Convênio',
      cancelButtonText: 'Cancelar'
    });

    if (newConvenio) {
      try {
        const response = await fetch('/api/pacientes/bulk-convenio', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            patient_ids: Array.from(this.selectedPatients),
            new_convenio: newConvenio
          })
        });

        if (response.ok) {
          this.showNotification(`Convênio alterado para ${newConvenio} em ${this.selectedPatients.size} pacientes!`, 'success');
          this.reloadPage();
        } else {
          throw new Error('Falha na alteração de convênio');
        }
      } catch (error) {
        throw new Error(`Erro na alteração: ${error.message}`);
      }
    }
  }

  async bulkAddTag() {
    const { value: tag } = await Swal.fire({
      title: 'Adicionar Tag em Lote',
      input: 'text',
      inputLabel: 'Tag para todos os pacientes selecionados',
      inputPlaceholder: 'Ex: VIP, Retorno, Emergência...',
      showCancelButton: true,
      confirmButtonText: 'Adicionar Tag',
      cancelButtonText: 'Cancelar',
      inputValidator: (value) => {
        if (!value) {
          return 'Digite uma tag!';
        }
        if (value.length > 20) {
          return 'Tag muito longa! Máximo 20 caracteres.';
        }
      }
    });

    if (tag) {
      try {
        const response = await fetch('/api/pacientes/bulk-tag', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            patient_ids: Array.from(this.selectedPatients),
            tag: tag
          })
        });

        if (response.ok) {
          this.showNotification(`Tag "${tag}" adicionada a ${this.selectedPatients.size} pacientes!`, 'success');
          this.reloadPage();
        } else {
          throw new Error('Falha na adição de tag');
        }
      } catch (error) {
        throw new Error(`Erro na adição: ${error.message}`);
      }
    }
  }

  // ===== IMPORTAÇÃO VIA CSV =====
  handleFileSelection(file) {
    if (!file) return;
    
    if (!file.name.endsWith('.csv')) {
      this.showNotification('Por favor, selecione um arquivo CSV válido', 'error');
      return;
    }

    if (file.size > 5 * 1024 * 1024) { // 5MB
      this.showNotification('Arquivo muito grande. Máximo 5MB', 'error');
      return;
    }

    // Mostrar preview do arquivo
    this.showCSVPreview(file);
  }

  async showCSVPreview(file) {
    try {
      const text = await file.text();
      const lines = text.split('\n');
      const headers = lines[0].split(',');
      const previewData = lines.slice(1, 6); // Primeiras 5 linhas

      const previewHTML = `
        <div class="mb-3">
          <h6>Preview do Arquivo (${file.name})</h6>
          <div class="table-responsive">
            <table class="table table-sm table-bordered">
              <thead>
                <tr>
                  ${headers.map(h => `<th>${h.trim()}</th>`).join('')}
                </tr>
              </thead>
              <tbody>
                ${previewData.map(line => {
                  const cells = line.split(',');
                  return `<tr>${cells.map(cell => `<td>${cell.trim()}</td>`).join('')}</tr>`;
                }).join('')}
              </tbody>
            </table>
          </div>
          <small class="text-muted">Total de linhas: ${lines.length - 1}</small>
        </div>
      `;

      const previewDiv = document.getElementById('csvPreview');
      if (previewDiv) {
        previewDiv.innerHTML = previewHTML;
        previewDiv.style.display = 'block';
      }
    } catch (error) {
      console.error('Erro ao ler arquivo CSV:', error);
      this.showNotification('Erro ao ler arquivo CSV', 'error');
    }
  }

  async handleImport() {
    const file = this.csvFileInput.files[0];
    if (!file) {
      this.showNotification('Selecione um arquivo CSV', 'warning');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('csv_file', file);
      
      // Opções de importação
      const skipDuplicates = document.getElementById('skipDuplicates')?.checked || false;
      const updateExisting = document.getElementById('updateExisting')?.checked || false;
      const validateData = document.getElementById('validateData')?.checked || true;
      
      formData.append('options', JSON.stringify({
        skip_duplicates: skipDuplicates,
        update_existing: updateExisting,
        validate_data: validateData
      }));

      this.showImportProgress('Iniciando importação...');
      
      const response = await fetch('/api/pacientes/import-csv', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        
        this.showImportProgress(`Importação concluída! ✅`);
        this.showImportResult(result);
        
        setTimeout(() => {
          this.hideImportProgress();
          this.reloadPage();
        }, 3000);
        
      } else {
        const error = await response.json();
        throw new Error(error.message || 'Falha na importação');
      }
      
    } catch (error) {
      console.error('Erro na importação:', error);
      this.showImportProgress(`Erro: ${error.message} ❌`);
      
      setTimeout(() => this.hideImportProgress(), 3000);
    }
  }

  showImportResult(result) {
    Swal.fire({
      title: 'Importação Concluída!',
      html: `
        <div class="text-start">
          <div class="alert alert-success">
            <strong>Sucesso:</strong> ${result.imported || 0} pacientes importados
          </div>
          ${result.updated ? `<div class="alert alert-info"><strong>Atualizados:</strong> ${result.updated} pacientes</div>` : ''}
          ${result.skipped ? `<div class="alert alert-warning"><strong>Pulados:</strong> ${result.skipped} pacientes (duplicados)</div>` : ''}
          ${result.errors && result.errors.length > 0 ? `
            <div class="alert alert-danger">
              <strong>Erros:</strong> ${result.errors.length} linhas com problemas
              <details class="mt-2">
                <summary>Ver detalhes</summary>
                <small>${result.errors.join('<br>')}</small>
              </details>
            </div>
          ` : ''}
        </div>
      `,
      icon: 'success',
      confirmButtonText: 'OK'
    });
  }

  // ===== BACKUP E RESTORE =====
  async createBackup() {
    try {
      this.showBackupProgress('Criando backup...');
      
      const response = await fetch('/api/pacientes/backup', {
        method: 'POST'
      });

      if (response.ok) {
        const result = await response.json();
        
        this.showBackupProgress('Backup criado com sucesso! ✅');
        
        // Download do arquivo de backup
        const link = document.createElement('a');
        link.href = result.download_url;
        link.download = `backup_pacientes_${new Date().toISOString().split('T')[0]}.zip`;
        link.click();
        
        setTimeout(() => this.hideBackupProgress(), 2000);
        
      } else {
        throw new Error('Falha na criação do backup');
      }
      
    } catch (error) {
      console.error('Erro no backup:', error);
      this.showBackupProgress(`Erro: ${error.message} ❌`);
      setTimeout(() => this.hideBackupProgress(), 3000);
    }
  }

  async restoreBackup(backupFile) {
    if (!backupFile) return;
    
    const result = await Swal.fire({
      title: 'Restaurar Backup?',
      text: 'Esta ação irá substituir todos os dados atuais. Tem certeza?',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#dc3545',
      cancelButtonColor: '#6c757d',
      confirmButtonText: 'Sim, Restaurar!',
      cancelButtonText: 'Cancelar'
    });

    if (result.isConfirmed) {
      try {
        const formData = new FormData();
        formData.append('backup_file', backupFile);
        
        this.showBackupProgress('Restaurando backup...');
        
        const response = await fetch('/api/pacientes/restore', {
          method: 'POST',
          body: formData
        });

        if (response.ok) {
          this.showBackupProgress('Backup restaurado com sucesso! ✅');
          setTimeout(() => {
            this.hideBackupProgress();
            this.reloadPage();
          }, 2000);
        } else {
          throw new Error('Falha na restauração do backup');
        }
        
      } catch (error) {
        console.error('Erro na restauração:', error);
        this.showBackupProgress(`Erro: ${error.message} ❌`);
        setTimeout(() => this.hideBackupProgress(), 3000);
      }
    }
  }

  // ===== HISTÓRICO DE ALTERAÇÕES =====
  async loadHistory(patientId = null) {
    try {
      const url = patientId ? 
        `/api/pacientes/${patientId}/history` : 
        '/api/pacientes/history';
      
      const response = await fetch(url);
      
      if (response.ok) {
        const history = await response.json();
        this.displayHistory(history, patientId);
      } else {
        throw new Error('Falha ao carregar histórico');
      }
      
    } catch (error) {
      console.error('Erro ao carregar histórico:', error);
      this.showNotification(`Erro ao carregar histórico: ${error.message}`, 'error');
    }
  }

  displayHistory(history, patientId = null) {
    const title = patientId ? 'Histórico do Paciente' : 'Histórico Geral';
    
    const historyHTML = history.map(entry => `
      <div class="timeline-item">
        <div class="timeline-marker ${this.getActionColor(entry.action)}"></div>
        <div class="timeline-content">
          <h6 class="timeline-title">${entry.action}</h6>
          <p class="timeline-text">${entry.description}</p>
          <small class="text-muted">
            ${entry.user || 'Sistema'} • ${new Date(entry.timestamp).toLocaleString('pt-BR')}
          </small>
        </div>
      </div>
    `).join('');

    Swal.fire({
      title: title,
      html: `
        <div class="timeline">
          ${historyHTML}
        </div>
      `,
      width: '800px',
      showConfirmButton: false,
      showCloseButton: true
    });
  }

  getActionColor(action) {
    const colors = {
      'create': 'bg-success',
      'update': 'bg-primary',
      'delete': 'bg-danger',
      'import': 'bg-info',
      'export': 'bg-warning',
      'status_change': 'bg-secondary'
    };
    return colors[action] || 'bg-secondary';
  }

  // ===== UTILITÁRIOS =====
  clearSelection() {
    this.selectedPatients.clear();
    this.patientCheckboxes.forEach(checkbox => {
      checkbox.checked = false;
    });
    this.updateBulkActionsBar();
  }

  reloadPage() {
    window.location.reload();
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

  showImportProgress(message) {
    const progress = document.getElementById('importProgress');
    const status = document.getElementById('importStatus');
    
    if (progress && status) {
      progress.style.display = 'block';
      status.textContent = message;
    }
  }

  hideImportProgress() {
    const progress = document.getElementById('importProgress');
    if (progress) {
      progress.style.display = 'none';
    }
  }

  showBackupProgress(message) {
    const progress = document.getElementById('backupProgress');
    const status = document.getElementById('backupStatus');
    
    if (progress && status) {
      progress.style.display = 'block';
      status.textContent = message;
    }
  }

  hideBackupProgress() {
    const progress = document.getElementById('backupProgress');
    if (progress) {
      progress.style.display = 'none';
    }
  }
}

// ===== FUNÇÕES GLOBAIS =====
function showBulkActionsModal() {
  const modal = new bootstrap.Modal(document.getElementById('bulkActionsModal'));
  modal.show();
}

function showImportModal() {
  const modal = new bootstrap.Modal(document.getElementById('importModal'));
  modal.show();
}

function showBackupModal() {
  const modal = new bootstrap.Modal(document.getElementById('backupModal'));
  modal.show();
}

function showHistoryModal(patientId = null) {
  if (window.pacientesGestao) {
    window.pacientesGestao.loadHistory(patientId);
  }
}

// ===== INICIALIZAÇÃO =====
document.addEventListener('DOMContentLoaded', function() {
  window.pacientesGestao = new PacientesGestao();
});
