# Sistema de Gestão de Agenda Clínica - Versão Melhorada

Sistema completo para gestão de clínicas médicas com funcionalidades avançadas de segurança, notificações e relatórios.

## 🚀 Funcionalidades Principais

### 🎯 Menu Vivo (NOVO!)
- **Menu Lateral Inteligente**: Transforma o menu em um painel lateral com gráficos dinâmicos
- **Gráfico em Tempo Real**: Visualização de agendamentos do dia com atualização automática
- **Busca Global**: Pesquisa inteligente em pacientes, profissionais e serviços
- **Mini Dashboard**: Cards com métricas importantes (próximos agendamentos, receita)
- **Responsivo**: Adaptação automática para desktop, tablet e mobile
- **Atalhos de Teclado**: Ctrl/Cmd + B para toggle, Ctrl/Cmd + K para busca

### ✅ Gestão de Agendamentos
- Agendamento de consultas com verificação de conflitos de horário
- Calendário visual interativo
- Status de agendamentos (Agendado, Confirmado, Realizado, Cancelado, Falta)
- Controle de duração de serviços

### ✅ Gestão de Usuários
- Sistema de roles (Admin, Recepção, Profissional)
- Autenticação segura com hash de senhas
- Controle de acesso baseado em permissões

### ✅ Gestão de Pacientes
- Cadastro completo de pacientes
- Histórico médico (prontuário)
- Contatos e informações pessoais

### ✅ Gestão de Profissionais
- Cadastro de profissionais de saúde
- Controle de horários de disponibilidade
- Especialidades médicas

### ✅ Gestão de Serviços
- Cadastro de serviços oferecidos
- Controle de preços e duração
- Vinculação com profissionais

## 🔒 Melhorias de Segurança Implementadas

### Autenticação Robusta
- Hash seguro de senhas com Werkzeug
- Validação de força de senha
- Autenticação de dois fatores (2FA) com QR Code
- Rate limiting para prevenir ataques de força bruta

### Proteção contra Ataques
- Sanitização de entrada para prevenir XSS
- Validação de dados de entrada
- Tokens CSRF para formulários
- Headers de segurança com Flask-Talisman

### Validação de Dados
- Validação de formato de email
- Validação de telefone brasileiro
- Sanitização de texto para evitar injeção de código

## 📧 Sistema de Notificações

### Email
- Confirmação automática de agendamentos
- Lembretes 24h antes da consulta
- Notificações de cancelamento
- Templates HTML responsivos

### WhatsApp (Opcional)
- Integração com WhatsApp Business API
- Mensagens automáticas para pacientes
- Confirmações e lembretes

## 📊 Relatórios Avançados

### Formato PDF
- Relatórios de agendamentos
- Relatórios financeiros
- Relatórios gerais da clínica
- Layout profissional com cores e estilos

### Formato Excel
- Planilhas organizadas e formatadas
- Múltiplas abas para diferentes tipos de dados
- Cálculos automáticos e estatísticas

## 🧪 Testando o Menu Vivo

### Páginas de Demonstração
- **`test_live_menu.html`**: Página completa de teste com todas as funcionalidades
- **`demo_live_menu.html`**: Demonstração simples e elegante
- **`templates/live_menu.html`**: Template principal do Menu Vivo

### Como Testar
1. **Abra qualquer página** do sistema (o Menu Vivo está integrado ao template base)
2. **Clique no botão do menu** (☰) no header superior
3. **Explore as funcionalidades**:
   - Navegue pelas opções
   - Use a busca global
   - Visualize o gráfico dinâmico
   - Teste os atalhos de teclado (Ctrl/Cmd + B, Ctrl/Cmd + K)

### Funcionalidades para Testar
- ✅ **Toggle do Menu**: Abrir/fechar com animações suaves
- ✅ **Gráfico Dinâmico**: Atualização automática a cada 30 segundos
- ✅ **Busca Global**: Pesquisa em tempo real
- ✅ **Responsividade**: Teste em diferentes tamanhos de tela
- ✅ **Atalhos**: Use Ctrl/Cmd + B para toggle, ESC para fechar

## 🛠️ Instalação e Configuração

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd sistema-clinica
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
Copie o arquivo `env_example.txt` para `.env` e configure:
```bash
# Configurações de Segurança
SECRET_KEY=sua-chave-secreta-super-segura-aqui
FLASK_ENV=production
FLASK_DEBUG=False

# Configurações de Email (para notificações)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-app

# Configurações de WhatsApp Business API (opcional)
WHATSAPP_API_KEY=sua-chave-api-whatsapp
WHATSAPP_PHONE_NUMBER=seu-numero-whatsapp
```

### 5. Execute o sistema
```bash
python app.py
```

Acesse: http://127.0.0.1:5000

**Login padrão:** admin / admin123

## 🧪 Executando Testes

### Instalar pytest
```bash
pip install pytest
```

### Executar todos os testes
```bash
pytest tests.py -v
```

### Executar testes específicos
```bash
pytest tests.py::TestSecurity -v
pytest tests.py::TestNotifications -v
pytest tests.py::TestReports -v
```

## 📱 Uso do Sistema

### 1. Primeiro Acesso
- Faça login com as credenciais padrão
- **IMPORTANTE:** Altere a senha do admin imediatamente
- Configure autenticação de dois fatores (recomendado)

### 2. Configuração Inicial
- Cadastre profissionais de saúde
- Configure serviços oferecidos
- Defina horários de disponibilidade

### 3. Operação Diária
- Cadastre pacientes
- Faça agendamentos
- Gerencie status de consultas
- Acesse prontuários

### 4. Relatórios
- Gere relatórios em PDF ou Excel
- Analise dados financeiros
- Monitore estatísticas da clínica

## 🔧 Configurações Avançadas

### Banco de Dados
O sistema usa SQLite por padrão. Para produção, considere migrar para:
- PostgreSQL (recomendado)
- MySQL
- SQL Server

### Email
Configure um servidor SMTP para notificações:
- Gmail (com senha de app)
- Outlook/Office 365
- Servidor próprio

### WhatsApp Business API
Para notificações via WhatsApp:
1. Crie uma conta no WhatsApp Business API
2. Obtenha a chave de API
3. Configure o número de telefone

## 📈 Melhorias Futuras Sugeridas

### Performance
- Implementar cache Redis
- Otimizar consultas do banco
- Paginação de resultados

### Interface
- Frontend em React/Vue.js
- Design responsivo para mobile
- PWA (Progressive Web App)

### Funcionalidades
- Sistema de faturamento
- Integração com planos de saúde
- Telemedicina
- App mobile para pacientes

## 🚨 Segurança em Produção

### Configurações Obrigatórias
```bash
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=chave-aleatoria-muito-segura
SESSION_COOKIE_SECURE=True
```

### Recomendações
- Use HTTPS em produção
- Configure firewall adequado
- Faça backups regulares
- Monitore logs de acesso
- Atualize dependências regularmente

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação
2. Execute os testes para verificar funcionamento
3. Consulte os logs da aplicação
4. Abra uma issue no repositório

## 📄 Licença

Este projeto é de uso livre para fins educacionais e comerciais.

---

**Desenvolvido com ❤️ para melhorar a gestão de clínicas médicas**
