from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, flash
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, time, timedelta
import csv, io, json, os, logging
from config import config
import plotly.graph_objs as go
import plotly.utils
import pandas as pd

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicialização do Flask
app = Flask(__name__)
app.config.from_object(config['development'])

# Extensões
db = SQLAlchemy(app)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Importar módulos avançados
from integrations.whatsapp import WhatsAppIntegration
from integrations.google import GoogleIntegration
from ai.chatbot import IntelligentChatbot
from websockets.notifications import NotificationManager
from gamification.points_system import GamificationSystem

# Inicializar módulos
whatsapp = WhatsAppIntegration()
google_integration = GoogleIntegration()
chatbot = IntelligentChatbot()
notification_manager = NotificationManager(socketio)
gamification = GamificationSystem(db)

# Configurar handlers do WebSocket
notification_manager.setup_handlers()

# ---------------- MODELOS EXISTENTES ----------------
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="recepcao")
    profissional_id = db.Column(db.Integer, db.ForeignKey('profissional.id'))

class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(30))
    email = db.Column(db.String(120))
    nascimento = db.Column(db.String(10))
    observacoes = db.Column(db.Text)
    convenio = db.Column(db.String(120))
    pontos = db.Column(db.Integer, default=0)
    nivel = db.Column(db.Integer, default=1)

class Profissional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    especialidade = db.Column(db.String(120))
    telefone = db.Column(db.String(30))
    email = db.Column(db.String(120))
    horarios = db.Column(db.Text)
    pontos = db.Column(db.Integer, default=0)
    nivel = db.Column(db.Integer, default=1)
    avaliacao_media = db.Column(db.Float, default=0.0)

class Servico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    duracao_min = db.Column(db.Integer, default=30)
    preco = db.Column(db.Float, default=0.0)

class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    profissional_id = db.Column(db.Integer, db.ForeignKey('profissional.id'), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servico.id'), nullable=False)
    data = db.Column(db.String(10), nullable=False)
    hora = db.Column(db.String(5), nullable=False)
    duracao = db.Column(db.Integer, default=30)
    status = db.Column(db.String(20), default="Agendado")
    observacoes = db.Column(db.Text)
    origem = db.Column(db.String(20))
    valor_pago = db.Column(db.Float, default=0.0)
    google_event_id = db.Column(db.String(100))
    video_call_link = db.Column(db.String(200))
    avaliacao = db.Column(db.Integer)
    feedback = db.Column(db.Text)

    paciente = db.relationship('Paciente')
    profissional = db.relationship('Profissional')
    servico = db.relationship('Servico')

class Prontuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    data = db.Column(db.String(10), nullable=False)
    anotacao = db.Column(db.Text, nullable=False)
    paciente = db.relationship('Paciente')

# ---------------- NOVOS MODELOS ----------------
class Notificacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    tipo = db.Column(db.String(50))
    titulo = db.Column(db.String(200))
    mensagem = db.Column(db.Text)
    lida = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    dados_extras = db.Column(db.Text)  # JSON

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sala = db.Column(db.String(100))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    mensagem = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    tipo = db.Column(db.String(20), default='text')

class Pagamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agendamento_id = db.Column(db.Integer, db.ForeignKey('agendamento.id'))
    valor = db.Column(db.Float)
    metodo = db.Column(db.String(50))  # stripe, mercadopago, etc.
    status = db.Column(db.String(50))  # pendente, aprovado, cancelado
    gateway_id = db.Column(db.String(100))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

# ---------------- HELPERS EXISTENTES ----------------
def require_login(role=None):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            if 'usuario' not in session:
                return redirect(url_for('login'))
            if role and session.get('role') not in role:
                flash("Sem permissão para acessar.", "warning")
                return redirect(url_for('dashboard'))
            return fn(*args, **kwargs)
        wrapper.__name__ = fn.__name__
        return wrapper
    return decorator

def to_datetime(dstr, tstr):
    return datetime.strptime(f"{dstr} {tstr}", "%Y-%m-%d %H:%M")

def conflito(profissional_id, data, hora, duracao, agendamento_id=None):
    inicio = to_datetime(data, hora)
    fim = inicio + timedelta(minutes=duracao)
    eventos = Agendamento.query.filter_by(profissional_id=profissional_id, data=data).all()
    for ev in eventos:
        if agendamento_id and ev.id == agendamento_id:
            continue
        ev_inicio = to_datetime(ev.data, ev.hora)
        ev_fim = ev_inicio + timedelta(minutes=ev.duracao)
        if inicio < ev_fim and ev_inicio < fim and ev.status not in ["Cancelado"]:
            return True
    return False

def timedelta_minutes(mins):
    return timedelta(minutes=int(mins))

# ---------------- AUTH EXISTENTE ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')
        user = Usuario.query.filter_by(usuario=usuario).first()
        if user and check_password_hash(user.senha, senha):
            session['usuario'] = user.usuario
            session['role'] = user.role
            session['profissional_id'] = user.profissional_id
            
            # Envia notificação de login
            notification_manager.send_system_notification(
                f"Usuário {usuario} fez login no sistema",
                "info",
                ["general"]
            )
            
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', erro="Login inválido")
    return render_template('login.html')

@app.route('/logout')
def logout():
    usuario = session.get('usuario')
    session.clear()
    
    if usuario:
        notification_manager.send_system_notification(
            f"Usuário {usuario} fez logout do sistema",
            "info",
            ["general"]
        )
    
    return redirect(url_for('login'))

# ---------------- DASHBOARD AVANÇADO ----------------
@app.route('/dashboard')
@require_login()
def dashboard():
    hoje = date.today().strftime("%Y-%m-%d")
    prof_id = session.get('profissional_id')
    
    # Agendamentos do dia
    q = Agendamento.query.filter_by(data=hoje)
    if session.get('role') == 'profissional' and prof_id:
        q = q.filter_by(profissional_id=prof_id)
    proximos = q.order_by(Agendamento.hora.asc()).all()
    
    # Estatísticas avançadas
    total_receita = db.session.query(db.func.sum(Agendamento.valor_pago)).scalar() or 0
    
    # KPIs em tempo real
    total_pacientes = Paciente.query.count()
    total_profissionais = Profissional.query.count()
    agendamentos_hoje = len(proximos)
    agendamentos_pendentes = Agendamento.query.filter_by(status="Agendado").count()
    
    # Dados para gráficos
    chart_data = generate_dashboard_charts()
    
    # Perfil gamificado do usuário
    user_profile = None
    if session.get('usuario'):
        user_type = 'professional' if session.get('role') == 'profissional' else 'patient'
        user_profile = gamification.get_user_profile(1, user_type)  # ID hardcoded por simplicidade
    
    return render_template('dashboard_advanced.html', 
                         proximos=proximos, 
                         total_receita=total_receita,
                         kpis={
                             'total_pacientes': total_pacientes,
                             'total_profissionais': total_profissionais,
                             'agendamentos_hoje': agendamentos_hoje,
                             'agendamentos_pendentes': agendamentos_pendentes
                         },
                         chart_data=chart_data,
                         user_profile=user_profile)

def generate_dashboard_charts():
    """Gera dados para gráficos do dashboard"""
    try:
        # Gráfico de receita por mês
        receita_mensal = db.session.query(
            db.func.strftime('%Y-%m', Agendamento.data).label('mes'),
            db.func.sum(Agendamento.valor_pago).label('receita')
        ).filter(
            Agendamento.status.in_(['Realizado', 'Confirmado'])
        ).group_by('mes').order_by('mes').limit(12).all()
        
        meses = [r.mes for r in receita_mensal]
        receitas = [float(r.receita) for r in receita_mensal]
        
        receita_chart = go.Figure(data=[
            go.Bar(x=meses, y=receitas, name='Receita Mensal')
        ])
        receita_chart.update_layout(
            title='Receita Mensal',
            xaxis_title='Mês',
            yaxis_title='Receita (R$)'
        )
        
        # Gráfico de agendamentos por status
        status_counts = db.session.query(
            Agendamento.status,
            db.func.count(Agendamento.id)
        ).group_by(Agendamento.status).all()
        
        status_labels = [s[0] for s in status_counts]
        status_values = [s[1] for s in status_counts]
        
        status_chart = go.Figure(data=[
            go.Pie(labels=status_labels, values=status_values)
        ])
        status_chart.update_layout(title='Agendamentos por Status')
        
        return {
            'receita_mensal': json.dumps(receita_chart, cls=plotly.utils.PlotlyJSONEncoder),
            'status_agendamentos': json.dumps(status_chart, cls=plotly.utils.PlotlyJSONEncoder)
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar gráficos: {str(e)}")
        return {}

# ---------------- ROTAS EXISTENTES ATUALIZADAS ----------------
@app.route('/pacientes', methods=['GET', 'POST'])
@require_login(role=['admin','recepcao','profissional'])
def pacientes():
    if request.method == 'POST' and session.get('role') in ['admin','recepcao']:
        p = Paciente(
            nome=request.form.get('nome'),
            telefone=request.form.get('telefone'),
            email=request.form.get('email'),
            nascimento=request.form.get('nascimento'),
            observacoes=request.form.get('observacoes'),
            convenio=request.form.get('convenio'),
        )
        db.session.add(p)
        db.session.commit()
        
        # Envia notificação
        notification_manager.send_system_notification(
            f"Novo paciente cadastrado: {p.nome}",
            "info",
            ["role_admin", "role_recepcao"]
        )
        
        # Concede pontos para gamificação
        gamification.award_points(p.id, 'patient', 'first_appointment')
        
        return redirect(url_for('pacientes'))
    
    lista = Paciente.query.order_by(Paciente.nome.asc()).all()
    return render_template('pacientes.html', pacientes=lista)

@app.route('/agenda', methods=['GET','POST'])
@require_login(role=['admin','recepcao','profissional'])
def agenda():
    if request.method == 'POST':
        data = request.form.get('data')
        hora = request.form.get('hora')
        duracao = int(request.form.get('duracao'))
        profissional_id = int(request.form.get('profissional_id'))
        
        if conflito(profissional_id, data, hora, duracao):
            flash("Conflito de horário para este profissional.", "danger")
        else:
            ag = Agendamento(
                paciente_id=int(request.form.get('paciente_id')),
                profissional_id=profissional_id,
                servico_id=int(request.form.get('servico_id')),
                data=data, hora=hora, duracao=duracao,
                status=request.form.get('status'),
                observacoes=request.form.get('observacoes'),
                origem=request.form.get('origem'),
                valor_pago=float(request.form.get('valor_pago') or 0)
            )
            db.session.add(ag)
            db.session.commit()
            
            # Integração com Google Calendar
            if google_integration.is_configured():
                appointment_data = {
                    'paciente': {'nome': ag.paciente.nome, 'email': ag.paciente.email},
                    'profissional': {'nome': ag.profissional.nome, 'email': ag.profissional.email},
                    'servico': {'nome': ag.servico.nome},
                    'data': ag.data,
                    'hora': ag.hora,
                    'duracao': ag.duracao,
                    'observacoes': ag.observacoes
                }
                
                google_result = google_integration.create_calendar_event(appointment_data)
                if google_result['success']:
                    ag.google_event_id = google_result['event_id']
                    db.session.commit()
            
            # Envia notificação em tempo real
            notification_manager.send_appointment_notification(
                {
                    'id': ag.id,
                    'paciente': {'nome': ag.paciente.nome},
                    'profissional': {'nome': ag.profissional.nome},
                    'servico': {'nome': ag.servico.nome},
                    'data': ag.data,
                    'hora': ag.hora,
                    'profissional_id': ag.profissional_id
                },
                'new_appointment'
            )
            
            # Envia confirmação via WhatsApp
            if whatsapp.is_configured():
                whatsapp.send_appointment_confirmation(
                    ag.paciente.telefone,
                    {
                        'paciente': {'nome': ag.paciente.nome},
                        'profissional': {'nome': ag.profissional.nome},
                        'servico': {'nome': ag.servico.nome},
                        'data': ag.data,
                        'hora': ag.hora
                    }
                )
            
            flash("Agendamento criado.", "success")
        return redirect(url_for('agenda'))

    dia = request.args.get('dia') or date.today().strftime("%Y-%m-%d")
    prof_filtro = request.args.get('prof')
    pac_filtro = request.args.get('pac')
    q = Agendamento.query.filter_by(data=dia)
    if prof_filtro: q = q.filter_by(profissional_id=prof_filtro)
    if pac_filtro: q = q.filter_by(paciente_id=pac_filtro)
    ags = q.order_by(Agendamento.hora.asc()).all()

    pacientes = Paciente.query.order_by(Paciente.nome.asc()).all()
    profissionais = Profissional.query.order_by(Profissional.nome.asc()).all()
    servicos = Servico.query.order_by(Servico.nome.asc()).all()
    return render_template('agenda.html', ags=ags, pacientes=pacientes, profissionais=profissionais, servicos=servicos, dia=dia)

# ---------------- NOVAS ROTAS AVANÇADAS ----------------
@app.route('/chatbot', methods=['POST'])
def chatbot_endpoint():
    """Endpoint para o chatbot inteligente"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        user_id = data.get('user_id', 'anonymous')
        context = data.get('context', {})
        
        response = chatbot.get_response(user_message, user_id, context)
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Erro no chatbot: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/notifications')
@require_login()
def get_notifications():
    """API para buscar notificações do usuário"""
    try:
        user_id = session.get('usuario')
        notifications = notification_manager.get_user_notifications(user_id, limit=50)
        return jsonify({"success": True, "notifications": notifications})
        
    except Exception as e:
        logger.error(f"Erro ao buscar notificações: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/gamification/profile')
@require_login()
def get_gamification_profile():
    """API para perfil gamificado do usuário"""
    try:
        user_id = 1  # Em produção, viria do banco
        user_type = 'professional' if session.get('role') == 'profissional' else 'patient'
        profile = gamification.get_user_profile(user_id, user_type)
        return jsonify({"success": True, "profile": profile})
        
    except Exception as e:
        logger.error(f"Erro ao buscar perfil gamificado: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/gamification/leaderboard')
def get_leaderboard():
    """API para ranking de usuários"""
    try:
        user_type = request.args.get('type', 'patient')
        limit = int(request.args.get('limit', 10))
        leaderboard = gamification.get_leaderboard(user_type, limit)
        return jsonify({"success": True, "leaderboard": leaderboard})
        
    except Exception as e:
        logger.error(f"Erro ao buscar ranking: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/telemedicina/<int:agendamento_id>')
@require_login()
def telemedicina(agendamento_id):
    """Página de telemedicina para consulta online"""
    agendamento = Agendamento.query.get_or_404(agendamento_id)
    
    # Verifica se o usuário tem permissão para acessar
    if (session.get('role') not in ['admin', 'recepcao'] and 
        session.get('profissional_id') != agendamento.profissional_id and
        session.get('usuario') != str(agendamento.paciente_id)):
        flash("Sem permissão para acessar esta consulta.", "warning")
        return redirect(url_for('dashboard'))
    
    return render_template('telemedicina.html', agendamento=agendamento)

@app.route('/api/telemedicina/session', methods=['POST'])
@require_login()
def create_telemedicina_session():
    """Cria sessão de telemedicina"""
    try:
        data = request.get_json()
        agendamento_id = data.get('agendamento_id')
        
        # Em produção, isso seria integrado com OpenTok ou similar
        session_data = {
            'session_id': f"session_{agendamento_id}_{datetime.now().timestamp()}",
            'token': f"token_{agendamento_id}",
            'api_key': app.config.get('OPENTOK_API_KEY', 'demo_key')
        }
        
        # Atualiza agendamento com link de vídeo
        agendamento = Agendamento.query.get(agendamento_id)
        if agendamento:
            agendamento.video_call_link = f"/telemedicina/{agendamento_id}"
            db.session.commit()
        
        return jsonify({"success": True, "session": session_data})
        
    except Exception as e:
        logger.error(f"Erro ao criar sessão de telemedicina: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/whatsapp/webhook', methods=['POST'])
def whatsapp_webhook():
    """Webhook para receber mensagens do WhatsApp"""
    try:
        data = request.get_json()
        
        # Processa mensagem recebida
        if data.get('entry') and data['entry'][0].get('changes'):
            change = data['entry'][0]['changes'][0]
            if change.get('value') and change['value'].get('messages'):
                message = change['value']['messages'][0]
                
                # Processa mensagem com chatbot
                user_id = f"whatsapp_{message['from']}"
                response = chatbot.get_response(message['text']['body'], user_id)
                
                # Envia resposta via WhatsApp
                if response['success']:
                    whatsapp.send_message(
                        message['from'],
                        response['response']
                    )
        
        return jsonify({"success": True})
        
    except Exception as e:
        logger.error(f"Erro no webhook do WhatsApp: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/google/sync')
@require_login(role=['admin'])
def google_sync():
    """Sincroniza dados com Google"""
    try:
        if not google_integration.is_configured():
            flash("Google não configurado.", "warning")
            return redirect(url_for('dashboard'))
        
        # Sincroniza agendamentos para Google Sheets
        agendamentos = Agendamento.query.all()
        appointments_data = []
        
        for ag in agendamentos:
            appointments_data.append({
                'id': ag.id,
                'paciente': {'nome': ag.paciente.nome},
                'profissional': {'nome': ag.profissional.nome},
                'servico': {'nome': ag.servico.nome},
                'data': ag.data,
                'hora': ag.hora,
                'status': ag.status,
                'valor_pago': ag.valor_pago,
                'observacoes': ag.observacoes
            })
        
        result = google_integration.sync_appointments_to_sheets(appointments_data)
        
        if result['success']:
            flash(f"Dados sincronizados com Google Sheets. ID: {result['spreadsheet_id']}", "success")
        else:
            flash(f"Erro na sincronização: {result['error']}", "warning")
        
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logger.error(f"Erro na sincronização Google: {str(e)}")
        flash(f"Erro na sincronização: {str(e)}", "danger")
        return redirect(url_for('dashboard'))

# ---------------- ROTAS EXISTENTES MANTIDAS ----------------
@app.route('/profissionais', methods=['GET', 'POST'])
@require_login(role=['admin'])
def profissionais():
    if request.method == 'POST':
        horarios = request.form.get('horarios') or "{}"
        prof = Profissional(
            nome=request.form.get('nome'),
            especialidade=request.form.get('especialidade'),
            telefone=request.form.get('telefone'),
            email=request.form.get('email'),
            horarios=horarios
        )
        db.session.add(prof)
        db.session.commit()
        return redirect(url_for('profissionais'))
    lista = Profissional.query.order_by(Profissional.nome.asc()).all()
    return render_template('profissionais.html', profissionais=lista)

@app.route('/usuarios', methods=['GET', 'POST'])
@require_login(role=['admin'])
def usuarios():
    if request.method == 'POST':
        u = Usuario(
            usuario=request.form.get('usuario'),
            senha=generate_password_hash(request.form.get('senha')),
            role=request.form.get('role')
        )
        db.session.add(u)
        db.session.commit()
        return redirect(url_for('usuarios'))
    usuarios = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/servicos', methods=['GET','POST'])
@require_login(role=['admin','recepcao'])
def servicos():
    if request.method == 'POST':
        s = Servico(
            nome=request.form.get('nome'),
            duracao_min=int(request.form.get('duracao_min') or 30),
            preco=float(request.form.get('preco') or 0)
        )
        db.session.add(s)
        db.session.commit()
        return redirect(url_for('servicos'))
    lista = Servico.query.order_by(Servico.nome.asc()).all()
    return render_template('servicos.html', servicos=lista)

@app.route('/relatorios')
@require_login(role=['admin'])
def relatorios():
    faltas = Agendamento.query.filter_by(status="Falta").count()
    receita_por_prof = db.session.query(Profissional.nome, db.func.sum(Agendamento.valor_pago)).join(Agendamento, Agendamento.profissional_id==Profissional.id).group_by(Profissional.id).all()
    total_conf = Agendamento.query.filter(Agendamento.status.in_(["Agendado","Confirmado"])).count()
    confirmados = Agendamento.query.filter_by(status="Confirmado").count()
    taxa_confirmacao = (confirmados/total_conf*100) if total_conf else 0
    
    # Dados para gráficos avançados
    chart_data = generate_advanced_charts()
    
    return render_template('relatorios_advanced.html', 
                         faltas=faltas, 
                         receita_por_prof=receita_por_prof, 
                         taxa_confirmacao=taxa_confirmacao,
                         chart_data=chart_data)

def generate_advanced_charts():
    """Gera gráficos avançados para relatórios"""
    try:
        # Gráfico de evolução de pacientes
        pacientes_por_mes = db.session.query(
            db.func.strftime('%Y-%m', Paciente.nascimento).label('mes'),
            db.func.count(Paciente.id).label('total')
        ).group_by('mes').order_by('mes').limit(12).all()
        
        meses = [p.mes for p in pacientes_por_mes]
        totais = [p.total for p in pacientes_por_mes]
        
        pacientes_chart = go.Figure(data=[
            go.Scatter(x=meses, y=totais, mode='lines+markers', name='Novos Pacientes')
        ])
        pacientes_chart.update_layout(
            title='Evolução de Pacientes',
            xaxis_title='Mês',
            yaxis_title='Novos Pacientes'
        )
        
        return {
            'pacientes_evolucao': json.dumps(pacientes_chart, cls=plotly.utils.PlotlyJSONEncoder)
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar gráficos avançados: {str(e)}")
        return {}

@app.route('/prontuario/<int:paciente_id>', methods=['GET','POST'])
@require_login(role=['admin','recepcao','profissional'])
def prontuario(paciente_id):
    if request.method == 'POST':
        pr = Prontuario(
            paciente_id=paciente_id,
            data=request.form.get('data') or date.today().strftime("%Y-%m-%d"),
            anotacao=request.form.get('anotacao')
        )
        db.session.add(pr)
        db.session.commit()
        return redirect(url_for('prontuario', paciente_id=paciente_id))
    paciente = Paciente.query.get_or_404(paciente_id)
    registros = Prontuario.query.filter_by(paciente_id=paciente_id).order_by(Prontuario.id.desc()).all()
    return render_template('prontuario.html', paciente=paciente, registros=registros)

@app.route('/calendario')
@require_login(role=['admin','recepcao','profissional'])
def calendario():
    return render_template('calendario.html')

# ---------------- SETUP INICIAL ----------------
with app.app_context():
    db.create_all()
    # cria admin padrão
    if not Usuario.query.filter_by(usuario='admin').first():
        admin = Usuario(usuario='admin', senha=generate_password_hash('admin123'), role='admin')
        db.session.add(admin)
        db.session.commit()

# ---------------- RUN ----------------
if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
