"""
Módulo de Integração do Analytics
Conecta o módulo de analytics com o sistema principal
"""

from flask import Blueprint
from .routes import analytics_bp
from .models import db as analytics_db

def init_analytics(app, db):
    """
    Inicializa o módulo de analytics no sistema principal
    
    Args:
        app: Instância do Flask
        db: Instância do SQLAlchemy do sistema principal
    """
    
    # Registrar blueprint
    app.register_blueprint(analytics_bp)
    
    # Configurar banco de dados
    analytics_db.init_app(app)
    
    # Criar tabelas se não existirem
    with app.app_context():
        analytics_db.create_all()
    
    print("✅ Módulo de Analytics inicializado com sucesso!")
    
    # Registrar rotas no menu principal (se necessário)
    register_menu_items(app)

def register_menu_items(app):
    """Registra itens do menu para o analytics"""
    
    # Esta função pode ser usada para adicionar itens ao menu principal
    # Por exemplo, adicionar a aba "Analytics" no menu de navegação
    
    # Por enquanto, o menu já está configurado no template base.html
    # mas você pode usar esta função para configurações dinâmicas
    
    pass

def get_analytics_summary():
    """
    Retorna um resumo das métricas principais para exibir no dashboard principal
    
    Returns:
        dict: Dicionário com métricas resumidas
    """
    try:
        from .services import analytics_service
        
        # Calcular métricas básicas
        metricas = analytics_service.calcular_metricas_gerais()
        
        return {
            'taxa_presenca': metricas['presenca']['taxa'],
            'consultas_hoje': metricas.get('consultas_hoje', 0),
            'faturamento_mes': metricas.get('faturamento_mes', 0),
            'pacientes_ativos': metricas['participantes']['pacientes_unicos']
        }
        
    except Exception as e:
        print(f"Erro ao obter resumo do analytics: {e}")
        return {
            'taxa_presenca': 0,
            'consultas_hoje': 0,
            'faturamento_mes': 0,
            'pacientes_ativos': 0
        }

def get_analytics_alerts():
    """
    Retorna alertas importantes do analytics para exibir no sistema principal
    
    Returns:
        list: Lista de alertas
    """
    try:
        from .models import InsightAutomatico
        from datetime import date
        
        # Buscar insights críticos não lidos
        alertas = InsightAutomatico.query.filter(
            InsightAutomatico.prioridade.in_(['alta', 'critica']),
            InsightAutomatico.lido == False
        ).limit(5).all()
        
        return [
            {
                'id': alerta.id,
                'titulo': alerta.titulo,
                'descricao': alerta.descricao,
                'prioridade': alerta.prioridade,
                'tipo': alerta.tipo
            }
            for alerta in alertas
        ]
        
    except Exception as e:
        print(f"Erro ao obter alertas do analytics: {e}")
        return []

def get_analytics_quick_stats():
    """
    Retorna estatísticas rápidas para widgets no dashboard principal
    
    Returns:
        dict: Dicionário com estatísticas
    """
    try:
        from .services import analytics_service
        
        # Estatísticas básicas
        stats = {
            'total_agendamentos_hoje': 0,
            'taxa_presenca_hoje': 0,
            'faturamento_hoje': 0,
            'pacientes_unicos_hoje': 0
        }
        
        # Aqui você implementaria a lógica para buscar estatísticas rápidas
        # Por enquanto, retorna valores padrão
        
        return stats
        
    except Exception as e:
        print(f"Erro ao obter estatísticas rápidas: {e}")
        return {
            'total_agendamentos_hoje': 0,
            'taxa_presenca_hoje': 0,
            'faturamento_hoje': 0,
            'pacientes_unicos_hoje': 0
        }

# Função para verificar se o módulo está funcionando
def health_check():
    """
    Verifica se o módulo de analytics está funcionando corretamente
    
    Returns:
        dict: Status do módulo
    """
    try:
        from .services import analytics_service
        
        return {
            'status': 'healthy',
            'module': 'analytics',
            'version': '1.0.0',
            'services': [
                'calcular_metricas_gerais',
                'calcular_taxa_presenca_detalhada',
                'calcular_consultas_por_especialidade',
                'calcular_receita_mensal_profissional',
                'calcular_crescimento_pacientes',
                'treinar_modelo_falta',
                'prever_falta',
                'gerar_insights_automaticos'
            ],
            'modelo_treinado': analytics_service.modelo_treinado
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'module': 'analytics',
            'error': str(e),
            'version': '1.0.0'
        }

# Função para obter informações de configuração
def get_config_info():
    """
    Retorna informações sobre a configuração do módulo
    
    Returns:
        dict: Informações de configuração
    """
    try:
        from .models import get_config
        
        return {
            'auto_insights': get_config('analytics_auto_insights', False),
            'modelo_auto_treino': get_config('analytics_modelo_auto_treino', False),
            'relatorios_auto': get_config('analytics_relatorios_auto', False),
            'email_admin': get_config('analytics_email_admin', False)
        }
        
    except Exception as e:
        print(f"Erro ao obter configurações: {e}")
        return {
            'auto_insights': False,
            'modelo_auto_treino': False,
            'relatorios_auto': False,
            'email_admin': False
        }

# Função para executar tarefas de manutenção
def maintenance_tasks():
    """
    Executa tarefas de manutenção do módulo analytics
    
    Returns:
        dict: Resultado das tarefas
    """
    try:
        from .services import analytics_service
        
        results = {}
        
        # Atualizar métricas em tempo real
        try:
            analytics_service.atualizar_metricas_tempo_real()
            results['metricas_tempo_real'] = 'success'
        except Exception as e:
            results['metricas_tempo_real'] = f'error: {str(e)}'
        
        # Gerar insights automáticos (se configurado)
        try:
            from .models import get_config
            if get_config('analytics_auto_insights', False):
                insights = analytics_service.gerar_insights_automaticos()
                results['insights_automaticos'] = f'success: {len(insights)} insights gerados'
            else:
                results['insights_automaticos'] = 'skipped: não configurado'
        except Exception as e:
            results['insights_automaticos'] = f'error: {str(e)}'
        
        # Treinar modelo (se configurado)
        try:
            from .models import get_config
            if get_config('analytics_modelo_auto_treino', False):
                if analytics_service.treinar_modelo_falta():
                    results['treinamento_modelo'] = 'success'
                else:
                    results['treinamento_modelo'] = 'skipped: dados insuficientes'
            else:
                results['treinamento_modelo'] = 'skipped: não configurado'
        except Exception as e:
            results['treinamento_modelo'] = f'error: {str(e)}'
        
        return {
            'status': 'completed',
            'results': results,
            'timestamp': '2024-01-15T10:00:00Z'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': '2024-01-15T10:00:00Z'
        }

# Função para obter estatísticas de uso
def get_usage_stats():
    """
    Retorna estatísticas de uso do módulo analytics
    
    Returns:
        dict: Estatísticas de uso
    """
    try:
        from .models import (
            AnalyticsHistorico, InsightAutomatico, 
            PrevisaoFalta, RelatorioAgendado
        )
        
        # Contar registros em cada tabela
        stats = {
            'metricas_historicas': AnalyticsHistorico.query.count(),
            'insights_gerados': InsightAutomatico.query.count(),
            'previsoes_realizadas': PrevisaoFalta.query.count(),
            'relatorios_agendados': RelatorioAgendado.query.count()
        }
        
        # Adicionar estatísticas de insights por prioridade
        insights_por_prioridade = {}
        for prioridade in ['baixa', 'normal', 'alta', 'critica']:
            count = InsightAutomatico.query.filter_by(prioridade=prioridade).count()
            insights_por_prioridade[prioridade] = count
        
        stats['insights_por_prioridade'] = insights_por_prioridade
        
        return stats
        
    except Exception as e:
        print(f"Erro ao obter estatísticas de uso: {e}")
        return {
            'metricas_historicas': 0,
            'insights_gerados': 0,
            'previsoes_realizadas': 0,
            'relatorios_agendados': 0,
            'insights_por_prioridade': {}
        }
