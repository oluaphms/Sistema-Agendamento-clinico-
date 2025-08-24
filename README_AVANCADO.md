# 🏥 Sistema de Clínica Avançado - Versão 2.0

## 🚀 Visão Geral

Sistema completo de gerenciamento de clínica médica com funcionalidades avançadas de IA, integrações externas, gamificação e telemedicina. Desenvolvido em Python com Flask, mantendo toda a estrutura existente e adicionando recursos modernos.

## ✨ Funcionalidades Implementadas

### 🔐 **Sistema Base (Mantido)**
- ✅ Autenticação e controle de acesso por roles
- ✅ Gestão de pacientes, profissionais e serviços
- ✅ Sistema de agendamentos com verificação de conflitos
- ✅ Prontuários e relatórios básicos
- ✅ Exportação de dados em CSV

### 🆕 **Funcionalidades Avançadas (Novas)**

#### 🤖 **Inteligência Artificial e Chatbot**
- Chatbot inteligente com OpenAI GPT
- Processamento de linguagem natural (NLP)
- Análise de intenção das mensagens
- Sugestões inteligentes para agendamentos
- Dicas de saúde personalizadas

#### 📱 **Integrações Externas**
- **WhatsApp Business API**: Confirmações automáticas, lembretes e suporte
- **Google Calendar**: Sincronização bidirecional de agendamentos
- **Google Sheets**: Exportação automática de dados
- **WebSockets**: Notificações em tempo real

#### 🎮 **Sistema de Gamificação**
- Pontos para pacientes e profissionais
- Badges e conquistas por metas atingidas
- Ranking e leaderboards
- Desafios mensais
- Sistema de níveis

#### 🏥 **Telemedicina**
- Agendamentos com link de vídeo
- Sessões de consulta online
- Integração com OpenTok (configurável)
- Controle de acesso por permissões

#### 📊 **Analytics e Business Intelligence**
- Dashboard executivo com KPIs em tempo real
- Gráficos interativos com Plotly
- Análise de receita por período
- Estatísticas de agendamentos
- Relatórios avançados

#### 🔔 **Notificações Inteligentes**
- Notificações em tempo real via WebSockets
- Alertas para novos agendamentos
- Lembretes automáticos
- Notificações de emergência
- Chat em tempo real entre equipe

## 🛠️ Tecnologias Utilizadas

### **Backend**
- **Python 3.8+**
- **Flask 2.3.3** - Framework web
- **Flask-SQLAlchemy** - ORM para banco de dados
- **Flask-SocketIO** - WebSockets para tempo real
- **Flask-CORS** - Cross-origin resource sharing

### **Banco de Dados**
- **SQLite** (desenvolvimento)
- **PostgreSQL/MySQL** (produção)

### **APIs e Integrações**
- **OpenAI GPT** - Chatbot inteligente
- **WhatsApp Business API** - Comunicação
- **Google APIs** - Calendar e Sheets
- **OpenTok** - Telemedicina

### **Frontend**
- **Bootstrap 5** - Interface responsiva
- **FullCalendar** - Calendário interativo
- **Plotly** - Gráficos avançados
- **Socket.IO** - Comunicação em tempo real

### **Ferramentas de Desenvolvimento**
- **Celery** - Tarefas assíncronas
- **Redis** - Cache e filas
- **Docker** - Containerização

## 📋 Pré-requisitos

### **Sistema**
- Python 3.8 ou superior
- Redis (para cache e WebSockets)
- Git

### **APIs Externas (Opcionais)**
- OpenAI API Key
- WhatsApp Business API
- Google Cloud Platform
- OpenTok (para telemedicina)

## 🚀 Instalação

### **1. Clone o Repositório**
```bash
git clone <url-do-repositorio>
cd sistema-clinica-avancado
```

### **2. Crie um Ambiente Virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### **3. Instale as Dependências**
```bash
pip install -r requirements.txt
```

### **4. Configure as Variáveis de Ambiente**
```bash
# Copie o arquivo de exemplo
cp env_example.txt .env

# Edite o arquivo .env com suas configurações
nano .env
```

### **5. Configure o Banco de Dados**
```bash
# O banco será criado automaticamente na primeira execução
# Para produção, configure DATABASE_URL no .env
```

### **6. Execute o Sistema**
```bash
# Versão básica (original)
python app.py

# Versão avançada (com todas as funcionalidades)
python app_advanced.py
```

## ⚙️ Configuração

### **Variáveis de Ambiente Principais**

```env
# Configurações Básicas
SECRET_KEY=sua-chave-secreta-aqui
DATABASE_URL=sqlite:///clinica.db

# OpenAI (Chatbot)
OPENAI_API_KEY=sua-openai-api-key

# WhatsApp Business API
WHATSAPP_API_KEY=sua-api-key-whatsapp
WHATSAPP_PHONE_NUMBER_ID=seu-phone-number-id
WHATSAPP_ACCESS_TOKEN=seu-access-token-whatsapp

# Google APIs
GOOGLE_CLIENT_ID=seu-google-client-id
GOOGLE_CLIENT_SECRET=seu-google-client-secret
GOOGLE_CALENDAR_ID=seu-calendar-id

# Telemedicina
OPENTOK_API_KEY=sua-opentok-api-key
OPENTOK_API_SECRET=sua-opentok-api-secret
```

### **Configuração do WhatsApp Business API**

1. Acesse [Facebook Developers](https://developers.facebook.com/)
2. Crie um app para WhatsApp Business
3. Configure o webhook: `https://seudominio.com/whatsapp/webhook`
4. Adicione as credenciais no arquivo `.env`

### **Configuração do Google APIs**

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um projeto e ative as APIs:
   - Google Calendar API
   - Google Sheets API
3. Configure OAuth 2.0
4. Adicione as credenciais no arquivo `.env`

## 🎯 Como Usar

### **1. Acesso Inicial**
- URL: `http://localhost:5000`
- Usuário: `admin`
- Senha: `admin123`

### **2. Dashboard Avançado**
- KPIs em tempo real
- Gráficos interativos
- Perfil gamificado
- Notificações instantâneas

### **3. Chatbot Inteligente**
- Acesse via API: `POST /chatbot`
- Integrado com WhatsApp
- Suporte automático para pacientes

### **4. Telemedicina**
- Acesse: `/telemedicina/<id_agendamento>`
- Sessões de vídeo integradas
- Controle de acesso por permissões

### **5. Gamificação**
- Sistema de pontos automático
- Badges por conquistas
- Ranking de usuários
- Desafios mensais

## 🔧 Desenvolvimento

### **Estrutura de Arquivos**
```
sistema-clinica-avancado/
├── app.py                          # Versão original
├── app_advanced.py                 # Versão com todas as funcionalidades
├── config.py                       # Configurações
├── requirements.txt                # Dependências
├── integrations/                   # Módulos de integração
│   ├── whatsapp.py                # WhatsApp Business API
│   └── google.py                  # Google APIs
├── ai/                            # Inteligência Artificial
│   └── chatbot.py                 # Chatbot OpenAI
├── websockets/                     # WebSockets
│   └── notifications.py           # Sistema de notificações
├── gamification/                   # Gamificação
│   └── points_system.py           # Sistema de pontos
├── templates/                      # Templates HTML
└── static/                         # Arquivos estáticos
```

### **Adicionando Novas Funcionalidades**

1. **Crie um novo módulo** na pasta apropriada
2. **Importe no app_advanced.py**
3. **Adicione as rotas** necessárias
4. **Atualize os templates** se necessário
5. **Teste a funcionalidade**

### **Exemplo de Módulo Personalizado**
```python
# meu_modulo.py
class MeuModulo:
    def __init__(self):
        self.nome = "Meu Módulo"
    
    def executar_funcao(self):
        return "Função executada!"

# No app_advanced.py
from meu_modulo import MeuModulo
meu_modulo = MeuModulo()
```

## 🧪 Testes

### **Executar Testes Básicos**
```bash
# Teste de conectividade
python -c "import app_advanced; print('Sistema carregado com sucesso!')"

# Teste do banco de dados
python -c "from app_advanced import db; print('Banco conectado!')"
```

### **Teste das Funcionalidades**
1. **Login**: Teste acesso com diferentes roles
2. **Chatbot**: Envie mensagens via API
3. **WebSockets**: Verifique notificações em tempo real
4. **Integrações**: Teste WhatsApp e Google (se configurado)

## 🚀 Deploy em Produção

### **1. Configuração de Produção**
```bash
# Altere para produção
export FLASK_ENV=production
export FLASK_CONFIG=production
```

### **2. Usando Gunicorn**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app_advanced:app
```

### **3. Usando Docker**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app_advanced.py"]
```

### **4. Configuração de Proxy Reverso (Nginx)**
```nginx
server {
    listen 80;
    server_name sua-clinica.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /socket.io {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 📊 Monitoramento e Logs

### **Logs do Sistema**
```bash
# Logs em tempo real
tail -f logs/app.log

# Logs de erro
grep "ERROR" logs/app.log
```

### **Métricas de Performance**
- Tempo de resposta das APIs
- Uso de memória e CPU
- Conexões WebSocket ativas
- Taxa de sucesso das integrações

## 🔒 Segurança

### **Medidas Implementadas**
- ✅ Autenticação por sessão
- ✅ Controle de acesso por roles
- ✅ Validação de entrada
- ✅ Rate limiting
- ✅ CORS configurado
- ✅ Sanitização de dados

### **Recomendações de Produção**
- Use HTTPS
- Configure firewall
- Monitore logs de acesso
- Atualize dependências regularmente
- Use variáveis de ambiente para credenciais

## 🤝 Contribuição

### **Como Contribuir**
1. Fork o projeto
2. Crie uma branch para sua feature
3. Implemente as mudanças
4. Adicione testes se necessário
5. Envie um Pull Request

### **Padrões de Código**
- Use Python 3.8+ syntax
- Siga PEP 8
- Documente funções e classes
- Mantenha compatibilidade com estrutura existente

## 📞 Suporte

### **Canais de Suporte**
- **Issues**: Reporte bugs e solicite features
- **Documentação**: Este README e comentários no código
- **Comunidade**: Fórum de desenvolvedores

### **Problemas Comuns**

#### **Erro de Importação**
```bash
ModuleNotFoundError: No module named 'integrations'
```
**Solução**: Verifique se está executando do diretório raiz

#### **Erro de Conexão WebSocket**
```bash
WebSocket connection failed
```
**Solução**: Verifique se o Redis está rodando

#### **Erro de API Externa**
```bash
WhatsApp API error
```
**Solução**: Verifique as credenciais no arquivo `.env`

## 🔮 Roadmap Futuro

### **Versão 3.0 (Próximas Funcionalidades)**
- [ ] Machine Learning para previsão de demanda
- [ ] Blockchain para prontuários
- [ ] Realidade Aumentada para check-in
- [ ] Integração com planos de saúde
- [ ] App mobile nativo
- [ ] Analytics preditivos avançados

### **Melhorias Técnicas**
- [ ] Migração para FastAPI
- [ ] Implementação de GraphQL
- [ ] Microserviços
- [ ] Kubernetes deployment
- [ ] CI/CD pipeline

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- Comunidade Flask
- OpenAI pela API GPT
- Google pelas APIs
- WhatsApp Business API
- Contribuidores do projeto

---

**Desenvolvido com ❤️ para revolucionar a gestão de clínicas médicas**

*Para dúvidas ou suporte, abra uma issue no repositório.*
