/**
 * Configurações dos gráficos para o Sistema Clínica
 * Cores, estilos e opções padrão
 */

const ChartConfig = {
  // Cores padrão para os gráficos
  colors: {
    primary: '#0d6efd',
    success: '#198754',
    warning: '#ffc107',
    danger: '#dc3545',
    info: '#0dcaf0',
    secondary: '#6c757d',
    purple: '#6f42c1',
    orange: '#fd7e14',
    teal: '#20c997',
    pink: '#e83e8c'
  },
  
  // Gradientes para preenchimento
  gradients: {
    primary: 'rgba(13, 110, 253, 0.1)',
    success: 'rgba(25, 135, 84, 0.1)',
    warning: 'rgba(255, 193, 7, 0.1)',
    danger: 'rgba(220, 53, 69, 0.1)',
    info: 'rgba(13, 202, 240, 0.1)'
  },
  
  // Configurações padrão para todos os gráficos
  defaults: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          font: {
            size: 12,
            family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
          },
          padding: 20,
          usePointStyle: true
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0,0,0,0.8)',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        borderColor: '#0d6efd',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: false,
        titleFont: {
          size: 14,
          weight: 'bold'
        },
        bodyFont: {
          size: 12
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0,0,0,0.1)',
          drawBorder: false
        },
        ticks: {
          color: '#6c757d',
          font: {
            size: 12
          }
        }
      },
      x: {
        grid: {
          color: 'rgba(0,0,0,0.1)',
          drawBorder: false
        },
        ticks: {
          color: '#6c757d',
          font: {
            size: 12
          }
        }
      }
    }
  },
  
  // Configurações específicas para cada tipo de gráfico
  lineChart: {
    tension: 0.4,
    fill: true,
    pointBackgroundColor: '#0d6efd',
    pointBorderColor: '#ffffff',
    pointBorderWidth: 2,
    pointRadius: 6,
    pointHoverRadius: 8,
    borderWidth: 3
  },
  
  doughnutChart: {
    borderWidth: 2,
    borderColor: '#ffffff',
    hoverOffset: 4,
    cutout: '60%'
  },
  
  pieChart: {
    borderWidth: 2,
    borderColor: '#ffffff',
    hoverOffset: 4
  },
  
  barChart: {
    borderRadius: 5,
    borderSkipped: false,
    borderWidth: 0
  },
  
  // Paletas de cores para diferentes tipos de dados
  palettes: {
    // Para gráficos de profissionais
    profissionais: [
      '#0d6efd', '#198754', '#ffc107', '#dc3545', '#6f42c1',
      '#fd7e14', '#20c997', '#e83e8c', '#6c757d', '#0dcaf0'
    ],
    
    // Para gráficos de status
    status: [
      '#ffc107', '#0d6efd', '#198754', '#dc3545', '#6c757d'
    ],
    
    // Para gráficos de receita
    receita: [
      '#198754', '#20c997', '#0d6efd', '#0dcaf0', '#6f42c1'
    ],
    
    // Para gráficos de horários
    horarios: [
      '#0d6efd', '#198754', '#ffc107', '#dc3545', '#6f42c1',
      '#fd7e14', '#20c997', '#e83e8c', '#6c757d', '#0dcaf0',
      '#0d6efd', '#198754', '#ffc107', '#dc3545', '#6f42c1',
      '#fd7e14', '#20c997', '#e83e8c', '#6c757d', '#0dcaf0',
      '#0d6efd', '#198754', '#ffc107', '#dc3545', '#6f42c1',
      '#fd7e14', '#20c997', '#e83e8c', '#6c757d', '#0dcaf0'
    ]
  },
  
  // Animações personalizadas
  animations: {
    duration: 1000,
    easing: 'easeInOutQuart'
  },
  
  // Configurações de interação
  interaction: {
    intersect: false,
    mode: 'index'
  }
};

// Função para criar um gráfico de linha com configurações padrão
function createLineChart(ctx, data, options = {}) {
  const config = {
    type: 'line',
    data: {
      labels: data.labels || [],
      datasets: data.datasets.map(dataset => ({
        ...dataset,
        ...ChartConfig.lineChart,
        borderColor: dataset.borderColor || ChartConfig.colors.primary,
        backgroundColor: dataset.backgroundColor || ChartConfig.gradients.primary
      }))
    },
    options: {
      ...ChartConfig.defaults,
      ...options
    }
  };
  
  return new Chart(ctx, config);
}

// Função para criar um gráfico de rosca com configurações padrão
function createDoughnutChart(ctx, data, options = {}) {
  const config = {
    type: 'doughnut',
    data: {
      labels: data.labels || [],
      datasets: [{
        data: data.data || [],
        backgroundColor: data.backgroundColor || ChartConfig.palettes.profissionais,
        ...ChartConfig.doughnutChart
      }]
    },
    options: {
      ...ChartConfig.defaults,
      ...options
    }
  };
  
  return new Chart(ctx, config);
}

// Função para criar um gráfico de pizza com configurações padrão
function createPieChart(ctx, data, options = {}) {
  const config = {
    type: 'pie',
    data: {
      labels: data.labels || [],
      datasets: [{
        data: data.data || [],
        backgroundColor: data.backgroundColor || ChartConfig.palettes.status,
        ...ChartConfig.pieChart
      }]
    },
    options: {
      ...ChartConfig.defaults,
      ...options
    }
  };
  
  return new Chart(ctx, config);
}

// Função para criar um gráfico de barras com configurações padrão
function createBarChart(ctx, data, options = {}) {
  const config = {
    type: 'bar',
    data: {
      labels: data.labels || [],
      datasets: [{
        label: data.label || 'Dados',
        data: data.data || [],
        backgroundColor: data.backgroundColor || ChartConfig.palettes.horarios,
        ...ChartConfig.barChart
      }]
    },
    options: {
      ...ChartConfig.defaults,
      ...options
    }
  };
  
  return new Chart(ctx, config);
}

// Exportar para uso global
window.ChartConfig = ChartConfig;
window.createLineChart = createLineChart;
window.createDoughnutChart = createDoughnutChart;
window.createPieChart = createPieChart;
window.createBarChart = createBarChart;
