/**
 * Dados de Exemplo para Demonstração
 * Sistema Clínica - Analytics & Relatórios
 */

const SampleData = {
  // Dados de agendamentos mensais (últimos 12 meses)
  agendamentosMensal: {
    labels: [
      'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
      'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
    ],
    datasets: [{
      label: 'Agendamentos',
      data: [45, 52, 48, 61, 55, 67, 72, 68, 75, 82, 78, 89]
    }]
  },
  
  // Dados de ranking de profissionais
  profissionaisRanking: {
    labels: [
      'Dr. João Silva',
      'Dra. Maria Santos',
      'Dr. Carlos Oliveira',
      'Dra. Ana Costa',
      'Dr. Pedro Lima'
    ],
    datasets: [{
      data: [156, 142, 128, 115, 98]
    }]
  },
  
  // Dados de receita acumulada
  receitaAcumulada: {
    labels: [
      'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
      'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
    ],
    datasets: [{
      label: 'Receita Acumulada',
      data: [4500, 5200, 4800, 6100, 5500, 6700, 7200, 6800, 7500, 8200, 7800, 8900]
    }]
  },
  
  // Dados de conversão de status
  conversaoStatus: {
    labels: [
      'Agendado',
      'Confirmado',
      'Realizado',
      'Cancelado',
      'Faltou'
    ],
    datasets: [{
      data: [120, 98, 85, 12, 8]
    }]
  },
  
  // Dados de horários populares
  horariosPopulares: {
    labels: [
      '08:00', '09:00', '10:00', '11:00', '12:00',
      '13:00', '14:00', '15:00', '16:00', '17:00'
    ],
    datasets: [{
      label: 'Agendamentos',
      data: [15, 28, 35, 42, 18, 22, 45, 52, 38, 25]
    }]
  },
  
  // Estatísticas gerais
  estatisticasGerais: {
    agendamentos_mes: 89,
    receita_mes: 8900.00,
    taxa_faltas: 8.5,
    total_pacientes: 342,
    total_profissionais: 8,
    total_agendamentos: 756
  },
  
  // Dados de comparação mensal
  comparacaoMensal: {
    labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
    datasets: [
      {
        label: 'Este Ano',
        data: [45, 52, 48, 61, 55, 67],
        borderColor: '#0d6efd',
        backgroundColor: 'rgba(13, 110, 253, 0.1)'
      },
      {
        label: 'Ano Passado',
        data: [38, 45, 42, 55, 48, 58],
        borderColor: '#6c757d',
        backgroundColor: 'rgba(108, 117, 125, 0.1)'
      }
    ]
  },
  
  // Dados de receita por profissional
  receitaPorProfissional: [
    { nome: 'Dr. João Silva', total: 15600.00, consultas: 156 },
    { nome: 'Dra. Maria Santos', total: 14200.00, consultas: 142 },
    { nome: 'Dr. Carlos Oliveira', total: 12800.00, consultas: 128 },
    { nome: 'Dra. Ana Costa', total: 11500.00, consultas: 115 },
    { nome: 'Dr. Pedro Lima', total: 9800.00, consultas: 98 }
  ],
  
  // Dados de crescimento de pacientes
  crescimentoPacientes: {
    labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
    datasets: [{
      label: 'Novos Pacientes',
      data: [12, 18, 15, 22, 19, 25],
      borderColor: '#198754',
      backgroundColor: 'rgba(25, 135, 84, 0.1)'
    }]
  },
  
  // Dados de satisfação
  satisfacao: {
    labels: ['Muito Satisfeito', 'Satisfeito', 'Neutro', 'Insatisfeito', 'Muito Insatisfeito'],
    datasets: [{
      data: [65, 25, 8, 2, 0],
      backgroundColor: [
        '#198754', '#20c997', '#ffc107', '#fd7e14', '#dc3545'
      ]
    }]
  },
  
  // Dados de serviços mais procurados
  servicosPopulares: {
    labels: ['Consulta', 'Exame', 'Procedimento', 'Avaliação', 'Retorno'],
    datasets: [{
      label: 'Quantidade',
      data: [45, 28, 15, 12, 8],
      backgroundColor: [
        '#0d6efd', '#198754', '#ffc107', '#6f42c1', '#fd7e14'
      ]
    }]
  },
  
  // Dados de tempo médio de atendimento
  tempoAtendimento: {
    labels: ['Dr. João', 'Dra. Maria', 'Dr. Carlos', 'Dra. Ana', 'Dr. Pedro'],
    datasets: [{
      label: 'Minutos',
      data: [25, 30, 28, 22, 35],
      backgroundColor: 'rgba(13, 110, 253, 0.8)'
    }]
  },
  
  // Dados de ocupação por dia da semana
  ocupacaoSemanal: {
    labels: ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'],
    datasets: [{
      label: 'Agendamentos',
      data: [18, 22, 20, 25, 23, 12],
      backgroundColor: [
        '#0d6efd', '#198754', '#ffc107', '#6f42c1', '#fd7e14', '#6c757d'
      ]
    }]
  },
  
  // Dados de retorno de pacientes
  retornoPacientes: {
    labels: ['1ª Consulta', '2ª Consulta', '3ª Consulta', '4ª+ Consulta'],
    datasets: [{
      label: 'Pacientes',
      data: [120, 85, 62, 45],
      backgroundColor: [
        '#0d6efd', '#198754', '#ffc107', '#6f42c1'
      ]
    }]
  },
  
  // Dados de cancelamentos por motivo
  cancelamentosMotivo: {
    labels: ['Horário Inconveniente', 'Problema de Saúde', 'Compromisso Pessoal', 'Esqueceu', 'Outros'],
    datasets: [{
      data: [8, 3, 2, 4, 1],
      backgroundColor: [
        '#ffc107', '#dc3545', '#6c757d', '#fd7e14', '#6f42c1'
      ]
    }]
  },
  
  // Dados de eficiência por período
  eficienciaPeriodo: {
    labels: ['Manhã (8-12h)', 'Tarde (13-17h)', 'Noite (18-20h)'],
    datasets: [{
      label: 'Eficiência (%)',
      data: [92, 88, 85],
      backgroundColor: [
        '#198754', '#ffc107', '#fd7e14'
      ]
    }]
  }
};

// Função para gerar dados aleatórios para demonstração
function generateRandomData(baseData, variation = 0.2) {
  return baseData.map(value => {
    const randomFactor = 1 + (Math.random() - 0.5) * variation;
    return Math.round(value * randomFactor);
  });
}

// Função para atualizar dados de exemplo
function updateSampleData() {
  // Atualizar agendamentos mensais com variação
  SampleData.agendamentosMensal.datasets[0].data = generateRandomData(
    SampleData.agendamentosMensal.datasets[0].data
  );
  
  // Atualizar receita acumulada
  SampleData.receitaAcumulada.datasets[0].data = generateRandomData(
    SampleData.receitaAcumulada.datasets[0].data
  );
  
  // Atualizar estatísticas gerais
  SampleData.estatisticasGerais.agendamentos_mes = 
    SampleData.agendamentosMensal.datasets[0].data[SampleData.agendamentosMensal.datasets[0].data.length - 1];
  
  SampleData.estatisticasGerais.receita_mes = 
    SampleData.receitaAcumulada.datasets[0].data[SampleData.receitaAcumulada.datasets[0].data.length - 1] * 100;
}

// Função para obter dados de exemplo por tipo
function getSampleData(type) {
  switch (type) {
    case 'agendamentos-mensal':
      return SampleData.agendamentosMensal;
    case 'profissionais-ranking':
      return SampleData.profissionaisRanking;
    case 'receita-acumulada':
      return SampleData.receitaAcumulada;
    case 'conversao-status':
      return SampleData.conversaoStatus;
    case 'horarios-populares':
      return SampleData.horariosPopulares;
    case 'estatisticas-gerais':
      return SampleData.estatisticasGerais;
    case 'comparacao-mensal':
      return SampleData.comparacaoMensal;
    case 'crescimento-pacientes':
      return SampleData.crescimentoPacientes;
    case 'satisfacao':
      return SampleData.satisfacao;
    case 'servicos-populares':
      return SampleData.servicosPopulares;
    case 'tempo-atendimento':
      return SampleData.tempoAtendimento;
    case 'ocupacao-semanal':
      return SampleData.ocupacaoSemanal;
    case 'retorno-pacientes':
      return SampleData.retornoPacientes;
    case 'cancelamentos-motivo':
      return SampleData.cancelamentosMotivo;
    case 'eficiencia-periodo':
      return SampleData.eficienciaPeriodo;
    default:
      return null;
  }
}

// Função para simular dados em tempo real
function simulateRealTimeData() {
  setInterval(() => {
    updateSampleData();
    
    // Disparar evento de dados atualizados
    const event = new CustomEvent('sampleDataUpdated', {
      detail: { timestamp: new Date(), data: SampleData }
    });
    document.dispatchEvent(event);
  }, 30000); // Atualizar a cada 30 segundos
}

// Exportar para uso global
window.SampleData = SampleData;
window.getSampleData = getSampleData;
window.updateSampleData = updateSampleData;
window.simulateRealTimeData = simulateRealTimeData;

// Inicializar simulação quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
  // Iniciar simulação de dados em tempo real
  simulateRealTimeData();
  
  console.log('📊 Dados de exemplo carregados com sucesso!');
  console.log('💡 Use getSampleData("tipo") para acessar dados específicos');
  console.log('🔄 Dados são atualizados automaticamente a cada 30 segundos');
});
