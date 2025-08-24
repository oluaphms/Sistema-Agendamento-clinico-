"""
Exemplo de Integração do Módulo Analytics
Mostra como integrar o módulo ao sistema principal
"""

# Exemplo de integração no arquivo principal (app.py ou run.py)

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from analytics.integration import init_analytics

# Criar aplicação Flask
app = Flask(__name__)

# Configurações
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinica.db'
app.config['SECRET_KEY'] = 'sua-chave-secreta'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# Importar modelos do sistema principal
from app import Usuario, Paciente, Profissional, Agendamento, Servico

# Inicializar módulo de analytics
init_analytics(app, db)

# Exemplo de uso das funcionalidades do analytics
@app.route('/dashboard-resumo')
def dashboard_resumo():
    """Dashboard resumido com métricas do analytics"""
    from analytics.integration import get_analytics_summary, get_analytics_alerts
    
    # Obter resumo das métricas
    resumo = get_analytics_summary()
    
    # Obter alertas importantes
    alertas = get_analytics_alerts()
    
    return {
        'resumo': resumo,
        'alertas': alertas,
        'status': 'success'
    }

@app.route('/analytics/health')
def analytics_health():
    """Verificar saúde do módulo analytics"""
    from analytics.integration import health_check
    
    return health_check()

@app.route('/analytics/stats')
def analytics_stats():
    """Estatísticas de uso do módulo analytics"""
    from analytics.integration import get_usage_stats
    
    return get_usage_stats()

@app.route('/analytics/maintenance')
def analytics_maintenance():
    """Executar tarefas de manutenção"""
    from analytics.integration import maintenance_tasks
    
    return maintenance_tasks()

# Exemplo de uso em outras rotas do sistema
@app.route('/pacientes/<int:paciente_id>/analytics')
def paciente_analytics(paciente_id):
    """Analytics específicos de um paciente"""
    from analytics.services import analytics_service
    
    # Buscar agendamentos do paciente
    agendamentos = Agendamento.query.filter_by(paciente_id=paciente_id).all()
    
    if not agendamentos:
        return {'error': 'Paciente não encontrado'}, 404
    
    # Calcular métricas específicas do paciente
    metricas_paciente = {
        'total_consultas': len(agendamentos),
        'consultas_realizadas': len([a for a in agendamentos if a.status == 'Realizado']),
        'consultas_faltas': len([a for a in agendamentos if a.status == 'Falta']),
        'taxa_presenca': 0
    }
    
    if metricas_paciente['total_consultas'] > 0:
        metricas_paciente['taxa_presenca'] = (
            metricas_paciente['consultas_realizadas'] / 
            metricas_paciente['total_consultas'] * 100
        )
    
    # Fazer previsão de falta para próximas consultas
    proximas_consultas = [
        a for a in agendamentos 
        if a.status == 'Agendado' and a.data >= '2024-01-15'
    ]
    
    previsoes = []
    for consulta in proximas_consultas:
        previsao = analytics_service.prever_falta(
            paciente_id, 
            consulta.id, 
            consulta.data, 
            consulta.hora
        )
        if previsao:
            previsoes.append({
                'data': consulta.data,
                'hora': consulta.hora,
                'probabilidade_falta': previsao['probabilidade_falta'],
                'nivel_risco': previsao['nivel_risco']
            })
    
    return {
        'paciente_id': paciente_id,
        'metricas': metricas_paciente,
        'previsoes': previsoes,
        'status': 'success'
    }

# Exemplo de middleware para analytics
@app.before_request
def analytics_middleware():
    """Middleware para capturar métricas de uso"""
    from analytics.models import registrar_metrica
    from datetime import date
    
    # Registrar métricas de uso (exemplo simplificado)
    if request.endpoint and 'analytics' not in request.endpoint:
        try:
            registrar_metrica(
                date.today(),
                'pagina_acessada',
                1,
                {'endpoint': request.endpoint, 'method': request.method}
            )
        except:
            pass  # Ignorar erros de analytics para não afetar o sistema principal

# Exemplo de tarefa agendada
def tarefa_analytics_diaria():
    """Tarefa diária para atualizar métricas e gerar insights"""
    from analytics.integration import maintenance_tasks
    
    try:
        resultado = maintenance_tasks()
        print(f"Tarefa de analytics executada: {resultado}")
    except Exception as e:
        print(f"Erro na tarefa de analytics: {e}")

# Exemplo de configuração automática
def configurar_analytics_padrao():
    """Configurar analytics com valores padrão"""
    from analytics.models import set_config
    
    configs_padrao = {
        'analytics_auto_insights': True,
        'analytics_modelo_auto_treino': True,
        'analytics_relatorios_auto': True,
        'analytics_email_admin': False
    }
    
    for chave, valor in configs_padrao.items():
        set_config(chave, valor, 'bool', f'Configuração padrão para {chave}')

# Exemplo de uso em templates
@app.context_processor
def analytics_context():
    """Injetar dados do analytics nos templates"""
    def get_analytics_widget_data():
        """Dados para widgets do analytics no dashboard principal"""
        try:
            from analytics.integration import get_analytics_summary, get_analytics_alerts
            
            return {
                'resumo': get_analytics_summary(),
                'alertas': get_analytics_alerts()[:3]  # Apenas 3 alertas
            }
        except:
            return {
                'resumo': {},
                'alertas': []
            }
    
    return {
        'analytics_widget': get_analytics_widget_data
    }

# Exemplo de uso em JavaScript
@app.route('/analytics/widget-data')
def analytics_widget_data():
    """API para widgets do analytics no dashboard principal"""
    from analytics.integration import get_analytics_summary, get_analytics_alerts
    
    return {
        'resumo': get_analytics_summary(),
        'alertas': get_analytics_alerts(),
        'status': 'success'
    }

# Exemplo de integração com sistema de notificações
def notificar_insights_importantes():
    """Notificar administradores sobre insights importantes"""
    from analytics.models import InsightAutomatico
    from analytics.integration import get_config
    
    # Verificar se notificações estão ativadas
    if not get_config('analytics_email_admin', False):
        return
    
    # Buscar insights críticos não lidos
    insights_criticos = InsightAutomatico.query.filter(
        InsightAutomatico.prioridade.in_(['alta', 'critica']),
        InsightAutomatico.lido == False
    ).limit(5).all()
    
    if insights_criticos:
        # Aqui você implementaria o envio de email
        print(f"Notificando sobre {len(insights_criticos)} insights críticos")
        
        for insight in insights_criticos:
            print(f"⚠️ {insight.titulo}: {insight.descricao}")

# Exemplo de uso em relatórios existentes
@app.route('/relatorio-completo')
def relatorio_completo():
    """Relatório completo incluindo dados do analytics"""
    from analytics.services import analytics_service
    
    # Dados básicos do sistema
    dados_basicos = {
        'usuarios': Usuario.query.count(),
        'pacientes': Paciente.query.count(),
        'profissionais': Profissional.query.count(),
        'agendamentos': Agendamento.query.count()
    }
    
    # Dados do analytics
    try:
        metricas_gerais = analytics_service.calcular_metricas_gerais()
        taxa_presenca = analytics_service.calcular_taxa_presenca_detalhada()
        consultas_especialidade = analytics_service.calcular_consultas_por_especialidade()
        
        dados_analytics = {
            'metricas_gerais': metricas_gerais,
            'taxa_presenca': taxa_presenca,
            'consultas_especialidade': consultas_especialidade
        }
    except Exception as e:
        dados_analytics = {'error': str(e)}
    
    return {
        'dados_basicos': dados_basicos,
        'analytics': dados_analytics,
        'status': 'success'
    }

if __name__ == '__main__':
    # Configurar analytics padrão
    with app.app_context():
        configurar_analytics_padrao()
    
    # Executar aplicação
    app.run(debug=True)
