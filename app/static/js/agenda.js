// Agenda JavaScript - Sistema Clínica
console.log('=== ARQUIVO AGENDA.JS INICIANDO ===');

// Definir funções imediatamente para evitar erros de referência
console.log('Definindo funções imediatamente...');

// Função para mostrar modal de novo agendamento
window.showQuickAppointment = function() {
    console.log('showQuickAppointment chamada');
    
    // Verificar se o modal existe
    const modal = document.getElementById('quickAppointmentModal');
    if (!modal) {
        console.error('Modal de novo agendamento não encontrado');
        return;
    }
    
    // Limpar formulário
    const form = document.getElementById('quickAppointmentForm');
    if (form) {
        form.reset();
        
        // Definir data atual como padrão
        const dateInput = document.getElementById('appointmentDate');
        if (dateInput) {
            const today = new Date().toISOString().split('T')[0];
            dateInput.value = today;
        }
        
        // Limpar seleções
        const pacienteSelect = document.getElementById('pacienteSelect');
        const profissionalSelect = document.getElementById('profissionalSelect');
        const servicoSelect = document.getElementById('servicoSelect');
        const timeSlotSelect = document.getElementById('timeSlotSelect');
        
        if (pacienteSelect) pacienteSelect.value = '';
        if (profissionalSelect) profissionalSelect.value = '';
        if (servicoSelect) {
            servicoSelect.value = '';
            updateDuration();
        }
        if (timeSlotSelect) timeSlotSelect.innerHTML = '<option value="">Selecione um horário</option>';
    }
    
    // Mostrar modal usando Bootstrap
    try {
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        console.log('Modal de novo agendamento aberto');
    } catch (error) {
        console.error('Erro ao abrir modal:', error);
        // Fallback: mostrar modal manualmente
        modal.style.display = 'block';
        modal.classList.add('show');
        document.body.classList.add('modal-open');
    }
};

// Função para alternar visualização
window.toggleView = function(view) {
    console.log('toggleView chamada:', view);
    
    // Esconder todas as visualizações
    const calendarView = document.getElementById('calendarView');
    const listView = document.getElementById('listView');
    
    if (view === 'calendar') {
        // Mostrar visualização de calendário
        if (calendarView) {
            calendarView.style.display = 'block';
            listView.style.display = 'none';
            
            // Inicializar calendário se ainda não foi inicializado
            if (!window.calendarInitialized) {
                initializeCalendar();
                window.calendarInitialized = true;
            }
            
            // Atualizar botões ativos
            updateActiveViewButtons('calendar');
        }
    } else if (view === 'list') {
        // Mostrar visualização de lista
        if (listView) {
            listView.style.display = 'block';
            calendarView.style.display = 'none';
            
            // Atualizar botões ativos
            updateActiveViewButtons('list');
        }
    }
    
    // Salvar preferência do usuário
    localStorage.setItem('agendaView', view);
};

// Função para inicializar o calendário
function initializeCalendar() {
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;
    
    try {
        const calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'pt-br',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay'
            },
            buttonText: {
                today: 'Hoje',
                month: 'Mês',
                week: 'Semana',
                day: 'Dia'
            },
            events: getAgendamentosForCalendar(),
            eventClick: function(info) {
                const agendamentoId = info.event.id;
                editAppointment(agendamentoId);
            },
            eventColor: '#007bff',
            height: 'auto'
        });
        
        calendar.render();
        window.agendaCalendar = calendar;
        console.log('Calendário inicializado com sucesso');
    } catch (error) {
        console.error('Erro ao inicializar calendário:', error);
        // Fallback para lista se o calendário falhar
        toggleView('list');
    }
}

// Função para obter agendamentos para o calendário
function getAgendamentosForCalendar() {
    const agendamentos = [];
    const rows = document.querySelectorAll('.agendamento-row');
    
    rows.forEach(row => {
        const id = row.getAttribute('data-id');
        const hora = row.querySelector('td:nth-child(2) strong').textContent;
        const paciente = row.querySelector('td:nth-child(3) strong').textContent;
        const profissional = row.querySelector('td:nth-child(4) strong').textContent;
        const servico = row.querySelector('td:nth-child(5) .badge').textContent;
        const status = row.querySelector('td:nth-child(6) .badge').textContent;
        
        // Obter data do filtro atual ou usar hoje
        const filterDate = document.getElementById('filterDate')?.value || new Date().toISOString().split('T')[0];
        
        agendamentos.push({
            id: id,
            title: `${hora} - ${paciente}`,
            start: `${filterDate}T${hora}:00`,
            end: `${filterDate}T${filterDate}:30`,
            extendedProps: {
                profissional: profissional,
                servico: servico,
                status: status
            }
        });
    });
    
    return agendamentos;
}

// Função para atualizar botões de visualização ativos
function updateActiveViewButtons(activeView) {
    const buttons = document.querySelectorAll('[onclick*="toggleView"]');
    buttons.forEach(button => {
        if (button.onclick.toString().includes(activeView)) {
            button.classList.remove('btn-outline-secondary');
            button.classList.add('btn-secondary');
        } else {
            button.classList.remove('btn-secondary');
            button.classList.add('btn-outline-secondary');
        }
    });
}

// Função para aplicar filtros
window.applyFilters = function() {
    console.log('applyFilters chamada');
    
    // Obter valores dos filtros
    const dateFilter = document.getElementById('filterDate')?.value;
    const profissionalFilter = document.getElementById('filterProfissional')?.value;
    const statusFilter = document.getElementById('filterStatus')?.value;
    const servicoFilter = document.getElementById('filterServico')?.value;
    const searchFilter = document.getElementById('searchInput')?.value.toLowerCase();
    
    console.log('Filtros aplicados:', {
        data: dateFilter,
        profissional: profissionalFilter,
        status: statusFilter,
        servico: servicoFilter,
        busca: searchFilter
    });
    
    // Aplicar filtros na tabela
    const rows = document.querySelectorAll('.agendamento-row');
    let visibleCount = 0;
    
    rows.forEach(row => {
        let shouldShow = true;
        
        // Filtro por data
        if (dateFilter) {
            const rowDate = row.querySelector('td:nth-child(2)')?.textContent;
            if (rowDate && !rowDate.includes(dateFilter)) {
                shouldShow = false;
            }
        }
        
        // Filtro por profissional
        if (profissionalFilter && shouldShow) {
            const profId = row.getAttribute('data-prof-id');
            if (profId !== profissionalFilter) {
                shouldShow = false;
            }
        }
        
        // Filtro por status
        if (statusFilter && shouldShow) {
            const status = row.querySelector('td:nth-child(6) .badge')?.textContent;
            if (status !== statusFilter) {
                shouldShow = false;
            }
        }
        
        // Filtro por serviço
        if (servicoFilter && shouldShow) {
            const servId = row.getAttribute('data-serv-id');
            if (servId !== servicoFilter) {
                shouldShow = false;
            }
        }
        
        // Filtro por busca (paciente)
        if (searchFilter && shouldShow) {
            const paciente = row.querySelector('td:nth-child(3) strong')?.textContent.toLowerCase();
            if (!paciente || !paciente.includes(searchFilter)) {
                shouldShow = false;
            }
        }
        
        // Aplicar visibilidade
        if (shouldShow) {
            row.style.display = '';
            visibleCount++;
        } else {
            row.style.display = 'none';
        }
    });
    
    // Atualizar contadores
    updateAgendaCounters(visibleCount);
    
    // Atualizar calendário se estiver ativo
    if (window.agendaCalendar && window.calendarInitialized) {
        window.agendaCalendar.refetchEvents();
    }
    
    // Mostrar mensagem de resultado
    showFilterResult(visibleCount, rows.length);
    
    console.log(`Filtros aplicados: ${visibleCount} de ${rows.length} agendamentos visíveis`);
};

// Função para atualizar contadores da agenda
function updateAgendaCounters(visibleCount) {
    const totalElement = document.getElementById('totalAgendamentos');
    if (totalElement) {
        totalElement.textContent = visibleCount;
    }
}

// Função para mostrar resultado dos filtros
function showFilterResult(visible, total) {
    // Criar ou atualizar mensagem de resultado
    let resultDiv = document.getElementById('filterResult');
    if (!resultDiv) {
        resultDiv = document.createElement('div');
        resultDiv.id = 'filterResult';
        resultDiv.className = 'alert alert-info alert-dismissible fade show mt-3';
        resultDiv.innerHTML = `
            <i class="bi bi-funnel me-2"></i>
            <span id="filterResultText"></span>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const filtersCard = document.querySelector('.card.mb-4');
        if (filtersCard) {
            filtersCard.appendChild(resultDiv);
        }
    }
    
    const resultText = resultDiv.querySelector('#filterResultText');
    if (resultText) {
        if (visible === total) {
            resultText.textContent = `Mostrando todos os ${total} agendamentos`;
        } else {
            resultText.textContent = `Filtros aplicados: ${visible} de ${total} agendamentos encontrados`;
        }
    }
    
    // Auto-remover após 5 segundos
    setTimeout(() => {
        if (resultDiv && resultDiv.parentNode) {
            resultDiv.remove();
        }
    }, 5000);
}

// Função para exportar agenda
window.exportAgenda = function() {
    console.log('exportAgenda chamada');
    
    try {
        // Obter dados da agenda
        const agendamentos = getAgendamentosForExport();
        
        if (agendamentos.length === 0) {
            alert('Nenhum agendamento encontrado para exportar.');
            return;
        }
        
        // Criar CSV
        const csvContent = createCSV(agendamentos);
        
        // Download do arquivo
        downloadCSV(csvContent, `agenda_${new Date().toISOString().split('T')[0]}.csv`);
        
        console.log(`Agenda exportada com ${agendamentos.length} agendamentos`);
        
    } catch (error) {
        console.error('Erro ao exportar agenda:', error);
        alert('Erro ao exportar agenda. Verifique o console para mais detalhes.');
    }
};

// Função para obter dados para exportação
function getAgendamentosForExport() {
    const agendamentos = [];
    const rows = document.querySelectorAll('.agendamento-row:not([style*="display: none"])');
    
    rows.forEach(row => {
        const id = row.getAttribute('data-id');
        const hora = row.querySelector('td:nth-child(2) strong')?.textContent || '';
        const paciente = row.querySelector('td:nth-child(3) strong')?.textContent || '';
        const profissional = row.querySelector('td:nth-child(4) strong')?.textContent || '';
        const servico = row.querySelector('td:nth-child(5) .badge')?.textContent || '';
        const status = row.querySelector('td:nth-child(6) .badge')?.textContent || '';
        const valor = row.querySelector('td:nth-child(7) strong')?.textContent || '';
        
        agendamentos.push({
            id: id,
            hora: hora,
            paciente: paciente,
            profissional: profissional,
            servico: servico,
            status: status,
            valor: valor
        });
    });
    
    return agendamentos;
}

// Função para criar CSV
function createCSV(data) {
    const headers = ['ID', 'Hora', 'Paciente', 'Profissional', 'Serviço', 'Status', 'Valor'];
    const csvRows = [headers.join(',')];
    
    data.forEach(row => {
        const values = [
            row.id,
            `"${row.hora}"`,
            `"${row.paciente}"`,
            `"${row.profissional}"`,
            `"${row.servico}"`,
            `"${row.status}"`,
            `"${row.valor}"`
        ];
        csvRows.push(values.join(','));
    });
    
    return csvRows.join('\n');
}

// Função para download do CSV
function downloadCSV(content, filename) {
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } else {
        // Fallback para navegadores antigos
        alert('Seu navegador não suporta download automático. Copie o conteúdo abaixo:');
        prompt('Conteúdo CSV:', content);
    }
}

// Função para mostrar ações em lote
window.showBulkActions = function() {
    console.log('showBulkActions chamada');
    
    // Verificar se há agendamentos selecionados
    const selectedCheckboxes = document.querySelectorAll('.agendamento-checkbox:checked');
    
    if (selectedCheckboxes.length === 0) {
        alert('Selecione pelo menos um agendamento para realizar ações em lote.');
        return;
    }
    
    // Atualizar contador no modal
    const selectedCountElement = document.getElementById('selectedCount');
    if (selectedCountElement) {
        selectedCountElement.textContent = selectedCheckboxes.length;
    }
    
    // Mostrar modal de ações em lote
    const modal = document.getElementById('bulkActionsModal');
    if (modal) {
        try {
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
            console.log(`Modal de ações em lote aberto para ${selectedCheckboxes.length} agendamentos`);
        } catch (error) {
            console.error('Erro ao abrir modal de ações em lote:', error);
            // Fallback manual
            modal.style.display = 'block';
            modal.classList.add('show');
            document.body.classList.add('modal-open');
        }
    } else {
        console.error('Modal de ações em lote não encontrado');
        alert('Modal de ações em lote não encontrado.');
    }
};

// Função para editar agendamento
window.editAppointment = function(id) {
    console.log('editAppointment chamada:', id);
    
    // Buscar dados do agendamento
    const row = document.querySelector(`.agendamento-row[data-id="${id}"]`);
    if (!row) {
        console.error('Agendamento não encontrado:', id);
        alert('Agendamento não encontrado.');
        return;
    }
    
    // Preencher modal com dados existentes
    fillEditModal(row);
    
    // Mostrar modal de edição
    const modal = document.getElementById('quickAppointmentModal');
    if (modal) {
        // Alterar título do modal
        const modalTitle = modal.querySelector('.modal-title');
        if (modalTitle) {
            modalTitle.textContent = 'Editar Agendamento';
        }
        
        // Alterar botão de salvar
        const saveBtn = modal.querySelector('[onclick="saveAppointment()"]');
        if (saveBtn) {
            saveBtn.innerHTML = '<i class="bi bi-save me-2"></i>Salvar Alterações';
            saveBtn.onclick = () => updateAppointment(id);
        }
        
        // Mostrar modal
        try {
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
        } catch (error) {
            console.error('Erro ao abrir modal de edição:', error);
            modal.style.display = 'block';
            modal.classList.add('show');
        }
    }
};

// Função para preencher modal de edição
function fillEditModal(row) {
    // Preencher campos com dados existentes
    const paciente = row.querySelector('td:nth-child(3) strong')?.textContent;
    const profissional = row.querySelector('td:nth-child(4) strong')?.textContent;
    const servico = row.querySelector('td:nth-child(5) .badge')?.textContent;
    const status = row.querySelector('td:nth-child(6) .badge')?.textContent;
    
    // Preencher selects (simplificado - em produção seria mais robusto)
    const pacienteSelect = document.getElementById('pacienteSelect');
    const profissionalSelect = document.getElementById('profissionalSelect');
    const servicoSelect = document.getElementById('servicoSelect');
    const statusSelect = document.querySelector('select[name="status"]');
    
    if (pacienteSelect) {
        // Encontrar opção que corresponde ao paciente
        Array.from(pacienteSelect.options).forEach(option => {
            if (option.textContent === paciente) {
                pacienteSelect.value = option.value;
            }
        });
    }
    
    if (profissionalSelect) {
        Array.from(profissionalSelect.options).forEach(option => {
            if (option.textContent === profissional) {
                profissionalSelect.value = option.value;
            }
        });
    }
    
    if (servicoSelect) {
        Array.from(servicoSelect.options).forEach(option => {
            if (option.textContent === servico) {
                servicoSelect.value = option.value;
            }
        });
    }
    
    if (statusSelect) {
        Array.from(statusSelect.options).forEach(option => {
            if (option.textContent === status) {
                statusSelect.value = option.value;
            }
        });
    }
}

// Função para atualizar agendamento
function updateAppointment(id) {
    console.log('Atualizando agendamento:', id);
    
    // Aqui você implementaria a lógica para salvar as alterações
    // Por enquanto, apenas mostra uma mensagem
    alert(`Agendamento ${id} atualizado com sucesso!`);
    
    // Fechar modal
    const modal = document.getElementById('quickAppointmentModal');
    if (modal) {
        try {
            const bootstrapModal = bootstrap.Modal.getInstance(modal);
            if (bootstrapModal) {
                bootstrapModal.hide();
            }
        } catch (error) {
            modal.style.display = 'none';
            modal.classList.remove('show');
        }
    }
}

// Função para confirmar agendamento
window.confirmAppointment = function(id) {
    console.log('confirmAppointment chamada:', id);
    
    if (confirm('Confirmar este agendamento?')) {
        // Atualizar status na interface
        updateAppointmentStatus(id, 'Confirmado');
        
        // Aqui você implementaria a chamada para a API
        console.log(`Agendamento ${id} confirmado`);
        
        // Mostrar feedback visual
        showStatusUpdate(id, 'Confirmado', 'success');
    }
};

// Função para reagendar
window.rescheduleAppointment = function(id) {
    console.log('rescheduleAppointment chamada:', id);
    
    // Abrir modal de edição para reagendamento
    editAppointment(id);
    
    // Focar no campo de data
    setTimeout(() => {
        const dateInput = document.getElementById('appointmentDate');
        if (dateInput) {
            dateInput.focus();
            dateInput.select();
        }
    }, 500);
};

// Função para cancelar agendamento
window.cancelAppointment = function(id) {
    console.log('cancelAppointment chamada:', id);
    
    if (confirm('Cancelar este agendamento? Esta ação não pode ser desfeita.')) {
        // Atualizar status na interface
        updateAppointmentStatus(id, 'Cancelado');
        
        // Aqui você implementaria a chamada para a API
        console.log(`Agendamento ${id} cancelado`);
        
        // Mostrar feedback visual
        showStatusUpdate(id, 'Cancelado', 'danger');
    }
};

// Função para atualizar status do agendamento na interface
function updateAppointmentStatus(id, newStatus) {
    const row = document.querySelector(`.agendamento-row[data-id="${id}"]`);
    if (!row) return;
    
    const statusBadge = row.querySelector('td:nth-child(6) .badge');
    if (statusBadge) {
        // Remover classes de status anteriores
        statusBadge.className = 'badge status-badge';
        
        // Adicionar nova classe de status
        statusBadge.classList.add(`status-${newStatus.toLowerCase()}`);
        statusBadge.textContent = newStatus;
    }
}

// Função para mostrar feedback visual de atualização
function showStatusUpdate(id, status, type) {
    const row = document.querySelector(`.agendamento-row[data-id="${id}"]`);
    if (!row) return;
    
    // Adicionar efeito visual temporário
    row.style.backgroundColor = type === 'success' ? '#d4edda' : '#f8d7da';
    
    // Remover efeito após 2 segundos
    setTimeout(() => {
        row.style.backgroundColor = '';
    }, 2000);
    
    // Mostrar toast de confirmação
    if (window.showToast) {
        window.showToast(`Agendamento ${status.toLowerCase()} com sucesso!`, type);
    }
}

// Função para selecionar todos
window.toggleSelectAll = function() {
    console.log('toggleSelectAll chamada');
    
    const selectAllCheckbox = document.getElementById('selectAll');
    const agendamentoCheckboxes = document.querySelectorAll('.agendamento-checkbox');
    
    if (!selectAllCheckbox || agendamentoCheckboxes.length === 0) {
        console.error('Checkboxes não encontrados');
        return;
    }
    
    const isChecked = selectAllCheckbox.checked;
    
    // Marcar/desmarcar todos os checkboxes
    agendamentoCheckboxes.forEach(checkbox => {
        checkbox.checked = isChecked;
    });
    
    // Atualizar contador de selecionados
    updateSelectedCount();
    
    console.log(`${isChecked ? 'Marcados' : 'Desmarcados'} todos os ${agendamentoCheckboxes.length} agendamentos`);
};

// Função para atualizar contador de selecionados
function updateSelectedCount() {
    const selectedCount = document.querySelectorAll('.agendamento-checkbox:checked').length;
    const totalCount = document.querySelectorAll('.agendamento-checkbox').length;
    
    // Atualizar texto do botão de ações em lote
    const bulkActionsBtn = document.querySelector('[onclick="showBulkActions()"]');
    if (bulkActionsBtn) {
        if (selectedCount > 0) {
            bulkActionsBtn.innerHTML = `<i class="bi bi-collection me-1"></i>Ações em Lote (${selectedCount})`;
            bulkActionsBtn.classList.remove('btn-outline-success');
            bulkActionsBtn.classList.add('btn-success');
        } else {
            bulkActionsBtn.innerHTML = `<i class="bi bi-collection me-1"></i>Ações em Lote`;
            bulkActionsBtn.classList.remove('btn-success');
            bulkActionsBtn.classList.add('btn-outline-success');
        }
    }
    
    // Atualizar checkbox "selecionar todos"
    const selectAllCheckbox = document.getElementById('selectAll');
    if (selectAllCheckbox) {
        if (selectedCount === 0) {
            selectAllCheckbox.indeterminate = false;
            selectAllCheckbox.checked = false;
        } else if (selectedCount === totalCount) {
            selectAllCheckbox.indeterminate = false;
            selectAllCheckbox.checked = true;
        } else {
            selectAllCheckbox.indeterminate = true;
            selectAllCheckbox.checked = false;
        }
    }
}

// Função para confirmar em lote
window.bulkConfirm = function() {
    console.log('bulkConfirm chamada');
    
    const selectedIds = getSelectedAppointmentIds();
    if (selectedIds.length === 0) {
        alert('Nenhum agendamento selecionado.');
        return;
    }
    
    if (confirm(`Confirmar ${selectedIds.length} agendamento(s) selecionado(s)?`)) {
        selectedIds.forEach(id => {
            updateAppointmentStatus(id, 'Confirmado');
        });
        
        // Fechar modal e mostrar feedback
        closeBulkActionsModal();
        showBulkActionResult('confirmados', selectedIds.length);
    }
};

// Função para cancelar em lote
window.bulkCancel = function() {
    console.log('bulkCancel chamada');
    
    const selectedIds = getSelectedAppointmentIds();
    if (selectedIds.length === 0) {
        alert('Nenhum agendamento selecionado.');
        return;
    }
    
    if (confirm(`Cancelar ${selectedIds.length} agendamento(s) selecionado(s)? Esta ação não pode ser desfeita.`)) {
        selectedIds.forEach(id => {
            updateAppointmentStatus(id, 'Cancelado');
        });
        
        // Fechar modal e mostrar feedback
        closeBulkActionsModal();
        showBulkActionResult('cancelados', selectedIds.length);
    }
};

// Função para reagendar em lote
window.bulkReschedule = function() {
    console.log('bulkReschedule chamada');
    
    const selectedIds = getSelectedAppointmentIds();
    if (selectedIds.length === 0) {
        alert('Nenhum agendamento selecionado.');
        return;
    }
    
    alert(`Para reagendar ${selectedIds.length} agendamento(s), use a função de edição individual para cada um.`);
    closeBulkActionsModal();
};

// Função para exportar selecionados
window.bulkExport = function() {
    console.log('bulkExport chamada');
    
    const selectedIds = getSelectedAppointmentIds();
    if (selectedIds.length === 0) {
        alert('Nenhum agendamento selecionado.');
        return;
    }
    
    // Exportar apenas os selecionados
    const selectedRows = document.querySelectorAll('.agendamento-checkbox:checked');
    const agendamentos = [];
    
    selectedRows.forEach(checkbox => {
        const row = checkbox.closest('.agendamento-row');
        if (row) {
            const id = row.getAttribute('data-id');
            const hora = row.querySelector('td:nth-child(2) strong')?.textContent || '';
            const paciente = row.querySelector('td:nth-child(3) strong')?.textContent || '';
            const profissional = row.querySelector('td:nth-child(4) strong')?.textContent || '';
            const servico = row.querySelector('td:nth-child(5) .badge')?.textContent || '';
            const status = row.querySelector('td:nth-child(6) .badge')?.textContent || '';
            const valor = row.querySelector('td:nth-child(7) strong')?.textContent || '';
            
            agendamentos.push({
                id, hora, paciente, profissional, servico, status, valor
            });
        }
    });
    
    // Criar e baixar CSV
    const csvContent = createCSV(agendamentos);
    downloadCSV(csvContent, `agendamentos_selecionados_${new Date().toISOString().split('T')[0]}.csv`);
    
    closeBulkActionsModal();
    showBulkActionResult('exportados', selectedIds.length);
};

// Função auxiliar para obter IDs dos agendamentos selecionados
function getSelectedAppointmentIds() {
    const selectedCheckboxes = document.querySelectorAll('.agendamento-checkbox:checked');
    return Array.from(selectedCheckboxes).map(checkbox => checkbox.value);
}

// Função para fechar modal de ações em lote
function closeBulkActionsModal() {
    const modal = document.getElementById('bulkActionsModal');
    if (modal) {
        try {
            const bootstrapModal = bootstrap.Modal.getInstance(modal);
            if (bootstrapModal) {
                bootstrapModal.hide();
            }
        } catch (error) {
            modal.style.display = 'none';
            modal.classList.remove('show');
        }
    }
    
    // Limpar seleções
    const selectAllCheckbox = document.getElementById('selectAll');
    if (selectAllCheckbox) {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
    }
    
    document.querySelectorAll('.agendamento-checkbox').forEach(checkbox => {
        checkbox.checked = false;
    });
    
    updateSelectedCount();
}

// Função para mostrar resultado das ações em lote
function showBulkActionResult(action, count) {
    if (window.showToast) {
        window.showToast(`${count} agendamento(s) ${action} com sucesso!`, 'success');
    } else {
        alert(`${count} agendamento(s) ${action} com sucesso!`);
    }
}

// Função para filtrar opções de pacientes
window.filterPatientOptions = function(searchTerm) {
    console.log('filterPatientOptions chamada:', searchTerm);
    
    const pacienteSelect = document.getElementById('pacienteSelect');
    if (!pacienteSelect) return;
    
    const options = Array.from(pacienteSelect.options);
    options.forEach(option => {
        const text = option.textContent.toLowerCase();
        if (text.includes(searchTerm.toLowerCase()) || searchTerm === '') {
            option.style.display = '';
        } else {
            option.style.display = 'none';
        }
    });
};

// Função para carregar horários disponíveis
window.loadAvailableSlots = function() {
    console.log('loadAvailableSlots chamada');
    
    const profissionalId = document.getElementById('profissionalSelect')?.value;
    const data = document.getElementById('appointmentDate')?.value;
    
    if (!profissionalId || !data) {
        console.log('Profissional ou data não selecionados');
        return;
    }
    
    // Simular carregamento de horários disponíveis
    const timeSlots = generateTimeSlots();
    populateTimeSlots(timeSlots);
};

// Função para gerar horários disponíveis (simulada)
function generateTimeSlots() {
    const slots = [];
    const startHour = 8; // 8:00
    const endHour = 18;  // 18:00
    
    for (let hour = startHour; hour < endHour; hour++) {
        slots.push(`${hour.toString().padStart(2, '0')}:00`);
        slots.push(`${hour.toString().padStart(2, '0')}:30`);
    }
    
    return slots;
}

// Função para preencher horários disponíveis
function populateTimeSlots(slots) {
    const timeSlotSelect = document.getElementById('timeSlotSelect');
    if (!timeSlotSelect) return;
    
    timeSlotSelect.innerHTML = '<option value="">Selecione um horário</option>';
    
    slots.forEach(slot => {
        const option = document.createElement('option');
        option.value = slot;
        option.textContent = slot;
        timeSlotSelect.appendChild(option);
    });
}

// Função para atualizar duração
window.updateDuration = function() {
    console.log('updateDuration chamada');
    
    const servicoSelect = document.getElementById('servicoSelect');
    const durationInput = document.getElementById('durationInput');
    
    if (!servicoSelect || !durationInput) return;
    
    const selectedOption = servicoSelect.options[servicoSelect.selectedIndex];
    if (selectedOption && selectedOption.dataset.duration) {
        durationInput.value = selectedOption.dataset.duration;
    }
};

// Função para alternar opções recorrentes
window.toggleRecurringOptions = function() {
    console.log('toggleRecurringOptions chamada');
    
    const recurringCheck = document.getElementById('recurringCheck');
    const recurringOptions = document.getElementById('recurringOptions');
    
    if (recurringCheck && recurringOptions) {
        if (recurringCheck.checked) {
            recurringOptions.style.display = 'block';
        } else {
            recurringOptions.style.display = 'none';
        }
    }
};

// Função para salvar agendamento
window.saveAppointment = function() {
    console.log('saveAppointment chamada');
    
    // Validar formulário
    const form = document.getElementById('quickAppointmentForm');
    if (!form) return;
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    // Coletar dados do formulário
    const formData = new FormData(form);
    const appointmentData = {
        paciente_id: formData.get('paciente_id'),
        profissional_id: formData.get('profissional_id'),
        servico_id: formData.get('servico_id'),
        data: formData.get('data'),
        hora: formData.get('hora'),
        duracao_min: formData.get('duracao_min'),
        status: formData.get('status'),
        origem: formData.get('origem'),
        valor_pago: formData.get('valor_pago'),
        observacoes: formData.get('observacoes')
    };
    
    console.log('Dados do agendamento:', appointmentData);
    
    // Aqui você implementaria a chamada para a API
    // Por enquanto, apenas mostra sucesso
    alert('Agendamento salvo com sucesso!');
    
    // Fechar modal
    const modal = document.getElementById('quickAppointmentModal');
    if (modal) {
        try {
            const bootstrapModal = bootstrap.Modal.getInstance(modal);
            if (bootstrapModal) {
                bootstrapModal.hide();
            }
        } catch (error) {
            modal.style.display = 'none';
            modal.classList.remove('show');
        }
    }
    
    // Recarregar página para mostrar novo agendamento
    setTimeout(() => {
        location.reload();
    }, 1000);
};

// Função para mostrar modal de novo paciente
window.showNewPatientModal = function() {
    console.log('showNewPatientModal chamada');
    
    const modal = document.getElementById('newPatientModal');
    if (modal) {
        try {
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
        } catch (error) {
            console.error('Erro ao abrir modal de novo paciente:', error);
            modal.style.display = 'block';
            modal.classList.add('show');
        }
    }
};

// Função para salvar novo paciente
window.saveNewPatient = function() {
    console.log('saveNewPatient chamada');
    
    const form = document.getElementById('newPatientForm');
    if (!form) return;
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const formData = new FormData(form);
    const patientData = {
        nome: formData.get('nome'),
        cpf: formData.get('cpf'),
        telefone: formData.get('telefone'),
        email: formData.get('email'),
        endereco: formData.get('endereco')
    };
    
    console.log('Dados do paciente:', patientData);
    
    // Aqui você implementaria a chamada para a API
    alert('Paciente salvo com sucesso!');
    
    // Fechar modal
    const modal = document.getElementById('newPatientModal');
    if (modal) {
        try {
            const bootstrapModal = bootstrap.Modal.getInstance(modal);
            if (bootstrapModal) {
                bootstrapModal.hide();
            }
        } catch (error) {
            modal.style.display = 'none';
            modal.classList.remove('show');
        }
    }
    
    // Recarregar lista de pacientes
    setTimeout(() => {
        location.reload();
    }, 1000);
};

console.log('=== FUNÇÕES DEFINIDAS NO WINDOW ===');

// Inicialização da agenda quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== INICIALIZANDO AGENDA ===');
    
    // Carregar preferência de visualização salva
    const savedView = localStorage.getItem('agendaView') || 'list';
    if (savedView) {
        setTimeout(() => {
            toggleView(savedView);
        }, 100);
    }
    
    // Adicionar eventos aos checkboxes individuais
    document.querySelectorAll('.agendamento-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectedCount);
    });
    
    // Adicionar evento de busca em tempo real
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value;
            if (searchTerm.length >= 2 || searchTerm.length === 0) {
                applyFilters();
            }
        });
    }
    
    // Adicionar eventos de mudança nos filtros
    const filterInputs = ['filterDate', 'filterProfissional', 'filterStatus', 'filterServico'];
    filterInputs.forEach(filterId => {
        const filterElement = document.getElementById(filterId);
        if (filterElement) {
            filterElement.addEventListener('change', applyFilters);
        }
    });
    
    // Inicializar funcionalidades adicionais
    initializeAgendaFeatures();
    
    console.log('=== AGENDA INICIALIZADA COM SUCESSO ===');
});

// Função para inicializar funcionalidades adicionais
function initializeAgendaFeatures() {
    // Adicionar tooltips aos botões
    const buttons = document.querySelectorAll('[title]');
    buttons.forEach(button => {
        if (button.title) {
            button.setAttribute('data-bs-toggle', 'tooltip');
            button.setAttribute('data-bs-placement', 'top');
        }
    });
    
    // Inicializar tooltips do Bootstrap se disponível
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Adicionar efeitos visuais aos botões
    addButtonEffects();
}

// Função para adicionar efeitos visuais aos botões
function addButtonEffects() {
    const actionButtons = document.querySelectorAll('.btn-group-sm .btn');
    actionButtons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
            this.style.transition = 'transform 0.2s ease';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
}

// Verificação das funções após um pequeno delay para garantir que foram definidas
setTimeout(function() {
    console.log('=== VERIFICAÇÃO FINAL DAS FUNÇÕES ===');

    // Verificar se as funções foram definidas
    const functions = [
        'showQuickAppointment', 'toggleView', 'applyFilters', 'exportAgenda',
        'showBulkActions', 'editAppointment', 'confirmAppointment', 
        'rescheduleAppointment', 'cancelAppointment', 'toggleSelectAll',
        'bulkConfirm', 'bulkCancel', 'bulkReschedule', 'bulkExport',
        'filterPatientOptions', 'loadAvailableSlots', 'updateDuration',
        'toggleRecurringOptions', 'saveAppointment', 'showNewPatientModal', 'saveNewPatient'
    ];

    let allDefined = true;
    functions.forEach(funcName => {
        if (typeof window[funcName] === 'function') {
            console.log(`✅ ${funcName}: OK`);
        } else {
            console.error(`❌ ${funcName}: NÃO DEFINIDA`);
            allDefined = false;
        }
    });

    if (allDefined) {
        console.log('🎉 TODAS AS FUNÇÕES FORAM DEFINIDAS COM SUCESSO!');
    } else {
        console.error('⚠️ ALGUMAS FUNÇÕES NÃO FORAM DEFINIDAS');
    }

    // Verificar se Bootstrap está disponível
    console.log('Bootstrap disponível:', typeof bootstrap !== 'undefined');
    if (typeof bootstrap !== 'undefined') {
        console.log('Bootstrap Modal disponível:', typeof bootstrap.Modal !== 'undefined');
    }

    console.log('=== ARQUIVO AGENDA.JS CARREGADO COM SUCESSO ===');
}, 100);
