# 📊 Módulo de Analytics Avançados

Sistema de insights inteligentes e previsões automáticas para o Sistema Clínica.

## 🚀 Funcionalidades

### 📈 Dashboard Interativo
- **KPIs Principais**: Taxa de presença, consultas realizadas, faturamento, pacientes ativos
- **Gráficos Interativos**: Usando Plotly para visualizações avançadas
- **Filtros Dinâmicos**: Por período, paciente, profissional, especialidade
- **Métricas em Tempo Real**: Atualização automática de dados

### 🤖 Inteligência Artificial
- **Previsão de Faltas**: Modelo Random Forest treinado com dados históricos
- **Insights Automáticos**: Análise automática de padrões e tendências
- **Detecção de Riscos**: Identificação de pacientes em risco de abandono
- **Horários Críticos**: Análise de horários com alta taxa de problemas

### 📊 Relatórios Avançados
- **Relatórios Rápidos**: Taxa de presença, especialidades, receita, crescimento
- **Relatórios Personalizados**: Filtros avançados e configurações específicas
- **Agendamento Automático**: Envio programado de relatórios por email
- **Exportação**: PDF e Excel com gráficos incluídos

### ⚙️ Configurações
- **Configurações Gerais**: Ativação de funcionalidades automáticas
- **Parâmetros de IA**: Limiares de risco e frequência de treinamento
- **Configurações de Relatórios**: Formatos e horários padrão
- **Configurações de Alertas**: Limiares para notificações automáticas

## 🏗️ Arquitetura

### Estrutura de Pastas
```
analytics/
├── __init__.py              # Inicialização do módulo
├── models.py                # Modelos de dados
├── services.py              # Lógica de negócio e IA
├── routes.py                # Rotas da API
├── integration.py           # Integração com sistema principal
├── README.md               # Esta documentação
└── templates/              # Templates HTML
    ├── dashboard.html      # Dashboard principal
    ├── relatorios.html     # Página de relatórios
    └── configuracoes.html  # Página de configurações
```

### Modelos de Dados
- **AnalyticsConfig**: Configurações do sistema
- **AnalyticsHistorico**: Histórico de métricas
- **RelatorioAgendado**: Relatórios programados
- **PrevisaoFalta**: Previsões de IA
- **InsightAutomatico**: Insights gerados automaticamente
- **MetricaTempoReal**: Métricas em tempo real

### Serviços
- **AnalyticsService**: Serviço principal com todas as funcionalidades
- **Modelo de IA**: Random Forest para previsão de faltas
- **Geração de Insights**: Análise automática de dados
- **Cálculo de Métricas**: Estatísticas e indicadores

## 🛠️ Instalação

### 1. Dependências
O módulo requer as seguintes bibliotecas Python:
```bash
pip install scikit-learn pandas numpy plotly
```

### 2. Integração com Sistema Principal
```python
from analytics.integration import init_analytics

# No arquivo principal da aplicação
init_analytics(app, db)
```

### 3. Configuração do Banco
As tabelas são criadas automaticamente na inicialização.

## 📱 Uso

### Dashboard Principal
Acesse `/analytics/` para o dashboard principal com:
- KPIs em tempo real
- Gráficos interativos
- Insights automáticos
- Previsões de IA

### Relatórios
Acesse `/analytics/relatorios` para:
- Relatórios rápidos
- Relatórios personalizados
- Agendamento de relatórios
- Histórico de relatórios

### Configurações
Acesse `/analytics/configuracoes` para:
- Configurações gerais
- Parâmetros de IA
- Configurações de relatórios
- Configurações de alertas

## 🔌 APIs

### Métricas
- `GET /analytics/api/metricas-gerais` - Métricas gerais do sistema
- `GET /analytics/api/taxa-presenca` - Taxa de presença detalhada
- `GET /analytics/api/consultas-especialidade` - Consultas por especialidade
- `GET /analytics/api/receita-mensal` - Receita mensal por profissional
- `GET /analytics/api/crescimento-pacientes` - Crescimento de pacientes

### IA e Insights
- `POST /analytics/api/treinar-modelo` - Treinar modelo de IA
- `POST /analytics/api/prever-falta` - Prever falta de agendamento
- `POST /analytics/api/gerar-insights` - Gerar insights automáticos
- `GET /analytics/api/insights` - Listar insights disponíveis

### Relatórios
- `POST /analytics/api/exportar-relatorio` - Exportar relatório
- `GET /analytics/api/configuracoes` - Obter configurações
- `POST /analytics/api/configuracoes` - Salvar configurações

## 🎨 Personalização

### Cores e Temas
O módulo segue o esquema de cores do sistema principal:
- **Azul**: `#0d6efd` (primário)
- **Verde**: `#28a745` (sucesso)
- **Amarelo**: `#ffc107` (aviso)
- **Vermelho**: `#dc3545` (perigo)
- **Cinza**: `#6c757d` (secundário)

### Dark Mode
Suporte completo ao modo escuro com variáveis CSS personalizáveis.

### Responsividade
Interface totalmente responsiva para dispositivos móveis e desktop.

## 🔒 Segurança

### Permissões
- Acesso restrito a usuários autenticados
- Verificação de permissões por role
- Proteção contra acesso não autorizado

### Validação de Dados
- Validação de entrada em todas as APIs
- Sanitização de dados
- Proteção contra injeção SQL

## 📊 Métricas e Performance

### Indicadores de Performance
- **Tempo de Resposta**: < 500ms para APIs básicas
- **Cache**: Sistema de cache para métricas frequentes
- **Processamento em Lote**: Operações pesadas em background
- **Otimização de Consultas**: Queries otimizadas para grandes volumes

### Monitoramento
- Logs detalhados de operações
- Métricas de uso do sistema
- Alertas automáticos para problemas
- Dashboard de saúde do sistema

## 🚨 Troubleshooting

### Problemas Comuns

#### 1. Modelo de IA não treina
**Sintoma**: Erro "dados insuficientes para treinamento"
**Solução**: Verificar se há pelo menos 100 agendamentos no sistema

#### 2. Gráficos não carregam
**Sintoma**: Área de gráfico vazia
**Solução**: Verificar se Plotly está carregado e console para erros JavaScript

#### 3. Métricas não atualizam
**Sintoma**: KPIs mostram valores antigos
**Solução**: Verificar se as tarefas de atualização estão rodando

#### 4. Erro de banco de dados
**Sintoma**: Erro 500 ao acessar analytics
**Solução**: Verificar se as tabelas foram criadas e conexão com banco

### Logs
Os logs são salvos em:
- Console da aplicação
- Arquivo de log do sistema (se configurado)
- Banco de dados (para auditoria)

## 🔮 Roadmap

### Versão 1.1
- [ ] Integração com WhatsApp para notificações
- [ ] Relatórios em tempo real
- [ ] Dashboard mobile otimizado
- [ ] Mais algoritmos de IA

### Versão 1.2
- [ ] Machine Learning avançado
- [ ] Análise de sentimentos
- [ ] Integração com APIs externas
- [ ] Sistema de alertas push

### Versão 2.0
- [ ] IA conversacional
- [ ] Análise preditiva avançada
- [ ] Integração com BI tools
- [ ] API GraphQL

## 🤝 Contribuição

### Como Contribuir
1. Fork o repositório
2. Crie uma branch para sua feature
3. Implemente as mudanças
4. Adicione testes
5. Faça commit e push
6. Abra um Pull Request

### Padrões de Código
- PEP 8 para Python
- ESLint para JavaScript
- Documentação em português
- Testes unitários obrigatórios

## 📞 Suporte

### Contato
- **Email**: suporte@clinica.com
- **Documentação**: Este README
- **Issues**: GitHub Issues

### Recursos Adicionais
- [Documentação da API](https://docs.clinica.com/analytics)
- [Vídeos Tutoriais](https://youtube.com/clinica)
- [Comunidade](https://forum.clinica.com)

## 📄 Licença

Este módulo é parte do Sistema Clínica e segue a mesma licença do projeto principal.

---

**Desenvolvido com ❤️ pela equipe do Sistema Clínica**

*Versão: 1.0.0 | Última atualização: Janeiro 2024*
