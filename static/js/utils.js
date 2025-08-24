/**
 * Utilitários para o Sistema Clínica
 * Funções auxiliares e helpers
 */

const Utils = {
  // Formatação de moeda brasileira
  formatCurrency: (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value || 0);
  },
  
  // Formatação de data brasileira
  formatDate: (date, options = {}) => {
    const defaultOptions = {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    if (typeof date === 'string') {
      date = new Date(date);
    }
    
    return new Intl.DateTimeFormat('pt-BR', finalOptions).format(date);
  },
  
  // Formatação de data e hora
  formatDateTime: (date) => {
    return Utils.formatDate(date, {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  },
  
  // Formatação de porcentagem
  formatPercentage: (value, decimals = 1) => {
    return `${(value || 0).toFixed(decimals)}%`;
  },
  
  // Formatação de números grandes
  formatNumber: (value) => {
    return new Intl.NumberFormat('pt-BR').format(value || 0);
  },
  
  // Capitalizar primeira letra
  capitalize: (str) => {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
  },
  
  // Truncar texto
  truncate: (str, length = 50) => {
    if (!str || str.length <= length) return str;
    return str.substring(0, length) + '...';
  },
  
  // Debounce para otimizar chamadas de função
  debounce: (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },
  
  // Throttle para limitar frequência de chamadas
  throttle: (func, limit) => {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  },
  
  // Validação de email
  isValidEmail: (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },
  
  // Validação de CPF
  isValidCPF: (cpf) => {
    cpf = cpf.replace(/[^\d]/g, '');
    
    if (cpf.length !== 11) return false;
    
    // Verificar se todos os dígitos são iguais
    if (/^(\d)\1+$/.test(cpf)) return false;
    
    // Validar primeiro dígito verificador
    let sum = 0;
    for (let i = 0; i < 9; i++) {
      sum += parseInt(cpf.charAt(i)) * (10 - i);
    }
    let remainder = (sum * 10) % 11;
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cpf.charAt(9))) return false;
    
    // Validar segundo dígito verificador
    sum = 0;
    for (let i = 0; i < 10; i++) {
      sum += parseInt(cpf.charAt(i)) * (11 - i);
    }
    remainder = (sum * 10) % 11;
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cpf.charAt(10))) return false;
    
    return true;
  },
  
  // Validação de telefone brasileiro
  isValidPhone: (phone) => {
    const phoneRegex = /^\(?[1-9]{2}\)? ?(?:[2-8]|9[1-9])[0-9]{3}\-?[0-9]{4}$/;
    return phoneRegex.test(phone);
  },
  
  // Mascarar CPF
  maskCPF: (cpf) => {
    cpf = cpf.replace(/\D/g, '');
    cpf = cpf.replace(/(\d{3})(\d)/, '$1.$2');
    cpf = cpf.replace(/(\d{3})(\d)/, '$1.$2');
    cpf = cpf.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
    return cpf;
  },
  
  // Mascarar telefone
  maskPhone: (phone) => {
    phone = phone.replace(/\D/g, '');
    phone = phone.replace(/(\d{2})(\d)/, '($1) $2');
    phone = phone.replace(/(\d{5})(\d)/, '$1-$2');
    return phone;
  },
  
  // Mascarar CEP
  maskCEP: (cep) => {
    cep = cep.replace(/\D/g, '');
    cep = cep.replace(/(\d{5})(\d)/, '$1-$2');
    return cep;
  },
  
  // Gerar ID único
  generateId: () => {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  },
  
  // Converter string para slug
  toSlug: (str) => {
    return str
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)/g, '');
  },
  
  // Verificar se é dispositivo móvel
  isMobile: () => {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  },
  
  // Verificar se está online
  isOnline: () => {
    return navigator.onLine;
  },
  
  // Copiar texto para clipboard
  copyToClipboard: async (text) => {
    try {
      if (navigator.clipboard) {
        await navigator.clipboard.writeText(text);
        return true;
      } else {
        // Fallback para navegadores mais antigos
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        return true;
      }
    } catch (err) {
      console.error('Erro ao copiar para clipboard:', err);
      return false;
    }
  },
  
  // Download de arquivo
  downloadFile: (data, filename, type = 'text/plain') => {
    const blob = new Blob([data], { type });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  },
  
  // Exportar dados como CSV
  exportToCSV: (data, filename = 'export.csv') => {
    if (!Array.isArray(data) || data.length === 0) return;
    
    const headers = Object.keys(data[0]);
    const csvContent = [
      headers.join(','),
      ...data.map(row => 
        headers.map(header => {
          const value = row[header];
          // Escapar vírgulas e aspas
          if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
            return `"${value.replace(/"/g, '""')}"`;
          }
          return value;
        }).join(',')
      )
    ].join('\n');
    
    Utils.downloadFile(csvContent, filename, 'text/csv');
  },
  
  // Local Storage com expiração
  storage: {
    set: (key, value, ttl = null) => {
      const item = {
        value,
        timestamp: Date.now(),
        ttl
      };
      localStorage.setItem(key, JSON.stringify(item));
    },
    
    get: (key) => {
      const item = localStorage.getItem(key);
      if (!item) return null;
      
      try {
        const parsed = JSON.parse(item);
        if (parsed.ttl && Date.now() - parsed.timestamp > parsed.ttl) {
          localStorage.removeItem(key);
          return null;
        }
        return parsed.value;
      } catch {
        return null;
      }
    },
    
    remove: (key) => {
      localStorage.removeItem(key);
    },
    
    clear: () => {
      localStorage.clear();
    }
  },
  
  // Session Storage
  session: {
    set: (key, value) => {
      sessionStorage.setItem(key, JSON.stringify(value));
    },
    
    get: (key) => {
      try {
        const item = sessionStorage.getItem(key);
        return item ? JSON.parse(item) : null;
      } catch {
        return null;
      }
    },
    
    remove: (key) => {
      sessionStorage.removeItem(key);
    },
    
    clear: () => {
      sessionStorage.clear();
    }
  },
  
  // Cookies
  cookies: {
    set: (name, value, days = 7) => {
      const expires = new Date();
      expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
      document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/`;
    },
    
    get: (name) => {
      const nameEQ = name + "=";
      const ca = document.cookie.split(';');
      for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
      }
      return null;
    },
    
    remove: (name) => {
      document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`;
    }
  }
};

// Funções globais para compatibilidade
window.Utils = Utils;

// Funções de formatação globais
window.formatCurrency = Utils.formatCurrency;
window.formatDate = Utils.formatDate;
window.formatDateTime = Utils.formatDateTime;
window.formatPercentage = Utils.formatPercentage;
window.formatNumber = Utils.formatNumber;
