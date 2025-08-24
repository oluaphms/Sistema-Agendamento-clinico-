from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json

db = SQLAlchemy()

class AnalyticsConfig(db.Model):
    """Configurações do sistema de analytics"""
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(100), unique=True, nullable=False)
    valor = db.Column(db.Text)
    tipo = db.Column(db.String(20), default="string")  # string, int, float, json, bool
    descricao = db.Column(db.Text)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow)

class AnalyticsHistorico(db.Model):
    """Histórico de métricas para análise temporal"""
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    tipo_metrica = db.Column(db.String(50), nullable=False)  # presenca, faturamento, pacientes_ativos
    valor = db.Column(db.Float, nullable=False)
    detalhes = db.Column(db.Text)  # JSON com dados adicionais
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class RelatorioAgendado(db.Model):
    """Relatórios agendados para envio automático"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # diario, semanal, mensal
    frequencia = db.Column(db.String(20), nullable=False)  # cron expression
    destinatarios = db.Column(db.Text)  # JSON com emails
    formato = db.Column(db.String(10), default="pdf")  # pdf, excel, ambos
    ativo = db.Column(db.Boolean, default=True)
    ultimo_envio = db.Column(db.DateTime)
    proximo_envio = db.Column(db.DateTime)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class PrevisaoFalta(db.Model):
    """Previsões de faltas baseadas em IA"""
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, nullable=False)
    agendamento_id = db.Column(db.Integer, nullable=False)
    probabilidade_falta = db.Column(db.Float, nullable=False)  # 0.0 a 1.0
    fatores_risco = db.Column(db.Text)  # JSON com fatores analisados
    nivel_risco = db.Column(db.String(20), default="baixo")  # baixo, medio, alto
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow)

class InsightAutomatico(db.Model):
    """Insights gerados automaticamente pelo sistema"""
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)  # horario_critico, paciente_risco, tendencia
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    dados = db.Column(db.Text)  # JSON com dados do insight
    prioridade = db.Column(db.String(20), default="normal")  # baixa, normal, alta, critica
    lido = db.Column(db.Boolean, default=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    expira_em = db.Column(db.DateTime)

class MetricaTempoReal(db.Model):
    """Métricas em tempo real para dashboard"""
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(100), unique=True, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    unidade = db.Column(db.String(20))
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="normal")  # normal, alerta, critico

# Funções auxiliares para os modelos
def get_config(chave, valor_padrao=None):
    """Obtém configuração do analytics"""
    config = AnalyticsConfig.query.filter_by(chave=chave).first()
    if not config:
        return valor_padrao
    
    if config.tipo == "int":
        return int(config.valor) if config.valor else valor_padrao
    elif config.tipo == "float":
        return float(config.valor) if config.valor else valor_padrao
    elif config.tipo == "bool":
        return config.valor.lower() == "true" if config.valor else valor_padrao
    elif config.tipo == "json":
        return json.loads(config.valor) if config.valor else valor_padrao
    else:
        return config.valor or valor_padrao

def set_config(chave, valor, tipo="string", descricao=""):
    """Define configuração do analytics"""
    config = AnalyticsConfig.query.filter_by(chave=chave).first()
    if not config:
        config = AnalyticsConfig(
            chave=chave,
            valor=str(valor),
            tipo=tipo,
            descricao=descricao
        )
        db.session.add(config)
    else:
        config.valor = str(valor)
        config.tipo = tipo
        config.descricao = descricao
        config.atualizado_em = datetime.utcnow()
    
    db.session.commit()
    return config

def registrar_metrica(data, tipo_metrica, valor, detalhes=None):
    """Registra uma nova métrica no histórico"""
    metrica = AnalyticsHistorico(
        data=data,
        tipo_metrica=tipo_metrica,
        valor=valor,
        detalhes=json.dumps(detalhes) if detalhes else None
    )
    db.session.add(metrica)
    db.session.commit()
    return metrica

def registrar_insight(tipo, titulo, descricao, dados=None, prioridade="normal", expira_em=None):
    """Registra um novo insight automático"""
    insight = InsightAutomatico(
        tipo=tipo,
        titulo=titulo,
        descricao=descricao,
        dados=json.dumps(dados) if dados else None,
        prioridade=prioridade,
        expira_em=expira_em
    )
    db.session.add(insight)
    db.session.commit()
    return insight

def atualizar_metrica_tempo_real(chave, valor, unidade=None, status="normal"):
    """Atualiza métrica em tempo real"""
    metrica = MetricaTempoReal.query.filter_by(chave=chave).first()
    if not metrica:
        metrica = MetricaTempoReal(
            chave=chave,
            valor=valor,
            unidade=unidade,
            status=status
        )
        db.session.add(metrica)
    else:
        metrica.valor = valor
        metrica.unidade = unidade
        metrica.status = status
        metrica.atualizado_em = datetime.utcnow()
    
    db.session.commit()
    return metrica
