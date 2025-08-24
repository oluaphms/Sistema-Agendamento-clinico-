from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from datetime import datetime, date, timedelta
import json
import io
import os
from functools import wraps
from sqlalchemy import or_

# Importar serviços
from .services import analytics_service
from .models import (
    InsightAutomatico, MetricaTempoReal, RelatorioAgendado,
    get_config, set_config
)

# Blueprint do analytics
analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

# Decorator para verificar permissões
def require_analytics_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar se usuário está logado e tem acesso ao analytics
        # Esta verificação será feita pelo sistema principal
        return f(*args, **kwargs)
    return decorated_function

@analytics_bp.route('/')
@require_analytics_access
def dashboard():
    """Dashboard principal de analytics"""
    return render_template('analytics/dashboard.html', title="Analytics")

@analytics_bp.route('/api/metricas-gerais')
@require_analytics_access
def api_metricas_gerais():
    """API para métricas gerais"""
    try:
        # Parâmetros de filtro
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        if data_inicio:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        if data_fim:
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        
        metricas = analytics_service.calcular_metricas_gerais(data_inicio, data_fim)
        return jsonify({'success': True, 'data': metricas})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/taxa-presenca')
@require_analytics_access
def api_taxa_presenca():
    """API para taxa de presença detalhada"""
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        if data_inicio:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        if data_fim:
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        
        dados = analytics_service.calcular_taxa_presenca_detalhada(data_inicio, data_fim)
        return jsonify({'success': True, 'data': dados})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/consultas-especialidade')
@require_analytics_access
def api_consultas_especialidade():
    """API para consultas por especialidade"""
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        if data_inicio:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        if data_fim:
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        
        dados = analytics_service.calcular_consultas_por_especialidade(data_inicio, data_fim)
        return jsonify({'success': True, 'data': dados})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/receita-mensal')
@require_analytics_access
def api_receita_mensal():
    """API para receita mensal por profissional"""
    try:
        ano = request.args.get('ano', type=int)
        mes = request.args.get('mes', type=int)
        
        dados = analytics_service.calcular_receita_mensal_profissional(ano, mes)
        return jsonify({'success': True, 'data': dados})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/crescimento-pacientes')
@require_analytics_access
def api_crescimento_pacientes():
    """API para crescimento de pacientes"""
    try:
        meses = request.args.get('meses', 12, type=int)
        
        dados = analytics_service.calcular_crescimento_pacientes(meses)
        return jsonify({'success': True, 'data': dados})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/insights')
@require_analytics_access
def api_insights():
    """API para insights automáticos"""
    try:
        # Buscar insights não expirados
        hoje = date.today()
        insights = InsightAutomatico.query.filter(
            or_(
                InsightAutomatico.expira_em.is_(None),
                InsightAutomatico.expira_em >= hoje
            )
        ).order_by(InsightAutomatico.criado_em.desc()).limit(20).all()
        
        dados = []
        for insight in insights:
            dados.append({
                'id': insight.id,
                'tipo': insight.tipo,
                'titulo': insight.titulo,
                'descricao': insight.descricao,
                'dados': json.loads(insight.dados) if insight.dados else None,
                'prioridade': insight.prioridade,
                'lido': insight.lido,
                'criado_em': insight.criado_em.strftime('%Y-%m-%d %H:%M')
            })
        
        return jsonify({'success': True, 'data': dados})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/metricas-tempo-real')
@require_analytics_access
def api_metricas_tempo_real():
    """API para métricas em tempo real"""
    try:
        metricas = MetricaTempoReal.query.all()
        
        dados = {}
        for metrica in metricas:
            dados[metrica.chave] = {
                'valor': metrica.valor,
                'unidade': metrica.unidade,
                'status': metrica.status,
                'atualizado_em': metrica.atualizado_em.strftime('%Y-%m-%d %H:%M')
            }
        
        return jsonify({'success': True, 'data': dados})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/prever-falta', methods=['POST'])
@require_analytics_access
def api_prever_falta():
    """API para prever falta de um agendamento"""
    try:
        data = request.get_json()
        paciente_id = data.get('paciente_id')
        agendamento_id = data.get('agendamento_id')
        data_consulta = data.get('data')
        hora_consulta = data.get('hora')
        
        if not all([paciente_id, agendamento_id, data_consulta, hora_consulta]):
            return jsonify({'success': False, 'error': 'Dados incompletos'}), 400
        
        # Treinar modelo se necessário
        if not analytics_service.modelo_treinado:
            analytics_service.treinar_modelo_falta()
        
        # Fazer previsão
        previsao = analytics_service.prever_falta(
            paciente_id, agendamento_id, data_consulta, hora_consulta
        )
        
        if previsao:
            return jsonify({'success': True, 'data': previsao})
        else:
            return jsonify({'success': False, 'error': 'Não foi possível fazer a previsão'}), 400
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/treinar-modelo', methods=['POST'])
@require_analytics_access
def api_treinar_modelo():
    """API para treinar modelo de IA"""
    try:
        sucesso = analytics_service.treinar_modelo_falta()
        
        if sucesso:
            return jsonify({
                'success': True, 
                'message': 'Modelo treinado com sucesso',
                'modelo_treinado': True
            })
        else:
            return jsonify({
                'success': False, 
                'error': 'Não foi possível treinar o modelo',
                'modelo_treinado': False
            }), 400
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/gerar-insights', methods=['POST'])
@require_analytics_access
def api_gerar_insights():
    """API para gerar insights automáticos"""
    try:
        insights = analytics_service.gerar_insights_automaticos()
        
        return jsonify({
            'success': True, 
            'message': f'{len(insights)} insights gerados',
            'data': insights
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/atualizar-metricas', methods=['POST'])
@require_analytics_access
def api_atualizar_metricas():
    """API para atualizar métricas em tempo real"""
    try:
        sucesso = analytics_service.atualizar_metricas_tempo_real()
        
        if sucesso:
            return jsonify({'success': True, 'message': 'Métricas atualizadas'})
        else:
            return jsonify({'success': False, 'error': 'Erro ao atualizar métricas'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/marcar-insight-lido/<int:insight_id>', methods=['POST'])
@require_analytics_access
def api_marcar_insight_lido(insight_id):
    """API para marcar insight como lido"""
    try:
        insight = InsightAutomatico.query.get_or_404(insight_id)
        insight.lido = True
        insight.save()
        
        return jsonify({'success': True, 'message': 'Insight marcado como lido'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/relatorios')
@require_analytics_access
def relatorios():
    """Página de relatórios"""
    return render_template('analytics/relatorios.html', title="Relatórios")

@analytics_bp.route('/api/exportar-relatorio', methods=['POST'])
@require_analytics_access
def api_exportar_relatorio():
    """API para exportar relatórios"""
    try:
        data = request.get_json()
        tipo_relatorio = data.get('tipo')
        formato = data.get('formato', 'pdf')
        data_inicio = data.get('data_inicio')
        data_fim = data.get('data_fim')
        
        if not tipo_relatorio:
            return jsonify({'success': False, 'error': 'Tipo de relatório não especificado'}), 400
        
        # Converter datas
        if data_inicio:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        if data_fim:
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        
        # Gerar relatório baseado no tipo
        if tipo_relatorio == 'presenca':
            dados = analytics_service.calcular_taxa_presenca_detalhada(data_inicio, data_fim)
        elif tipo_relatorio == 'especialidade':
            dados = analytics_service.calcular_consultas_por_especialidade(data_inicio, data_fim)
        elif tipo_relatorio == 'receita':
            dados = analytics_service.calcular_receita_mensal_profissional()
        elif tipo_relatorio == 'crescimento':
            dados = analytics_service.calcular_crescimento_pacientes()
        else:
            return jsonify({'success': False, 'error': 'Tipo de relatório inválido'}), 400
        
        # Aqui você implementaria a geração do arquivo (PDF/Excel)
        # Por enquanto, retornamos os dados
        return jsonify({
            'success': True, 
            'message': 'Relatório gerado com sucesso',
            'dados': dados
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/configuracoes')
@require_analytics_access
def configuracoes():
    """Página de configurações do analytics"""
    return render_template('analytics/configuracoes.html', title="Configurações Analytics")

@analytics_bp.route('/api/configuracoes', methods=['GET', 'POST'])
@require_analytics_access
def api_configuracoes():
    """API para configurações do analytics"""
    if request.method == 'GET':
        try:
            # Buscar configurações
            configs = {}
            chaves = [
                'analytics_auto_insights',
                'analytics_modelo_auto_treino',
                'analytics_relatorios_auto',
                'analytics_email_admin'
            ]
            
            for chave in chaves:
                configs[chave] = get_config(chave, 'false')
            
            return jsonify({'success': True, 'data': configs})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Atualizar configurações
            for chave, valor in data.items():
                set_config(chave, valor, 'bool')
            
            return jsonify({'success': True, 'message': 'Configurações atualizadas'})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

# Rota para teste do módulo
@analytics_bp.route('/teste')
def teste():
    """Rota de teste para verificar se o módulo está funcionando"""
    return jsonify({
        'success': True,
        'message': 'Módulo de Analytics funcionando!',
        'versao': '1.0.0',
        'servicos_disponiveis': [
            'calcular_metricas_gerais',
            'calcular_taxa_presenca_detalhada',
            'calcular_consultas_por_especialidade',
            'calcular_receita_mensal_profissional',
            'calcular_crescimento_pacientes',
            'treinar_modelo_falta',
            'prever_falta',
            'gerar_insights_automaticos'
        ]
    })
