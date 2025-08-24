# Sistema Clínica - Notificações WhatsApp & Automação

## 📱 Visão Geral

Sistema completo de notificações automáticas via WhatsApp para clínicas médicas, incluindo lembretes de consultas, confirmações automáticas e integração com APIs profissionais.

## 🚀 Funcionalidades Implementadas

### 1. **Sistema de Notificações Automáticas**
- **Confirmação Imediata**: Após agendamento de consulta
- **Lembrete 24h**: Um dia antes da consulta
- **Lembrete 1h**: Uma hora antes da consulta
- **Lembrete Adicional**: Se não confirmar em 6h
- **Agradecimento**: Após consulta realizada
- **Sugestão de Reagendamento**: Após falta

### 2. **Integração WhatsApp**
- **Twilio WhatsApp API**: Integração profissional
- **WhatsApp Web**: Alternativa via Node.js
- **Modo Simulação**: Para desenvolvimento e testes
- **Webhook**: Recebimento de respostas dos pacientes

### 3. **Agendador de Tarefas**
- **Agendamento Automático**: Lembretes baseados em cron
- **Retry Inteligente**: Tentativas automáticas em caso de falha
- **Rate Limiting**: Controle de envio para evitar spam
- **Monitoramento**: Status e estatísticas das tarefas

### 4. **Templates Personalizáveis**
- **Mensagens Humanizadas**: Tom profissional e acolhedor
- **Variáveis Dinâmicas**: Nome, data, horário, profissional
- **Edição Visual**: Interface para personalizar mensagens
- **Teste de Envio**: Validação antes de usar em produção

### 5. **Dashboard de Controle**
- **Estatísticas em Tempo Real**: Taxa de entrega, respostas
- **Histórico Completo**: Todas as notificações enviadas
- **Filtros Avançados**: Por tipo, status, data
- **Exportação de Dados**: CSV e logs para análise

## 🛠️ Arquitetura Técnica

### **Estrutura de Módulos**
```
services/
├── __init__.py              # Módulo principal
├── notificacoes.py          # Gerenciador de notificações
├── whatsapp.py              # Serviço WhatsApp
└── agendador.py             # Agendador de tarefas

templates/
└── notificacoes.html        # Interface de controle

static/js/
└── notificacoes.js          # JavaScript da interface
```

### **Fluxo de Funcionamento**
1. **Agendamento Criado** → Notificação imediata + Lembretes agendados
2. **Agendador Executa** → Envia lembretes nos horários programados
3. **Paciente Responde** → Webhook recebe e processa resposta
4. **Sistema Atualiza** → Status e histórico atualizados
5. **Ações Automáticas** → Confirmação, reagendamento ou cancelamento

### **APIs Suportadas**
- **Twilio WhatsApp**: API oficial e confiável
- **WhatsApp Web**: Alternativa gratuita (Node.js)
- **Simulação**: Para desenvolvimento e testes

## 📋 Configuração e Instalação

### **1. Instalar Dependências**
```bash
pip install -r requirements_notificacoes.txt
```

### **2. Configurar Variáveis de Ambiente**
```bash
# Twilio (opcional)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# WhatsApp Web (opcional)
WHATSAPP_WEB_ENABLED=true
WHATSAPP_WEB_SESSION_PATH=/path/to/session

# Configurações Gerais
NOTIFICACOES_ATIVAS=true
LEMBRETE_24H_HORARIO=18:00
LEMBRETE_1H_ATIVO=true
```

### **3. Configurar Webhook**
```python
# Em services/whatsapp.py
webhook_url = "https://sua-clinica.com/webhook/whatsapp"
webhook_token = "seu_token_secreto"
```

### **4. Iniciar Sistema**
```python
from services.notificacoes import GerenciadorNotificacoes
from services.agendador import AgendadorTarefas

# Inicializar gerenciador
gerenciador = GerenciadorNotificacoes()

# Inicializar agendador
agendador = AgendadorTarefas()
agendador.definir_gerenciador_notificacoes(gerenciador)
agendador.iniciar()
```

## 🎯 Casos de Uso

### **1. Agendamento de Consulta**
```python
# Quando uma consulta é criada
agendamento = {
    'id': 123,
    'paciente_id': 456,
    'telefone_paciente': '+5511999999999',
    'data': '2025-01-20',
    'horario': '14:00',
    'profissional': 'Dr. João Silva',
    'especialidade': 'Clínico Geral'
}

# Enviar confirmação imediata
gerenciador.notificar_agendamento_criado(agendamento)

# Agendar lembretes automáticos
agendador.agendar_lembrete_agendamento(agendamento)
```

### **2. Processamento de Resposta**
```python
# Via webhook do WhatsApp
resposta = gerenciador.processar_resposta_paciente(
    telefone='+5511999999999',
    mensagem='SIM'
)

# Resposta: {'acao': 'confirmar_presenca', 'mensagem': 'Presença confirmada!'}
```

### **3. Envio de Resumo Diário**
```python
# Para profissionais
agendador.agendar_resumo_diario_profissional(
    profissional_id=789,
    data='2025-01-20'
)
```

## 📊 Monitoramento e Estatísticas

### **Métricas Disponíveis**
- **Taxa de Entrega**: % de mensagens recebidas
- **Taxa de Resposta**: % de pacientes que respondem
- **Confirmações**: Número de presenças confirmadas
- **Reagendamentos**: Solicitações de novo horário
- **Cancelamentos**: Consultas canceladas

### **Logs e Debug**
```python
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Logs automáticos para todas as operações
logger.info("Notificação enviada para +5511999999999")
logger.error("Falha no envio: Rate limit atingido")
```

## 🔒 Segurança e Compliance

### **Proteções Implementadas**
- **Rate Limiting**: Máximo 30 mensagens/minuto, 1000/hora
- **Validação de Telefone**: Formato internacional obrigatório
- **Token de Webhook**: Validação de requisições
- **Logs de Auditoria**: Rastreamento completo de ações

### **LGPD Compliance**
- **Consentimento**: Pacientes devem aceitar notificações
- **Dados Mínimos**: Apenas informações essenciais
- **Retenção**: Histórico limitado a 30 dias
- **Exclusão**: Direito ao esquecimento

## 🚀 Funcionalidades Futuras

### **1. Inteligência Artificial**
- **Análise de Sentimento**: Respostas dos pacientes
- **Predição de Faltas**: Machine Learning para otimização
- **Chatbot Inteligente**: Respostas automáticas avançadas

### **2. Integrações**
- **Telegram**: Alternativa ao WhatsApp
- **SMS**: Fallback para números não WhatsApp
- **Email**: Comunicações formais
- **Push Notifications**: App mobile

### **3. Automação Avançada**
- **Workflows Personalizados**: Regras de negócio específicas
- **Integração CRM**: Sincronização com sistemas externos
- **API Pública**: Para integrações de terceiros

## 🧪 Testes e Qualidade

### **Testes Automatizados**
```bash
# Executar testes
pytest tests/test_notificacoes.py

# Cobertura de código
pytest --cov=services tests/
```

### **Testes Manuais**
1. **Modo Simulação**: Testar sem enviar mensagens reais
2. **Sandbox Twilio**: Ambiente de desenvolvimento
3. **WhatsApp Web**: Teste com número pessoal

## 📞 Suporte e Manutenção

### **Monitoramento**
- **Health Checks**: Verificação automática de serviços
- **Alertas**: Notificações para problemas críticos
- **Métricas**: Dashboard de performance

### **Manutenção**
- **Backup Automático**: Configurações e histórico
- **Atualizações**: Versões mensais com melhorias
- **Documentação**: Atualização contínua

## 🔧 Troubleshooting

### **Problemas Comuns**

#### **1. Mensagens não sendo enviadas**
```python
# Verificar conectividade
resultado = whatsapp_service.testar_conectividade()
print(resultado)

# Verificar rate limit
status = whatsapp_service.obter_estatisticas_envio()
print(status)
```

#### **2. Webhook não recebendo mensagens**
```python
# Verificar configuração
webhook_url = whatsapp_service.webhook_url
print(f"Webhook configurado: {webhook_url}")

# Testar endpoint
import requests
response = requests.post(webhook_url, json={'test': 'data'})
print(f"Status: {response.status_code}")
```

#### **3. Agendador não executando tarefas**
```python
# Verificar status
estatisticas = agendador.obter_estatisticas()
print(f"Agendador executando: {estatisticas['agendador_executando']}")

# Verificar tarefas
tarefas = agendador.obter_tarefas()
for tarefa in tarefas:
    print(f"Tarefa: {tarefa['nome']} - Status: {tarefa['status']}")
```

## 📚 Recursos Adicionais

### **Documentação**
- [Twilio WhatsApp API](https://www.twilio.com/docs/whatsapp)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)
- [Expressões Cron](https://crontab.guru/)

### **Comunidade**
- **GitHub Issues**: Reportar bugs e solicitar features
- **Discord**: Suporte em tempo real
- **Documentação**: Wiki com exemplos práticos

---

**Sistema Clínica - Notificações WhatsApp**  
Transformando comunicação em engajamento e resultados mensuráveis. 🚀📱

*Desenvolvido com ❤️ para melhorar a experiência de pacientes e profissionais.*





