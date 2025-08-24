# 🏆 Sistema de Gamificação - Sistema Clínica

## 📋 Visão Geral

O Sistema de Gamificação é um módulo completo e independente que implementa mecânicas de engajamento para pacientes e profissionais da clínica. O sistema utiliza pontos, badges, rankings e conquistas para motivar o uso consistente e reduzir faltas.

## ✨ Funcionalidades Principais

### 🎯 Para Pacientes
- **Sistema de Pontos Automático:**
  - +10 pontos ao confirmar presença na consulta
  - +5 pontos ao comparecer na consulta
  - -10 pontos em caso de falta sem aviso
  - +3 pontos ao reagendar com antecedência

- **Badges Especiais:**
  - 🕐 **Paciente Pontual**: 5 consultas seguidas sem faltas
  - 👑 **Paciente Fiel**: 10 consultas realizadas
  - 🎯 **Zero Faltas**: 30 dias sem ausências

- **Ranking e Estatísticas:**
  - Pontuação acumulada visível no perfil
  - Ranking geral de pacientes
  - Estatísticas de comparecimento

### 👨‍⚕️ Para Profissionais
- **Ranking por Desempenho:**
  - Baseado no número de consultas realizadas
  - Pontos extras para baixa taxa de faltas (< 5%)

- **Badges Especiais:**
  - 🏆 **Top do Mês**: Maior receita mensal
  - 📅 **Super Agenda**: Mais consultas realizadas

### 🎨 Interface do Usuário
- Nova aba "Gamificação" no menu principal
- Rankings separados para pacientes e profissionais
- Lista de badges conquistados
- Interface com cores diferenciadas (azul/cinza base, dourado/prata/bronze para badges)
- Animações ao desbloquear conquistas

### 🚀 Funcionalidades Inovadoras
- **Notificações WhatsApp** automáticas ao desbloquear badges
- **Linha do tempo** de conquistas no perfil
- **Gamificação integrada** aos relatórios
- **Sistema de níveis** baseado em pontos acumulados

## 🏗️ Arquitetura do Sistema

### 📁 Estrutura de Arquivos
```
gamification/
├── __init__.py              # Inicialização do módulo
├── models.py                # Modelos de banco de dados
├── points_system.py         # Sistema de pontuação
├── services.py              # Serviços de gamificação
├── routes.py                # Rotas e endpoints
├── migrate.py               # Script de migração
└── README.md                # Esta documentação
```

### 🗄️ Modelos de Banco de Dados

#### `UserPoints`
- Armazena pontos e estatísticas dos usuários
- Rastreia consultas realizadas/perdidas
- Mantém sequências de comparecimento

#### `Badge`
- Define badges disponíveis no sistema
- Configura requisitos e recompensas
- Suporte a diferentes raridades (comum, raro, épico, lendário)

#### `UserBadge`
- Registra badges conquistados pelos usuários
- Controla notificações enviadas

#### `PointsTransaction`
- Histórico completo de transações de pontos
- Metadados para auditoria

#### `Achievement`
- Conquistas e marcos dos usuários
- Sistema de progressão

#### `Leaderboard`
- Rankings atualizados periodicamente
- Suporte a diferentes períodos (diário, semanal, mensal)

#### `GamificationEvent`
- Auditoria completa de eventos
- Dados para análise e relatórios

## 🚀 Instalação e Configuração

### 1. Pré-requisitos
- Python 3.7+
- Flask + SQLAlchemy
- Banco de dados PostgreSQL/SQLite
- Sistema de notificações WhatsApp (opcional)

### 2. Executar Migração
```bash
cd gamification
python migrate.py
```

### 3. Registrar Blueprint
No arquivo principal da aplicação (`app/__init__.py`):
```python
from gamification.routes import gamification_bp

def register_blueprints(app):
    # ... outros blueprints ...
    app.register_blueprint(gamification_bp)
```

### 4. Configurar Notificações (Opcional)
Para notificações WhatsApp automáticas:
```python
# Em services.py, configure o serviço WhatsApp
if hasattr(current_app, 'whatsapp_service'):
    current_app.whatsapp_service.send_message(...)
```

## 📱 Rotas Disponíveis

### 🔐 Rotas Protegidas (Login Obrigatório)
- `/gamification/` - Página principal
- `/gamification/profile` - Perfil detalhado do usuário
- `/gamification/leaderboard` - Rankings e classificações
- `/gamification/badges` - Badges disponíveis e conquistados

### 🔧 Rotas Administrativas
- `/gamification/admin/stats` - Estatísticas gerais (apenas admin)
- `/gamification/admin/reset-points/<user_id>` - Reset de pontos (apenas admin)

### 📡 APIs
- `/gamification/api/profile` - Dados do perfil em JSON
- `/gamification/api/leaderboard` - Rankings em JSON
- `/gamification/api/badges` - Badges em JSON
- `/gamification/api/stats` - Estatísticas em JSON
- `/gamification/api/award-points` - Conceder pontos (POST)

## 🎮 Como Usar o Sistema

### Para Pacientes
1. **Acesse a aba "Gamificação"** no menu principal
2. **Visualize seu progresso** na página principal
3. **Acompanhe seus badges** conquistados
4. **Compare-se no ranking** com outros pacientes
5. **Veja próximas metas** para desbloquear novos badges

### Para Profissionais
1. **Acesse o sistema de gamificação**
2. **Monitore seu desempenho** e ranking
3. **Acompanhe badges** relacionados à produtividade
4. **Analise estatísticas** de atendimento

### Para Administradores
1. **Acesse estatísticas gerais** em `/gamification/admin/stats`
2. **Monitore atividade** do sistema
3. **Exporte relatórios** em diferentes formatos
4. **Gerencie pontos** dos usuários se necessário

## 🔧 Personalização

### Adicionar Novos Badges
```python
# Em services.py, método _create_default_badges()
new_badge = {
    'code': 'novo_badge',
    'name': 'Nome do Badge',
    'description': 'Descrição do badge',
    'icon': '🎯',
    'category': 'attendance',
    'user_type': 'patient',
    'requirement_type': 'count',
    'requirement_value': 15,
    'points_reward': 150,
    'color': 'success',
    'rarity': 'rare'
}
```

### Modificar Regras de Pontuação
```python
# Em points_system.py, método _calculate_points()
if user_type == 'patient':
    patient_rules = {
        'confirm_presence': 15,      # Alterar de 10 para 15
        'attend_appointment': 8,     # Alterar de 5 para 8
        'miss_appointment': -15,     # Alterar de -10 para -15
        'reschedule_advance': 5      # Alterar de 3 para 5
    }
```

### Configurar Notificações
```python
# Em services.py, método _send_badge_notification()
# Personalizar mensagem de notificação
message = f"🎉 Parabéns! Você desbloqueou o badge '{badge['name']}'!"
message += f"\n\n{badge['description']}"
message += f"\n\nRecompensa: +{badge['points_reward']} pontos"
```

## 📊 Relatórios e Analytics

### Estatísticas Disponíveis
- Total de usuários por tipo
- Badges concedidos por categoria
- Pontos totais distribuídos
- Atividade recente do sistema
- Rankings por período

### Exportação de Dados
- **PDF**: Relatórios formatados
- **CSV**: Dados estruturados
- **Excel**: Planilhas com gráficos
- **JSON**: Dados para integração

## 🧪 Testes

### Executar Testes Básicos
```bash
# Testar criação de tabelas
python migrate.py

# Testar rotas (com servidor rodando)
curl http://localhost:5000/gamification/api/stats
```

### Testar Sistema de Pontos
```bash
# Simular concessão de pontos
curl -X POST http://localhost:5000/gamification/api/award-points \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "user_type": "patient",
    "action": "attend_appointment",
    "action_data": {"appointment_id": 123}
  }'
```

## 🔒 Segurança

### Controles de Acesso
- Todas as rotas requerem autenticação
- Rotas administrativas verificam papel de admin
- Validação de dados em todas as APIs
- Auditoria completa de ações

### Validações
- Verificação de tipos de usuário
- Validação de ações permitidas
- Controle de pontuação negativa
- Prevenção de duplicação de badges

## 🚨 Troubleshooting

### Problemas Comuns

#### Tabelas não criadas
```bash
# Executar migração novamente
python migrate.py
```

#### Erro de importação
```bash
# Verificar se o módulo está no PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/caminho/para/projeto"
```

#### Badges não aparecem
```bash
# Verificar se os badges foram criados
python -c "from gamification.models import Badge; print(Badge.query.count())"
```

#### Pontos não são concedidos
- Verificar se a ação está definida em `_calculate_points()`
- Confirmar se o usuário existe no sistema
- Verificar logs de erro

### Logs e Debug
```python
# Habilitar logs detalhados
import logging
logging.basicConfig(level=logging.DEBUG)

# Verificar estado do sistema
from gamification.services import GamificationService
service = GamificationService(db)
stats = service.get_gamification_stats()
print(stats)
```

## 🔮 Roadmap e Melhorias

### Próximas Versões
- [ ] Sistema de missões diárias
- [ ] Gamificação por especialidade médica
- [ ] Integração com redes sociais
- [ ] Sistema de recompensas físicas
- [ ] Analytics avançados com gráficos interativos

### Sugestões de Melhorias
- Implementar WebSockets para atualizações em tempo real
- Adicionar sistema de convites e referências
- Criar desafios sazonais (Natal, Ano Novo, etc.)
- Implementar sistema de clãs/equipes

## 📞 Suporte

### Documentação
- Este README
- Código comentado
- Exemplos de uso

### Contato
- Criar issue no repositório
- Consultar logs de erro
- Verificar configurações do sistema

## 📄 Licença

Este módulo é parte do Sistema Clínica e segue as mesmas políticas de licenciamento do projeto principal.

---

**🎉 Parabéns! Você agora tem um sistema de gamificação completo e funcional!**

Para começar a usar, execute `python migrate.py` e acesse `/gamification/` na sua aplicação.
