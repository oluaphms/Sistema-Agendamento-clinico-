from datetime import datetime, timedelta, date
from sqlalchemy import func, and_, or_, desc, asc
from sqlalchemy.sql import extract
import json
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

# Importar modelos do sistema principal (sem alterar código existente)
try:
    from app import db, Agendamento, Paciente, Profissional, Servico
except ImportError:
    # Fallback para desenvolvimento
    pass

from .models import (
    AnalyticsHistorico, PrevisaoFalta, InsightAutomatico, 
    MetricaTempoReal, registrar_metrica, registrar_insight, 
    atualizar_metrica_tempo_real
)

class AnalyticsService:
    """Serviço principal de analytics com IA"""
    
    def __init__(self):
        self.modelo_falta = None
        self.scaler = StandardScaler()
        self.modelo_treinado = False
    
    def calcular_metricas_gerais(self, data_inicio=None, data_fim=None):
        """Calcula métricas gerais do sistema"""
        if not data_inicio:
            data_inicio = date.today() - timedelta(days=30)
        if not data_fim:
            data_fim = date.today()
        
        # Filtros de data
        filtro_data = and_(
            Agendamento.data >= data_inicio.strftime('%Y-%m-%d'),
            Agendamento.data <= data_fim.strftime('%Y-%m-%d')
        )
        
        # Total de agendamentos
        total_agendamentos = Agendamento.query.filter(filtro_data).count()
        
        # Agendamentos por status
        agendamentos_por_status = db.session.query(
            Agendamento.status,
            func.count(Agendamento.id)
        ).filter(filtro_data).group_by(Agendamento.status).all()
        
        # Taxa de presença
        realizados = Agendamento.query.filter(
            and_(filtro_data, Agendamento.status == "Realizado")
        ).count()
        
        faltas = Agendamento.query.filter(
            and_(filtro_data, Agendamento.status == "Falta")
        ).count()
        
        total_consultas = realizados + faltas
        taxa_presenca = (realizados / total_consultas * 100) if total_consultas > 0 else 0
        
        # Faturamento
        faturamento_total = db.session.query(
            func.sum(Agendamento.valor_pago)
        ).filter(
            and_(filtro_data, Agendamento.status == "Realizado")
        ).scalar() or 0
        
        # Pacientes únicos
        pacientes_unicos = db.session.query(
            func.count(func.distinct(Agendamento.paciente_id))
        ).filter(filtro_data).scalar() or 0
        
        # Profissionais ativos
        profissionais_ativos = db.session.query(
            func.count(func.distinct(Agendamento.profissional_id))
        ).filter(filtro_data).scalar() or 0
        
        return {
            'periodo': {
                'inicio': data_inicio.strftime('%Y-%m-%d'),
                'fim': data_fim.strftime('%Y-%m-%d')
            },
            'agendamentos': {
                'total': total_agendamentos,
                'por_status': dict(agendamentos_por_status)
            },
            'presenca': {
                'taxa': round(taxa_presenca, 2),
                'realizados': realizados,
                'faltas': faltas,
                'total_consultas': total_consultas
            },
            'faturamento': {
                'total': round(faturamento_total, 2),
                'media_por_consulta': round(faturamento_total / realizados, 2) if realizados > 0 else 0
            },
            'participantes': {
                'pacientes_unicos': pacientes_unicos,
                'profissionais_ativos': profissionais_ativos
            }
        }
    
    def calcular_taxa_presenca_detalhada(self, data_inicio=None, data_fim=None):
        """Calcula taxa de presença detalhada por período, paciente e profissional"""
        if not data_inicio:
            data_inicio = date.today() - timedelta(days=30)
        if not data_fim:
            data_fim = date.today()
        
        filtro_data = and_(
            Agendamento.data >= data_inicio.strftime('%Y-%m-%d'),
            Agendamento.data <= data_fim.strftime('%Y-%m-%d')
        )
        
        # Por período (diário)
        presenca_diaria = db.session.query(
            Agendamento.data,
            func.count(Agendamento.id).label('total'),
            func.sum(func.case((Agendamento.status == "Realizado", 1), else_=0)).label('realizados'),
            func.sum(func.case((Agendamento.status == "Falta", 1), else_=0)).label('faltas')
        ).filter(filtro_data).group_by(Agendamento.data).order_by(Agendamento.data).all()
        
        # Por paciente
        presenca_paciente = db.session.query(
            Paciente.nome,
            func.count(Agendamento.id).label('total'),
            func.sum(func.case((Agendamento.status == "Realizado", 1), else_=0)).label('realizados'),
            func.sum(func.case((Agendamento.status == "Falta", 1), else_=0)).label('faltas')
        ).join(Agendamento).filter(filtro_data).group_by(Paciente.id, Paciente.nome).all()
        
        # Por profissional
        presenca_profissional = db.session.query(
            Profissional.nome,
            Profissional.especialidade,
            func.count(Agendamento.id).label('total'),
            func.sum(func.case((Agendamento.status == "Realizado", 1), else_=0)).label('realizados'),
            func.sum(func.case((Agendamento.status == "Falta", 1), else_=0)).label('faltas')
        ).join(Agendamento).filter(filtro_data).group_by(Profissional.id, Profissional.nome, Profissional.especialidade).all()
        
        # Calcular taxas
        def calcular_taxa(realizados, total):
            return round((realizados / total * 100), 2) if total > 0 else 0
        
        resultado = {
            'por_periodo': [
                {
                    'data': item.data,
                    'total': item.total,
                    'realizados': item.realizados,
                    'faltas': item.faltas,
                    'taxa_presenca': calcular_taxa(item.realizados, item.total)
                }
                for item in presenca_diaria
            ],
            'por_paciente': [
                {
                    'paciente': item.nome,
                    'total': item.total,
                    'realizados': item.realizados,
                    'faltas': item.faltas,
                    'taxa_presenca': calcular_taxa(item.realizados, item.total)
                }
                for item in presenca_paciente
            ],
            'por_profissional': [
                {
                    'profissional': item.nome,
                    'especialidade': item.especialidade,
                    'total': item.total,
                    'realizados': item.realizados,
                    'faltas': item.faltas,
                    'taxa_presenca': calcular_taxa(item.realizados, item.total)
                }
                for item in presenca_profissional
            ]
        }
        
        return resultado
    
    def calcular_consultas_por_especialidade(self, data_inicio=None, data_fim=None):
        """Calcula ranking de consultas por especialidade"""
        if not data_inicio:
            data_inicio = date.today() - timedelta(days=30)
        if not data_fim:
            data_fim = date.today()
        
        filtro_data = and_(
            Agendamento.data >= data_inicio.strftime('%Y-%m-%d'),
            Agendamento.data <= data_fim.strftime('%Y-%m-%d')
        )
        
        resultado = db.session.query(
            Profissional.especialidade,
            func.count(Agendamento.id).label('total_consultas'),
            func.sum(func.case((Agendamento.status == "Realizado", 1), else_=0)).label('realizadas'),
            func.sum(func.case((Agendamento.status == "Falta", 1), else_=0)).label('faltas'),
            func.sum(func.case((Agendamento.status == "Cancelado", 1), else_=0)).label('canceladas'),
            func.avg(Agendamento.valor_pago).label('valor_medio')
        ).join(Agendamento).filter(filtro_data).group_by(
            Profissional.especialidade
        ).order_by(desc('total_consultas')).all()
        
        return [
            {
                'especialidade': item.especialidade,
                'total_consultas': item.total_consultas,
                'realizadas': item.realizadas,
                'faltas': item.faltas,
                'canceladas': item.canceladas,
                'valor_medio': round(item.valor_medio or 0, 2),
                'taxa_realizacao': round((item.realizadas / item.total_consultas * 100), 2) if item.total_consultas > 0 else 0
            }
            for item in resultado
        ]
    
    def calcular_receita_mensal_profissional(self, ano=None, mes=None):
        """Calcula receita mensal por profissional"""
        if not ano:
            ano = date.today().year
        if not mes:
            mes = date.today().month
        
        resultado = db.session.query(
            Profissional.nome,
            Profissional.especialidade,
            func.sum(Agendamento.valor_pago).label('receita_total'),
            func.count(Agendamento.id).label('consultas_realizadas'),
            func.avg(Agendamento.valor_pago).label('valor_medio_consulta')
        ).join(Agendamento).filter(
            and_(
                extract('year', func.str_to_date(Agendamento.data, '%Y-%m-%d')) == ano,
                extract('month', func.str_to_date(Agendamento.data, '%Y-%m-%d')) == mes,
                Agendamento.status == "Realizado"
            )
        ).group_by(Profissional.id, Profissional.nome, Profissional.especialidade).order_by(
            desc('receita_total')
        ).all()
        
        return [
            {
                'profissional': item.nome,
                'especialidade': item.especialidade,
                'receita_total': round(item.receita_total or 0, 2),
                'consultas_realizadas': item.consultas_realizadas,
                'valor_medio_consulta': round(item.valor_medio_consulta or 0, 2)
            }
            for item in resultado
        ]
    
    def calcular_crescimento_pacientes(self, meses=12):
        """Calcula crescimento de pacientes ativos ao longo do tempo"""
        hoje = date.today()
        resultado = []
        
        for i in range(meses):
            data_analise = hoje - timedelta(days=30 * i)
            mes = data_analise.month
            ano = data_analise.year
            
            # Pacientes únicos no mês
            pacientes_mes = db.session.query(
                func.count(func.distinct(Agendamento.paciente_id))
            ).filter(
                and_(
                    extract('year', func.str_to_date(Agendamento.data, '%Y-%m-%d')) == ano,
                    extract('month', func.str_to_date(Agendamento.data, '%Y-%m-%d')) == mes
                )
            ).scalar() or 0
            
            # Novos pacientes no mês
            novos_pacientes = db.session.query(
                func.count(func.distinct(Agendamento.paciente_id))
            ).filter(
                and_(
                    extract('year', func.str_to_date(Agendamento.data, '%Y-%m-%d')) == ano,
                    extract('month', func.str_to_date(Agendamento.data, '%Y-%m-%d')) == mes,
                    ~Agendamento.paciente_id.in_(
                        db.session.query(Agendamento.paciente_id).filter(
                            func.str_to_date(Agendamento.data, '%Y-%m-%d') < f"{ano}-{mes:02d}-01"
                        ).subquery()
                    )
                )
            ).scalar() or 0
            
            resultado.append({
                'mes': f"{ano}-{mes:02d}",
                'pacientes_ativos': pacientes_mes,
                'novos_pacientes': novos_pacientes,
                'crescimento': 0  # Será calculado abaixo
            })
        
        # Calcular crescimento percentual
        for i in range(1, len(resultado)):
            anterior = resultado[i-1]['pacientes_ativos']
            atual = resultado[i]['pacientes_ativos']
            if anterior > 0:
                resultado[i]['crescimento'] = round(((atual - anterior) / anterior) * 100, 2)
        
        return list(reversed(resultado))  # Ordem cronológica
    
    def treinar_modelo_falta(self):
        """Treina modelo de IA para prever faltas"""
        try:
            # Buscar dados históricos
            agendamentos = Agendamento.query.filter(
                Agendamento.status.in_(["Realizado", "Falta"])
            ).all()
            
            if len(agendamentos) < 100:  # Mínimo de dados para treinar
                return False
            
            # Preparar dados para treinamento
            dados = []
            for agendamento in agendamentos:
                # Buscar histórico do paciente
                historico_paciente = Agendamento.query.filter(
                    and_(
                        Agendamento.paciente_id == agendamento.paciente_id,
                        Agendamento.data < agendamento.data
                    )
                ).all()
                
                # Calcular features
                total_consultas = len(historico_paciente)
                faltas_anteriores = sum(1 for h in historico_paciente if h.status == "Falta")
                taxa_falta_historica = faltas_anteriores / total_consultas if total_consultas > 0 else 0
                
                # Dia da semana (0=Segunda, 6=Domingo)
                data_obj = datetime.strptime(agendamento.data, '%Y-%m-%d')
                dia_semana = data_obj.weekday()
                
                # Hora do dia
                hora_obj = datetime.strptime(agendamento.hora, '%H:%M')
                hora_dia = hora_obj.hour
                
                # Distância da última consulta
                ultima_consulta = max([h.data for h in historico_paciente]) if historico_paciente else None
                if ultima_consulta:
                    ultima_data = datetime.strptime(ultima_consulta, '%Y-%m-%d')
                    dias_ultima_consulta = (data_obj - ultima_data).days
                else:
                    dias_ultima_consulta = 365  # Valor padrão para novos pacientes
                
                dados.append([
                    total_consultas,
                    faltas_anteriores,
                    taxa_falta_historica,
                    dia_semana,
                    hora_dia,
                    dias_ultima_consulta,
                    1 if agendamento.status == "Falta" else 0  # Target
                ])
            
            # Converter para DataFrame
            df = pd.DataFrame(dados, columns=[
                'total_consultas', 'faltas_anteriores', 'taxa_falta_historica',
                'dia_semana', 'hora_dia', 'dias_ultima_consulta', 'target'
            ])
            
            # Separar features e target
            X = df.drop('target', axis=1)
            y = df['target']
            
            # Dividir dados de treino e teste
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Normalizar features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Treinar modelo
            self.modelo_falta = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                n_jobs=-1
            )
            self.modelo_falta.fit(X_train_scaled, y_train)
            
            # Avaliar modelo
            y_pred = self.modelo_falta.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            self.modelo_treinado = True
            
            # Registrar métrica de acurácia
            registrar_metrica(
                date.today(),
                'acuracia_modelo_falta',
                accuracy * 100
            )
            
            return True
            
        except Exception as e:
            print(f"Erro ao treinar modelo: {e}")
            return False
    
    def prever_falta(self, paciente_id, agendamento_id, data, hora):
        """Prevê probabilidade de falta para um agendamento específico"""
        if not self.modelo_treinado:
            return None
        
        try:
            # Buscar histórico do paciente
            historico_paciente = Agendamento.query.filter(
                and_(
                    Agendamento.paciente_id == paciente_id,
                    Agendamento.data < data
                )
            ).all()
            
            # Calcular features
            total_consultas = len(historico_paciente)
            faltas_anteriores = sum(1 for h in historico_paciente if h.status == "Falta")
            taxa_falta_historica = faltas_anteriores / total_consultas if total_consultas > 0 else 0
            
            # Dia da semana
            data_obj = datetime.strptime(data, '%Y-%m-%d')
            dia_semana = data_obj.weekday()
            
            # Hora do dia
            hora_obj = datetime.strptime(hora, '%H:%M')
            hora_dia = hora_obj.hour
            
            # Distância da última consulta
            ultima_consulta = max([h.data for h in historico_paciente]) if historico_paciente else None
            if ultima_consulta:
                ultima_data = datetime.strptime(ultima_consulta, '%Y-%m-%d')
                dias_ultima_consulta = (data_obj - ultima_data).days
            else:
                dias_ultima_consulta = 365
            
            # Preparar features para predição
            features = np.array([[
                total_consultas,
                faltas_anteriores,
                taxa_falta_historica,
                dia_semana,
                hora_dia,
                dias_ultima_consulta
            ]])
            
            # Normalizar features
            features_scaled = self.scaler.transform(features)
            
            # Fazer predição
            probabilidade_falta = self.modelo_falta.predict_proba(features_scaled)[0][1]
            
            # Determinar nível de risco
            if probabilidade_falta < 0.3:
                nivel_risco = "baixo"
            elif probabilidade_falta < 0.6:
                nivel_risco = "medio"
            else:
                nivel_risco = "alto"
            
            # Fatores de risco
            fatores_risco = {
                'total_consultas': total_consultas,
                'faltas_anteriores': faltas_anteriores,
                'taxa_falta_historica': round(taxa_falta_historica * 100, 2),
                'dia_semana': dia_semana,
                'hora_dia': hora_dia,
                'dias_ultima_consulta': dias_ultima_consulta
            }
            
            return {
                'probabilidade_falta': round(probabilidade_falta * 100, 2),
                'nivel_risco': nivel_risco,
                'fatores_risco': fatores_risco
            }
            
        except Exception as e:
            print(f"Erro ao prever falta: {e}")
            return None
    
    def gerar_insights_automaticos(self):
        """Gera insights automáticos baseados nos dados"""
        insights = []
        
        try:
            # 1. Horários mais críticos
            horarios_criticos = db.session.query(
                Agendamento.hora,
                func.count(Agendamento.id).label('total'),
                func.sum(func.case((Agendamento.status == "Falta", 1), else_=0)).label('faltas'),
                func.sum(func.case((Agendamento.status == "Cancelado", 1), else_=0)).label('cancelamentos')
            ).filter(
                Agendamento.status.in_(["Realizado", "Falta", "Cancelado"])
            ).group_by(Agendamento.hora).having(
                func.count(Agendamento.id) >= 5  # Mínimo de 5 consultas
            ).all()
            
            for horario in horarios_criticos:
                taxa_problemas = ((horario.faltas + horario.cancelamentos) / horario.total) * 100
                if taxa_problemas > 30:  # Mais de 30% de problemas
                    insights.append({
                        'tipo': 'horario_critico',
                        'titulo': f"⚠️ Horário {horario.hora} com alta taxa de problemas",
                        'descricao': f"O horário {horario.hora} apresenta {taxa_problemas:.1f}% de faltas e cancelamentos. Considere revisar a disponibilidade.",
                        'dados': {
                            'horario': horario.hora,
                            'total_consultas': horario.total,
                            'faltas': horario.faltas,
                            'cancelamentos': horario.cancelamentos,
                            'taxa_problemas': round(taxa_problemas, 1)
                        },
                        'prioridade': 'alta' if taxa_problemas > 50 else 'normal'
                    })
            
            # 2. Pacientes em risco de abandono
            pacientes_risco = db.session.query(
                Paciente.nome,
                func.count(Agendamento.id).label('total_faltas'),
                func.max(Agendamento.data).label('ultima_consulta')
            ).join(Agendamento).filter(
                Agendamento.status == "Falta"
            ).group_by(Paciente.id, Paciente.nome).having(
                func.count(Agendamento.id) >= 3  # 3 ou mais faltas
            ).all()
            
            for paciente in pacientes_risco:
                ultima_data = datetime.strptime(paciente.ultima_consulta, '%Y-%m-%d')
                dias_desde_ultima = (date.today() - ultima_data.date()).days
                
                if dias_desde_ultima > 30:  # Não consulta há mais de 30 dias
                    insights.append({
                        'tipo': 'paciente_risco',
                        'titulo': f"🚨 Paciente {paciente.nome} em risco de abandono",
                        'descricao': f"Paciente com {paciente.total_faltas} faltas consecutivas e sem consulta há {dias_desde_ultima} dias.",
                        'dados': {
                            'paciente': paciente.nome,
                            'total_faltas': paciente.total_faltas,
                            'dias_sem_consulta': dias_desde_ultima,
                            'ultima_consulta': paciente.ultima_consulta
                        },
                        'prioridade': 'critica'
                    })
            
            # 3. Tendências de crescimento
            # (Implementar análise de tendências)
            
            # Registrar insights no banco
            for insight_data in insights:
                registrar_insight(
                    tipo=insight_data['tipo'],
                    titulo=insight_data['titulo'],
                    descricao=insight_data['descricao'],
                    dados=insight_data['dados'],
                    prioridade=insight_data['prioridade']
                )
            
            return insights
            
        except Exception as e:
            print(f"Erro ao gerar insights: {e}")
            return []
    
    def atualizar_metricas_tempo_real(self):
        """Atualiza métricas em tempo real para o dashboard"""
        try:
            hoje = date.today()
            
            # Taxa de presença hoje
            agendamentos_hoje = Agendamento.query.filter(
                Agendamento.data == hoje.strftime('%Y-%m-%d')
            ).count()
            
            if agendamentos_hoje > 0:
                presencas_hoje = Agendamento.query.filter(
                    and_(
                        Agendamento.data == hoje.strftime('%Y-%m-%d'),
                        Agendamento.status == "Realizado"
                    )
                ).count()
                
                taxa_presenca_hoje = (presencas_hoje / agendamentos_hoje) * 100
                
                atualizar_metrica_tempo_real(
                    'taxa_presenca_hoje',
                    round(taxa_presenca_hoje, 2),
                    '%',
                    'normal' if taxa_presenca_hoje >= 80 else 'alerta'
                )
            
            # Total de agendamentos para hoje
            atualizar_metrica_tempo_real(
                'agendamentos_hoje',
                agendamentos_hoje,
                'consultas'
            )
            
            # Faturamento do dia
            faturamento_hoje = db.session.query(
                func.sum(Agendamento.valor_pago)
            ).filter(
                and_(
                    Agendamento.data == hoje.strftime('%Y-%m-%d'),
                    Agendamento.status == "Realizado"
                )
            ).scalar() or 0
            
            atualizar_metrica_tempo_real(
                'faturamento_hoje',
                round(faturamento_hoje, 2),
                'R$'
            )
            
            # Pacientes únicos hoje
            pacientes_hoje = db.session.query(
                func.count(func.distinct(Agendamento.paciente_id))
            ).filter(
                Agendamento.data == hoje.strftime('%Y-%m-%d')
            ).scalar() or 0
            
            atualizar_metrica_tempo_real(
                'pacientes_hoje',
                pacientes_hoje,
                'pacientes'
            )
            
            return True
            
        except Exception as e:
            print(f"Erro ao atualizar métricas: {e}")
            return False

# Instância global do serviço
analytics_service = AnalyticsService()
