from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, flash, g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import joinedload
import io
import csv
from datetime import datetime, date, time, timedelta
import csv, io, json, os, re
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinica.db'
app.config['SECRET_KEY'] = 'chave-secreta-super'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def check_database_sync():
    """Verifica e corrige automaticamente problemas de sincronização do banco"""
    try:
        db_path = 'instance/clinica.db'
        if not os.path.exists(db_path):
            print("AVISO: Banco de dados não encontrado - será criado automaticamente")
            return True
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tabela paciente (problema principal identificado)
        cursor.execute("PRAGMA table_info(paciente)")
        paciente_columns = [col[1] for col in cursor.fetchall()]
        
        required_columns = ['categoria', 'data_cadastro', 'ultima_atualizacao']
        missing_columns = [col for col in required_columns if col not in paciente_columns]
        
        if missing_columns:
            print(f"🔧 Corrigindo colunas faltantes na tabela paciente: {missing_columns}")
            
            # Adicionar colunas faltantes
            for col in missing_columns:
                try:
                    if col in ['data_cadastro', 'ultima_atualizacao']:
                        cursor.execute(f"ALTER TABLE paciente ADD COLUMN {col} DATETIME")
                    else:
                        cursor.execute(f"ALTER TABLE paciente ADD COLUMN {col} TEXT")
                except Exception as e:
                    print(f"ℹ️ Coluna {col}: {e}")
            
            # Atualizar registros existentes
            now = datetime.now().isoformat()
            cursor.execute("UPDATE paciente SET categoria = 'particular' WHERE categoria IS NULL")
            cursor.execute("UPDATE paciente SET data_cadastro = ? WHERE data_cadastro IS NULL", (now,))
            cursor.execute("UPDATE paciente SET ultima_atualizacao = ? WHERE ultima_atualizacao IS NULL", (now,))
            
            conn.commit()
            print("✅ Banco de dados corrigido automaticamente")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"AVISO: Erro ao verificar banco: {e}")
        return False

# Executar verificação na inicialização
check_database_sync()

# Configuração do menu global
@app.before_request
def set_menu_items():
    """Define g.menu_items com valor padrão antes de cada requisição"""
    if not hasattr(g, 'menu_items') or g.menu_items is None:
        g.menu_items = []

# ---------------- MODELOS ----------------
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)  # CPF como identificador principal
    senha = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="recepcao")  # admin, recepcao, profissional
    profissional_id = db.Column(db.Integer, db.ForeignKey('profissional.id'))  # se for vinculado a um profissional
    primeiro_acesso = db.Column(db.Boolean, default=True)  # para controlar primeiro login
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acesso = db.Column(db.DateTime)

class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)  # CPF como identificador único
    telefone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120))
    data_nascimento = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    observacoes = db.Column(db.Text)
    convenio = db.Column(db.String(120))
    categoria = db.Column(db.String(20), default="particular")  # particular, convenio, emergencia
    tags = db.Column(db.Text)  # JSON com tags do paciente
    favorito = db.Column(db.Boolean, default=False)  # Marcação de favorito
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ultima_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Profissional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    especialidade = db.Column(db.String(120))
    telefone = db.Column(db.String(30))
    email = db.Column(db.String(120))
    horarios = db.Column(db.Text)  # JSON com disponibilidade simples (ex: {"segunda":["08:00-12:00","14:00-18:00"],...})

    usuarios = db.relationship('Usuario', backref='profissional', lazy=True)

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
    data = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    hora = db.Column(db.String(5), nullable=False)   # HH:MM
    duracao = db.Column(db.Integer, default=30)
    status = db.Column(db.String(20), default="Agendado")  # Agendado, Confirmado, Realizado, Cancelado, Falta
    observacoes = db.Column(db.Text)
    origem = db.Column(db.String(20))  # telefone / WhatsApp / online
    valor_pago = db.Column(db.Float, default=0.0)

    paciente = db.relationship('Paciente')
    profissional = db.relationship('Profissional')
    servico = db.relationship('Servico')

class Prontuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    data = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    anotacao = db.Column(db.Text, nullable=False)
    paciente = db.relationship('Paciente')

class HistoricoAtividade(db.Model):
    """Modelo para histórico de atividades do paciente"""
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    tipo_atividade = db.Column(db.String(50), nullable=False)  # consulta, exame, retorno, etc.
    descricao = db.Column(db.Text, nullable=False)
    data_atividade = db.Column(db.DateTime, default=datetime.utcnow)
    profissional_id = db.Column(db.Integer, db.ForeignKey('profissional.id'))
    agendamento_id = db.Column(db.Integer, db.ForeignKey('agendamento.id'))
    
    paciente = db.relationship('Paciente')
    profissional = db.relationship('Profissional')
    agendamento = db.relationship('Agendamento')

# ---------------- HELPERS ----------------
def validar_cpf(cpf):
    """Valida CPF brasileiro"""
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # PERMITE CPFs de teste para desenvolvimento
    cpfs_teste = ['00000000000', '11111111111', '22222222222', '33333333333']
    if cpf in cpfs_teste:
        return True
    
    # Verifica se todos os dígitos são iguais (exceto CPFs de teste)
    if cpf == cpf[0] * 11:
        return False
    
    # Validação do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    if resto < 2:
        digito1 = 0
    else:
        digito1 = 11 - resto
    
    if int(cpf[9]) != digito1:
        return False
    
    # Validação do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    if resto < 2:
        digito2 = 0
    else:
        digito2 = 11 - resto
    
    if int(cpf[10]) != digito2:
        return False
    
    return True

def gerar_senha_inicial(cpf):
    """Gera senha inicial baseada nos 3 primeiros dígitos do CPF"""
    cpf_limpo = re.sub(r'[^0-9]', '', cpf)
    return cpf_limpo[:3]

def require_login(role=None):
    """Decorator para controle de acesso baseado em perfis"""
    def decorator(fn):
        def wrapper(*args, **kwargs):
            if 'usuario' not in session:
                return redirect(url_for('login'))
            
            # Verifica se o usuário tem o perfil necessário
            if role:
                if isinstance(role, (list, tuple)):
                    if session.get('role') not in role:
                        flash(f"Sem permissão para acessar. Perfil necessário: {', '.join(role)}", "warning")
                        return redirect(url_for('dashboard'))
                else:
                    if session.get('role') != role:
                        flash(f"Sem permissão para acessar. Perfil necessário: {role}", "warning")
                        return redirect(url_for('dashboard'))
            
            return fn(*args, **kwargs)
        wrapper.__name__ = fn.__name__
        return wrapper
    return decorator

def verificar_permissao(acao):
    """Verifica se o usuário atual tem permissão para uma ação específica"""
    role = session.get('role')
    
    permissoes = {
        'admin': {
            'criar_usuarios': True,
            'deletar_usuarios': True,
            'alterar_permissoes': True,
            'acesso_total': True,
            'gerenciar_sistema': True
        },
        'recepcao': {
            'criar_usuarios': False,
            'deletar_usuarios': False,
            'alterar_permissoes': False,
            'acesso_total': False,
            'gerenciar_sistema': False,
            'gerenciar_pacientes': True,
            'gerenciar_agendamentos': True,
            'gerenciar_servicos': True
        },
        'profissional': {
            'criar_usuarios': False,
            'deletar_usuarios': False,
            'alterar_permissoes': False,
            'acesso_total': False,
            'gerenciar_sistema': False,
            'visualizar_agenda': True,
            'gerenciar_prontuarios': True,
            'atualizar_consultas': True
        }
    }
    
    return permissoes.get(role, {}).get(acao, False)

def to_datetime(dstr, tstr):
    return datetime.strptime(f"{dstr} {tstr}", "%Y-%m-%d %H:%M")

def conflito(profissional_id, data, hora, duracao, agendamento_id=None):
    """Retorna True se houver conflito de horário com o profissional."""
    inicio = to_datetime(data, hora)
    fim = inicio + timedelta(minutes=duracao)
    eventos = Agendamento.query.filter_by(profissional_id=profissional_id, data=data).all()
    for ev in eventos:
        if agendamento_id and ev.id == agendamento_id:
            continue
        ev_inicio = to_datetime(ev.data, ev.hora)
        ev_fim = ev_inicio + timedelta(minutes=ev.duracao)
        # sobreposição: startA < endB and startB < endA
        if inicio < ev_fim and ev_inicio < fim and ev.status not in ["Cancelado"]:
            return True
    return False

# ---------------- ROTAS DE AUTENTICAÇÃO ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cpf = request.form.get('cpf')
        senha = request.form.get('senha')
        
        # Validações básicas
        if not cpf or not senha:
            return render_template('login.html', title="Login", erro="CPF e senha são obrigatórios")
        
        # Valida CPF
        if not validar_cpf(cpf):
            return render_template('login.html', title="Login", erro="CPF inválido")
        
        # Limpa CPF para busca no banco
        cpf_limpo = re.sub(r'[^0-9]', '', cpf)
        
        # Busca usuário pelo CPF
        user = Usuario.query.filter_by(cpf=cpf_limpo).first()
        
        if user:
            # Verifica se é primeiro acesso
            if user.primeiro_acesso:
                # Para primeiro acesso, senha deve ser os 3 primeiros dígitos do CPF
                senha_inicial = gerar_senha_inicial(cpf_limpo)
                if senha == senha_inicial:
                    # Primeiro login bem-sucedido, redireciona para troca de senha
                    session['usuario'] = user.cpf
                    session['role'] = user.role
                    session['profissional_id'] = user.profissional_id
                    session['primeiro_acesso'] = True
                    session['nome'] = user.nome
                    return redirect(url_for('trocar_senha'))
                else:
                    return render_template('login.html', title="Login", erro="Senha inicial incorreta")
            else:
                # Login normal
                if check_password_hash(user.senha, senha):
                    # Atualiza último acesso
                    user.ultimo_acesso = datetime.utcnow()
                    db.session.commit()
                    
                    session['usuario'] = user.cpf
                    session['role'] = user.role
                    session['profissional_id'] = user.profissional_id
                    session['primeiro_acesso'] = False
                    session['nome'] = user.nome
                    
                    flash(f"Bem-vindo(a), {user.nome}!", "success")
                    return redirect(url_for('dashboard'))
                else:
                    return render_template('login.html', title="Login", erro="Senha incorreta")
        else:
            return render_template('login.html', title="Login", erro="CPF não cadastrado no sistema")
    
    return render_template('login.html', title="Login")

@app.route('/trocar-senha', methods=['GET', 'POST'])
def trocar_senha():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')
        
        if not nova_senha or not confirmar_senha:
            flash("Todos os campos são obrigatórios", "danger")
            return render_template('trocar_senha.html', title="Trocar Senha")
        
        if nova_senha != confirmar_senha:
            flash("As senhas não coincidem", "danger")
            return render_template('trocar_senha.html', title="Trocar Senha")
        
        if len(nova_senha) < 6:
            flash("A nova senha deve ter pelo menos 6 caracteres", "danger")
            return render_template('trocar_senha.html', title="Trocar Senha")
        
        # Atualiza senha e marca como não sendo primeiro acesso
        user = Usuario.query.filter_by(cpf=session['usuario']).first()
        if user:
            user.senha = generate_password_hash(nova_senha)
            user.primeiro_acesso = False
            db.session.commit()
            
            session['primeiro_acesso'] = False
            flash("Senha alterada com sucesso! Agora você pode acessar o sistema normalmente.", "success")
            return redirect(url_for('dashboard'))
    
    return render_template('trocar_senha.html', title="Trocar Senha")

@app.route('/logout')
def logout():
    session.clear()
    flash("Você saiu do sistema com sucesso", "info")
    return redirect(url_for('login'))

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
@require_login()
def dashboard():
    hoje = date.today().strftime("%Y-%m-%d")
    prof_id = session.get('profissional_id')
    
    # Usar joinedload para carregar relacionamentos de uma vez
    q = Agendamento.query.options(
        joinedload(Agendamento.paciente),
        joinedload(Agendamento.profissional),
        joinedload(Agendamento.servico)
    ).filter_by(data=hoje)
    
    if session.get('role') == 'profissional' and prof_id:
        q = q.filter_by(profissional_id=prof_id)
    
    proximos = q.order_by(Agendamento.hora.asc()).all() or []
    
    # Garantir que total_receita seja um número válido
    total_receita_raw = db.session.query(db.func.sum(Agendamento.valor_pago)).scalar()
    if total_receita_raw is None:
        total_receita = 0.0
    else:
        try:
            total_receita = float(total_receita_raw)
        except (ValueError, TypeError):
            total_receita = 0.0
    
    # Adicionar contadores para as estatísticas
    profissionais_count = Profissional.query.count() or 0
    servicos_count = Servico.query.count() or 0
    
    # Calcular estatísticas rápidas reais
    try:
        # Taxa de confirmação
        total_agendamentos = Agendamento.query.count()
        confirmados = Agendamento.query.filter_by(status="Confirmado").count()
        taxa_confirmacao = (confirmados / total_agendamentos * 100) if total_agendamentos > 0 else 0
        
        # Pacientes ativos (últimos 30 dias)
        data_limite = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        pacientes_ativos = db.session.query(
            db.func.count(db.func.distinct(Agendamento.paciente_id))
        ).filter(
            Agendamento.data >= data_limite
        ).scalar() or 0
        
        # Consultas por mês (últimos 30 dias)
        consultas_mes = Agendamento.query.filter(
            Agendamento.data >= data_limite
        ).count()
        
    except Exception as e:
        print(f"Erro ao calcular estatísticas: {e}")
        taxa_confirmacao = 0
        pacientes_ativos = 0
        consultas_mes = 0
    
    return render_template('dashboard.html', title="Dashboard", 
                         proximos=proximos, 
                         total_receita=total_receita,
                         profissionais_count=profissionais_count,
                         servicos_count=servicos_count,
                         taxa_confirmacao=round(taxa_confirmacao, 1),
                         pacientes_ativos=pacientes_ativos,
                         consultas_mes=consultas_mes)

# ---------------- PACIENTES ----------------
@app.route('/pacientes', methods=['GET', 'POST'])
@require_login(role=['admin','recepcao','profissional'])
def pacientes():
    if request.method == 'POST' and session.get('role') in ['admin','recepcao']:
        # Processar tags
        tags_input = request.form.get('tags', '')
        tags_list = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
        tags_json = json.dumps(tags_list) if tags_list else None
        
        p = Paciente(
            nome=request.form.get('nome'),
            cpf=request.form.get('cpf'),
            telefone=request.form.get('telefone'),
            email=request.form.get('email'),
            data_nascimento=request.form.get('data_nascimento'),
            observacoes=request.form.get('observacoes'),
            convenio=request.form.get('convenio'),
            categoria=request.form.get('categoria'),
            tags=tags_json,
            favorito=request.form.get('favorito') == 'on'
        )
        db.session.add(p)
        db.session.commit()
        
        # Criar histórico de atividade
        historico = HistoricoAtividade(
            paciente_id=p.id,
            tipo_atividade='cadastro',
            descricao=f'Paciente cadastrado no sistema',
            profissional_id=session.get('profissional_id')
        )
        db.session.add(historico)
        db.session.commit()
        
        return redirect(url_for('pacientes'))
    
    # Filtros avançados
    filtro_idade = request.args.get('idade', '')
    filtro_categoria = request.args.get('categoria', '')
    filtro_favorito = request.args.get('favorito', '')
    filtro_tags = request.args.get('tags', '')
    
    query = Paciente.query
    
    # Aplicar filtros
    if filtro_idade:
        hoje = date.today()
        if filtro_idade == '0-18':
            data_limite = hoje - timedelta(days=18*365)
            query = query.filter(Paciente.data_nascimento >= data_limite.strftime('%Y-%m-%d'))
        elif filtro_idade == '19-30':
            data_limite_inf = hoje - timedelta(days=30*365)
            data_limite_sup = hoje - timedelta(days=19*365)
            query = query.filter(
                Paciente.data_nascimento <= data_limite_inf.strftime('%Y-%m-%d'),
                Paciente.data_nascimento >= data_limite_sup.strftime('%Y-%m-%d')
            )
        elif filtro_idade == '31-50':
            data_limite_inf = hoje - timedelta(days=50*365)
            data_limite_sup = hoje - timedelta(days=31*365)
            query = query.filter(
                Paciente.data_nascimento <= data_limite_inf.strftime('%Y-%m-%d'),
                Paciente.data_nascimento >= data_limite_sup.strftime('%Y-%m-%d')
            )
        elif filtro_idade == '51+':
            data_limite = hoje - timedelta(days=51*365)
            query = query.filter(Paciente.data_nascimento <= data_limite.strftime('%Y-%m-%d'))
    
    if filtro_categoria:
        query = query.filter(Paciente.categoria == filtro_categoria)
    
    if filtro_favorito == 'true':
        query = query.filter(Paciente.favorito == True)
    
    if filtro_tags:
        query = query.filter(Paciente.tags.contains(filtro_tags))
    
    lista = query.order_by(Paciente.nome.asc()).all()
    
    # Processar tags para exibição
    for paciente in lista:
        if paciente.tags:
            try:
                paciente.tags_list = json.loads(paciente.tags)
            except:
                paciente.tags_list = []
        else:
            paciente.tags_list = []
    
    return render_template('pacientes.html', pacientes=lista)

@app.route('/api/verificar-duplicatas', methods=['POST'])
def verificar_duplicatas():
    """API para verificar duplicatas de pacientes"""
    try:
        data = request.get_json()
        cpf = re.sub(r'[^\d]', '', data.get('cpf', ''))
        email = data.get('email', '').strip()
        telefone = re.sub(r'[^\d]', '', data.get('telefone', ''))
        
        duplicatas = []
        
        # Verificar CPF duplicado
        if cpf:
            paciente_cpf = Paciente.query.filter_by(cpf=cpf).first()
            if paciente_cpf:
                duplicatas.append({
                    'tipo': 'CPF',
                    'valor': cpf,
                    'paciente_id': paciente_cpf.id,
                    'paciente_nome': paciente_cpf.nome
                })
        
        # Verificar email duplicado (se fornecido)
        if email:
            paciente_email = Paciente.query.filter_by(email=email).first()
            if paciente_email:
                duplicatas.append({
                    'tipo': 'Email',
                    'valor': email,
                    'paciente_id': paciente_email.id,
                    'paciente_nome': paciente_email.nome
                })
        
        # Verificar telefone duplicado
        if telefone:
            paciente_telefone = Paciente.query.filter_by(telefone=telefone).first()
            if paciente_telefone:
                duplicatas.append({
                    'tipo': 'Telefone',
                    'valor': telefone,
                    'paciente_id': paciente_telefone.id,
                    'paciente_nome': paciente_telefone.nome
                })
        
        return jsonify({
            'success': True,
            'duplicatas': duplicatas,
            'total': len(duplicatas)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/paciente/<int:paciente_id>/favorito', methods=['POST'])
@require_login()
def toggle_favorito(paciente_id):
    """Alterna o status de favorito do paciente"""
    paciente = Paciente.query.get_or_404(paciente_id)
    paciente.favorito = not paciente.favorito
    
    # Criar histórico de atividade
    acao = 'marcado como favorito' if paciente.favorito else 'removido dos favoritos'
    historico = HistoricoAtividade(
        paciente_id=paciente.id,
        tipo_atividade='favorito',
        descricao=f'Paciente {acao}',
        profissional_id=session.get('profissional_id')
    )
    db.session.add(historico)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'favorito': paciente.favorito,
        'message': f'Paciente {acao} com sucesso!'
    })

@app.route('/api/paciente/<int:paciente_id>/historico')
@require_login()
def historico_paciente(paciente_id):
    """Retorna o histórico de atividades do paciente"""
    paciente = Paciente.query.get_or_404(paciente_id)
    historico = HistoricoAtividade.query.filter_by(paciente_id=paciente_id)\
        .order_by(HistoricoAtividade.data_atividade.desc())\
        .limit(20).all()
    
    historico_data = []
    for h in historico:
        historico_data.append({
            'id': h.id,
            'tipo': h.tipo_atividade,
            'descricao': h.descricao,
            'data': h.data_atividade.strftime('%d/%m/%Y %H:%M'),
            'profissional': h.profissional.nome if h.profissional else 'Sistema'
        })
    
    return jsonify({
        'success': True,
        'historico': historico_data
    })

@app.route('/api/paciente/<int:paciente_id>/tags', methods=['POST'])
@require_login()
def atualizar_tags_paciente(paciente_id):
    """Atualiza as tags do paciente"""
    paciente = Paciente.query.get_or_404(paciente_id)
    data = request.get_json()
    tags = data.get('tags', [])
    
    paciente.tags = json.dumps(tags)
    
    # Criar histórico de atividade
    historico = HistoricoAtividade(
        paciente_id=paciente.id,
        tipo_atividade='tags',
        descricao=f'Tags atualizadas: {", ".join(tags)}',
        profissional_id=session.get('profissional_id')
    )
    db.session.add(historico)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'tags': tags,
        'message': 'Tags atualizadas com sucesso!'
    })

# ---------------- PROFISSIONAIS ----------------
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
    lista = Profissional.query.order_by(Profissional.nome.asc()).all() or []
    return render_template('profissionais.html', title="Profissionais", profissionais=lista)

# ---------------- USUÁRIOS (ADMIN) ----------------
@app.route('/usuarios', methods=['GET', 'POST'])
@require_login(role=['admin'])
def usuarios():
    if request.method == 'POST':
        nome = request.form.get('nome')
        cpf = request.form.get('cpf')
        role = request.form.get('role')
        
        # Validações
        if not nome or not cpf:
            flash("Nome e CPF são obrigatórios", "danger")
            return redirect(url_for('usuarios'))
        
        if not validar_cpf(cpf):
            flash("CPF inválido", "danger")
            return redirect(url_for('usuarios'))
        
        cpf_limpo = re.sub(r'[^0-9]', '', cpf)
        
        # Verifica se CPF já existe
        if Usuario.query.filter_by(cpf=cpf_limpo).first():
            flash("CPF já cadastrado no sistema", "danger")
            return redirect(url_for('usuarios'))
        
        # Gera senha inicial (3 primeiros dígitos do CPF)
        senha_inicial = gerar_senha_inicial(cpf_limpo)
        
        u = Usuario(
            nome=nome,
            cpf=cpf_limpo,
            senha=generate_password_hash(senha_inicial),
            role=role,
            primeiro_acesso=True
        )
        db.session.add(u)
        db.session.commit()
        
        flash(f"Usuário {nome} cadastrado com sucesso! Senha inicial: {senha_inicial}", "success")
        return redirect(url_for('usuarios'))
    
    usuarios = Usuario.query.all() or []
    return render_template('usuarios.html', title="Usuários", usuarios=usuarios)

# ---------------- SERVIÇOS ----------------
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
    lista = Servico.query.order_by(Servico.nome.asc()).all() or []
    return render_template('servicos.html', title="Serviços", servicos=lista)

# ---------------- AGENDA ----------------
@app.route('/agenda', methods=['GET', 'POST'])
@require_login(role=['admin','recepcao','profissional'])
def agenda():
    if request.method == 'POST':
        # Validações básicas
        if not all([request.form.get('paciente_id'), request.form.get('profissional_id'), 
                   request.form.get('servico_id'), request.form.get('data'), request.form.get('hora')]):
            flash("Todos os campos são obrigatórios", "danger")
            return redirect(url_for('agenda'))
        
        # Verifica conflito de horário
        if conflito(request.form.get('profissional_id'), request.form.get('data'), 
                   request.form.get('hora'), int(request.form.get('duracao_min') or 30)):
            flash("Horário indisponível para este profissional", "warning")
            return redirect(url_for('agenda'))
        
        a = Agendamento(
            paciente_id=request.form.get('paciente_id'),
            profissional_id=request.form.get('profissional_id'),
            servico_id=request.form.get('servico_id'),
            data=request.form.get('data'),
            hora=request.form.get('hora'),
            duracao=int(request.form.get('duracao_min') or 30),
            observacoes=request.form.get('observacoes'),
            origem=request.form.get('origem') or 'online'
        )
        db.session.add(a)
        db.session.commit()
        flash("Agendamento criado com sucesso!", "success")
        return redirect(url_for('agenda'))
    
    pacientes = Paciente.query.order_by(Paciente.nome.asc()).all() or []
    profissionais = Profissional.query.order_by(Profissional.nome.asc()).all() or []
    servicos = Servico.query.order_by(Servico.nome.asc()).all() or []
    
    # Filtra agendamentos por profissional se não for admin
    prof_id = session.get('profissional_id')
    if session.get('role') == 'profissional' and prof_id:
        agendamentos = Agendamento.query.filter_by(profissional_id=prof_id).order_by(Agendamento.data.desc(), Agendamento.hora.desc()).all() or []
    else:
        agendamentos = Agendamento.query.order_by(Agendamento.data.desc(), Agendamento.hora.desc()).all() or []
    
    # Pegar dia atual ou do filtro
    dia = request.args.get('dia') or date.today().strftime("%Y-%m-%d")
    
    # Filtrar agendamentos por data se especificada
    if request.args.get('dia'):
        agendamentos = [a for a in agendamentos if a.data == dia]
    
    return render_template('agenda.html', title="Agenda", 
                         pacientes=pacientes, 
                         profissionais=profissionais, 
                         servicos=servicos, 
                         agendamentos=agendamentos,
                         dia=dia)

# ---------------- RELATÓRIOS ----------------
@app.route('/relatorios')
@require_login(role=['admin'])
def relatorios():
    """Página de relatórios com dados reais do sistema"""
    try:
        # Calcular estatísticas básicas
        total_pacientes = Paciente.query.count()
        total_profissionais = Profissional.query.count()
        total_agendamentos = Agendamento.query.count()
        
        # Calcular estatísticas do mês atual
        hoje = datetime.now()
        inicio_mes = hoje.replace(day=1)
        
        agendamentos_mes = Agendamento.query.filter(
            Agendamento.data >= inicio_mes.strftime('%Y-%m-%d')
        ).count()
        
        # Calcular receita do mês
        receita_mes = db.session.query(
            db.func.sum(Agendamento.valor_pago)
        ).filter(
            Agendamento.data >= inicio_mes.strftime('%Y-%m-%d'),
            Agendamento.status == "Realizado",
            Agendamento.valor_pago > 0
        ).scalar() or 0
        
        # Calcular taxa de confirmação
        confirmados = Agendamento.query.filter_by(status="Confirmado").count()
        taxa_confirmacao = (confirmados / total_agendamentos * 100) if total_agendamentos > 0 else 0
        
        # Calcular faltas
        faltas = Agendamento.query.filter_by(status="Falta").count()
        
        # Calcular receita total
        receita_total = db.session.query(
            db.func.sum(Agendamento.valor_pago)
        ).filter(
            Agendamento.status == "Realizado",
            Agendamento.valor_pago > 0
        ).scalar() or 0
        
        # Receita por profissional
        receita_por_prof = db.session.query(
            Profissional.nome,
            db.func.sum(Agendamento.valor_pago)
        ).join(Agendamento).filter(
            Agendamento.status == "Realizado",
            Agendamento.valor_pago > 0
        ).group_by(Profissional.id, Profissional.nome).order_by(
            db.func.sum(Agendamento.valor_pago).desc()
        ).all()
        
        return render_template('relatorios.html', 
                             title="Relatórios",
                             total_pacientes=total_pacientes,
                             total_profissionais=total_profissionais,
                             agendamentos_mes=agendamentos_mes,
                             receita_mes=receita_mes,
                             taxa_confirmacao=taxa_confirmacao,
                             faltas=faltas,
                             receita_total=receita_total,
                             receita_por_prof=receita_por_prof)
    except Exception as e:
        print(f"Erro ao carregar relatórios: {e}")
        # Retornar valores padrão em caso de erro
        return render_template('relatorios.html', 
                             title="Relatórios",
                             total_pacientes=0,
                             total_profissionais=0,
                             agendamentos_mes=0,
                             receita_mes=0,
                             taxa_confirmacao=0,
                             faltas=0,
                             receita_total=0,
                             receita_por_prof=[])

# ---------------- CONFIGURAÇÕES ----------------
@app.route('/configuracoes')
@require_login(role=['admin'])
def configuracoes():
    return render_template('configuracoes.html', title="Configurações")

# ---------------- API RELATÓRIOS ----------------
@app.route('/api/relatorios/agendamentos-por-dia')
@require_login(role=['admin'])
def api_agendamentos_por_dia():
    """Retorna agendamentos por dia dos últimos N dias"""
    from datetime import datetime, timedelta
    hoje = datetime.now()
    dias = request.args.get('dias', 30, type=int)
    inicio = hoje - timedelta(days=dias)
    
    query = db.session.query(
        Agendamento.data,
        db.func.count(Agendamento.id).label('total')
    ).filter(
        Agendamento.data >= inicio.strftime('%Y-%m-%d')
    ).group_by(Agendamento.data).order_by(Agendamento.data)
    
    dados = query.all()
    
    # Formatar datas para exibição
    labels = []
    for d in dados:
        if d.data:
            try:
                data_obj = datetime.strptime(d.data, '%Y-%m-%d')
                if dias <= 30:
                    labels.append(data_obj.strftime('%d/%m'))
                else:
                    labels.append(data_obj.strftime('%m/%Y'))
            except:
                labels.append(d.data)
        else:
            labels.append("")
    
    return jsonify({
        'success': True,
        'labels': labels,
        'datasets': [{
            'label': 'Agendamentos',
            'data': [d.total or 0 for d in dados],
            'backgroundColor': 'rgba(13, 110, 253, 0.2)',
            'borderColor': 'rgba(13, 110, 253, 1)',
            'borderWidth': 2,
            'fill': True,
            'tension': 0.4
        }]
    })

@app.route('/api/relatorios/agendamentos-por-profissional')
@require_login(role=['admin'])
def api_agendamentos_por_profissional():
    """Retorna agendamentos por profissional"""
    try:
        from datetime import datetime, timedelta
        hoje = datetime.now()
        inicio = hoje - timedelta(days=30)
        
        query = db.session.query(
            Profissional.nome,
            db.func.count(Agendamento.id).label('total')
        ).join(Agendamento).filter(
            Agendamento.data >= inicio.strftime('%Y-%m-%d')
        ).group_by(Profissional.id, Profissional.nome).order_by(
            db.func.count(Agendamento.id).desc()
        ).limit(10)
        
        dados = query.all()
        
        return jsonify({
            'success': True,
            'labels': [d.nome for d in dados],
            'datasets': [{
                'data': [d.total for d in dados],
                'backgroundColor': [
                    '#0d6efd', '#198754', '#ffc107', '#dc3545', '#6f42c1',
                    '#fd7e14', '#20c997', '#e83e8c', '#6c757d', '#0dcaf0'
                ]
            }]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/relatorios/receita-por-mes')
@require_login(role=['admin'])
def api_receita_por_mes():
    """Retorna receita por mês dos últimos 12 meses"""
    try:
        from datetime import datetime, timedelta
        hoje = datetime.now()
        
        # Últimos 12 meses
        labels = []
        dados = []
        
        for i in range(12):
            data = hoje - timedelta(days=30*i)
            inicio_mes = data.replace(day=1)
            fim_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            receita = db.session.query(
                db.func.sum(Agendamento.valor_pago)
            ).filter(
                Agendamento.data >= inicio_mes.strftime('%Y-%m-%d'),
                Agendamento.data <= fim_mes.strftime('%Y-%m-%d'),
                Agendamento.status == "Realizado",
                Agendamento.valor_pago > 0
            ).scalar() or 0
            
            labels.insert(0, inicio_mes.strftime('%m/%Y'))
            dados.insert(0, float(receita))
        
        return jsonify({
            'success': True,
            'labels': labels,
            'datasets': [{
                'label': 'Receita Mensal',
                'data': dados,
                'backgroundColor': 'rgba(25, 135, 84, 0.2)',
                'borderColor': 'rgba(25, 135, 84, 1)',
                'borderWidth': 2,
                'fill': True,
                'tension': 0.4
            }]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/relatorios/status-agendamentos')
@require_login(role=['admin'])
def api_status_agendamentos():
    """Retorna status dos agendamentos para gráfico de pizza"""
    try:
        from datetime import datetime, timedelta
        hoje = datetime.now()
        inicio = hoje - timedelta(days=30)
        
        query = db.session.query(
            Agendamento.status,
            db.func.count(Agendamento.id).label('total')
        ).filter(
            Agendamento.data >= inicio.strftime('%Y-%m-%d')
        ).group_by(Agendamento.status)
        
        dados = query.all()
        
        # Mapear cores para cada status
        cores = {
            'Agendado': '#ffc107',
            'Confirmado': '#0d6efd',
            'Realizado': '#198754',
            'Cancelado': '#dc3545',
            'Falta': '#6c757d'
        }
        
        return jsonify({
            'success': True,
            'labels': [d.status or "" for d in dados],
            'datasets': [{
                'label': 'Quantidade',
                'data': [d.total or 0 for d in dados],
                'backgroundColor': [cores.get(d.status or "", '#6c757d') for d in dados],
                'borderWidth': 2,
                'borderColor': '#ffffff'
            }]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/relatorios/horarios-populares')
@require_login(role=['admin'])
def api_horarios_populares():
    """Retorna horários mais populares"""
    try:
        from datetime import datetime, timedelta
        hoje = datetime.now()
        inicio = hoje - timedelta(days=30)
        
        query = db.session.query(
            Agendamento.hora,
            db.func.count(Agendamento.id).label('total')
        ).filter(
            Agendamento.data >= inicio.strftime('%Y-%m-%d')
        ).group_by(Agendamento.hora).order_by(
            db.func.count(Agendamento.id).desc()
        ).limit(8)
        
        dados = query.all()
        
        return jsonify({
            'success': True,
            'labels': [d.hora for d in dados],
            'datasets': [{
                'label': 'Agendamentos',
                'data': [d.total for d in dados],
                'backgroundColor': 'rgba(13, 110, 253, 0.8)',
                'borderColor': 'rgba(13, 110, 253, 1)',
                'borderWidth': 1
            }]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics/conversao-status')
@require_login(role=['admin'])
def api_conversao_status():
    """Retorna taxa de conversão entre status de agendamentos"""
    from datetime import datetime, timedelta
    hoje = datetime.now()
    inicio = hoje - timedelta(days=30)
    
    query = db.session.query(
        Agendamento.status,
        db.func.count(Agendamento.id).label('total')
    ).filter(
        Agendamento.data >= inicio.strftime('%Y-%m-%d')
    ).group_by(Agendamento.status)
    
    dados = query.all()
    
    # Mapear cores para cada status
    cores = {
        'Agendado': '#ffc107',
        'Confirmado': '#0d6efd',
        'Realizado': '#198754',
        'Cancelado': '#dc3545',
        'Falta': '#6c757d'
    }
    
    return jsonify({
        'success': True,
        'labels': [d.status or "" for d in dados],
        'datasets': [{
            'label': 'Quantidade',
            'data': [d.total or 0 for d in dados],
            'backgroundColor': [cores.get(d.status or "", '#6c757d') for d in dados],
            'borderWidth': 2,
            'borderColor': '#ffffff'
        }]
    })

@app.route('/api/analytics/estatisticas-gerais')
@require_login(role=['admin'])
def api_estatisticas_gerais():
    """Retorna estatísticas gerais para cards resumo"""
    from datetime import datetime, timedelta
    hoje = datetime.now()
    inicio_mes = hoje - timedelta(days=30)
    inicio_semana = hoje - timedelta(days=7)
    
    # Estatísticas do mês
    agendamentos_mes = Agendamento.query.filter(
        Agendamento.data >= inicio_mes.strftime('%Y-%m-%d')
    ).count()
    
    receita_mes = db.session.query(
        db.func.sum(Agendamento.valor_pago)
    ).filter(
        Agendamento.data >= inicio_mes.strftime('%Y-%m-%d'),
        Agendamento.valor_pago > 0
    ).scalar() or 0
    
    # Estatísticas da semana
    agendamentos_semana = Agendamento.query.filter(
        Agendamento.data >= inicio_semana.strftime('%Y-%m-%d')
    ).count()
    
    # Taxa de faltas
    total_agendamentos = Agendamento.query.count()
    faltas = Agendamento.query.filter_by(status="Falta").count()
    taxa_faltas = (faltas / total_agendamentos * 100) if total_agendamentos > 0 else 0
    
    return jsonify({
        'success': True,
        'agendamentos_mes': agendamentos_mes or 0,
        'receita_mes': float(receita_mes or 0),
        'agendamentos_semana': agendamentos_semana or 0,
        'taxa_faltas': round(taxa_faltas or 0, 1),
        'total_pacientes': Paciente.query.count() or 0,
        'total_profissionais': Profissional.query.count() or 0
    })

# ---------------- PRONTUÁRIO ----------------
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
    registros = Prontuario.query.filter_by(paciente_id=paciente_id).order_by(Prontuario.id.desc()).all() or []
    return render_template('prontuario.html', title="Prontuário", paciente=paciente, registros=registros)

# ---------------- CALENDÁRIO VISUAL ----------------
@app.route('/calendario')
@require_login(role=['admin','recepcao','profissional'])
def calendario():
    return render_template('calendario.html', title="Calendário")

# ---------------- SETUP INICIAL ----------------
with app.app_context():
    db.create_all()
    
    # Cria usuários padrão conforme README_SISTEMA_ACESSO.md
    usuarios_padrao = [
        {
            'nome': 'Administrador',
            'cpf': '00000000000',
            'senha': '000',
            'role': 'admin',
            'primeiro_acesso': True
        },
        {
            'nome': 'Recepção',
            'cpf': '11111111111',
            'senha': '111',
            'role': 'recepcao',
            'primeiro_acesso': True
        },
        {
            'nome': 'Profissional de Saúde',
            'cpf': '22222222222',
            'senha': '222',
            'role': 'profissional',
            'primeiro_acesso': True
        },
        {
            'nome': 'Desenvolvedor',
            'cpf': '33333333333',
            'senha': '333',
            'role': 'admin',
            'primeiro_acesso': True
        }
    ]
    
    for usuario_data in usuarios_padrao:
        if not Usuario.query.filter_by(cpf=usuario_data['cpf']).first():
            # Para usuários padrão, a senha inicial é os 3 primeiros dígitos do CPF
            senha_inicial = gerar_senha_inicial(usuario_data['cpf'])
            usuario = Usuario(
                nome=usuario_data['nome'],
                cpf=usuario_data['cpf'],
                senha=generate_password_hash(senha_inicial),
                role=usuario_data['role'],
                primeiro_acesso=usuario_data['primeiro_acesso']
            )
            db.session.add(usuario)
            print(f"✅ Usuário {usuario_data['nome']} criado - CPF: {usuario_data['cpf']}, Senha: {senha_inicial}")
    
    db.session.commit()
    print("🎯 Sistema configurado com usuários padrão conforme README_SISTEMA_ACESSO.md")

# ---------------- ROTAS CRUD FALTANTES ----------------

# Editar Paciente
@app.route('/pacientes/editar/<int:paciente_id>', methods=['GET', 'POST'])
@require_login(role=['admin','recepcao'])
def editar_paciente(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    
    if request.method == 'POST':
        paciente.nome = request.form.get('nome')
        paciente.telefone = request.form.get('telefone')
        paciente.email = request.form.get('email')
        paciente.data_nascimento = request.form.get('nascimento')
        paciente.observacoes = request.form.get('observacoes')
        paciente.convenio = request.form.get('convenio')
        
        db.session.commit()
        flash("Paciente atualizado com sucesso!", "success")
        return redirect(url_for('pacientes'))
    
    return render_template('editar_paciente.html', title="Editar Paciente", paciente=paciente)

# Excluir Paciente
@app.route('/pacientes/excluir/<int:paciente_id>', methods=['POST'])
@require_login(role=['admin','recepcao'])
def excluir_paciente(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    
    # Verificar se há agendamentos vinculados
    agendamentos = Agendamento.query.filter_by(paciente_id=paciente_id).count()
    if agendamentos > 0:
        flash(f"Não é possível excluir o paciente {paciente.nome}. Existem {agendamentos} agendamentos vinculados.", "warning")
        return redirect(url_for('pacientes'))
    
    db.session.delete(paciente)
    db.session.commit()
    flash(f"Paciente {paciente.nome} excluído com sucesso!", "success")
    return redirect(url_for('pacientes'))

# Editar Profissional
@app.route('/profissionais/editar/<int:prof_id>', methods=['GET', 'POST'])
@require_login(role=['admin'])
def editar_profissional(prof_id):
    profissional = Profissional.query.get_or_404(prof_id)
    
    if request.method == 'POST':
        profissional.nome = request.form.get('nome')
        profissional.especialidade = request.form.get('especialidade')
        profissional.telefone = request.form.get('telefone')
        profissional.email = request.form.get('email')
        profissional.horarios = request.form.get('horarios') or "{}"
        
        db.session.commit()
        flash("Profissional atualizado com sucesso!", "success")
        return redirect(url_for('profissionais'))
    
    return render_template('editar_profissional.html', title="Editar Profissional", profissional=profissional)

# Excluir Profissional
@app.route('/profissionais/excluir/<int:prof_id>', methods=['POST'])
@require_login(role=['admin'])
def excluir_profissional(prof_id):
    profissional = Profissional.query.get_or_404(prof_id)
    
    # Verificar se há agendamentos vinculados
    agendamentos = Agendamento.query.filter_by(profissional_id=prof_id).count()
    if agendamentos > 0:
        flash(f"Não é possível excluir o profissional {profissional.nome}. Existem {agendamentos} agendamentos vinculados.", "warning")
        return redirect(url_for('profissionais'))
    
    db.session.delete(profissional)
    db.session.commit()
    flash(f"Profissional {profissional.nome} excluído com sucesso!", "success")
    return redirect(url_for('profissionais'))

# Editar Serviço
@app.route('/servicos/editar/<int:servico_id>', methods=['GET', 'POST'])
@require_login(role=['admin','recepcao'])
def editar_servico(servico_id):
    servico = Servico.query.get_or_404(servico_id)
    
    if request.method == 'POST':
        servico.nome = request.form.get('nome')
        servico.duracao_min = int(request.form.get('duracao_min') or 30)
        servico.preco = float(request.form.get('preco') or 0)
        
        db.session.commit()
        flash("Serviço atualizado com sucesso!", "success")
        return redirect(url_for('servicos'))
    
    return render_template('editar_servico.html', title="Editar Serviço", servico=servico)

# Excluir Serviço
@app.route('/servicos/excluir/<int:servico_id>', methods=['POST'])
@require_login(role=['admin','recepcao'])
def excluir_servico(servico_id):
    servico = Servico.query.get_or_404(servico_id)
    
    # Verificar se há agendamentos vinculados
    agendamentos = Agendamento.query.filter_by(servico_id=servico_id).count()
    if agendamentos > 0:
        flash(f"Não é possível excluir o serviço {servico.nome}. Existem {agendamentos} agendamentos vinculados.", "warning")
        return redirect(url_for('servicos'))
    
    db.session.delete(servico)
    db.session.commit()
    flash(f"Serviço {servico.nome} excluído com sucesso!", "success")
    return redirect(url_for('servicos'))

# Editar Agendamento
@app.route('/agendamentos/editar/<int:ag_id>', methods=['GET', 'POST'])
@require_login(role=['admin','recepcao','profissional'])
def editar_agendamento(ag_id):
    agendamento = Agendamento.query.get_or_404(ag_id)
    
    if request.method == 'POST':
        # Verificar conflito antes de atualizar
        if conflito(request.form.get('profissional_id'), request.form.get('data'), 
                   request.form.get('hora'), int(request.form.get('duracao') or 30), ag_id):
            flash("Horário indisponível para este profissional", "warning")
            return redirect(url_for('editar_agendamento', ag_id=ag_id))
        
        agendamento.paciente_id = request.form.get('paciente_id')
        agendamento.profissional_id = request.form.get('profissional_id')
        agendamento.servico_id = request.form.get('servico_id')
        agendamento.data = request.form.get('data')
        agendamento.hora = request.form.get('hora')
        agendamento.duracao = int(request.form.get('duracao') or 30)
        agendamento.status = request.form.get('status')
        agendamento.origem = request.form.get('origem')
        agendamento.valor_pago = float(request.form.get('valor_pago') or 0)
        agendamento.observacoes = request.form.get('observacoes')
        
        db.session.commit()
        flash("Agendamento atualizado com sucesso!", "success")
        return redirect(url_for('agenda'))
    
    pacientes = Paciente.query.order_by(Paciente.nome.asc()).all()
    profissionais = Profissional.query.order_by(Profissional.nome.asc()).all()
    servicos = Servico.query.order_by(Servico.nome.asc()).all()
    
    return render_template('editar_agendamento.html', title="Editar Agendamento", 
                         agendamento=agendamento,
                         pacientes=pacientes,
                         profissionais=profissionais,
                         servicos=servicos)

# Cancelar Agendamento
@app.route('/agendamentos/cancelar/<int:ag_id>', methods=['POST'])
@require_login(role=['admin','recepcao','profissional'])
def cancelar_agendamento(ag_id):
    agendamento = Agendamento.query.get_or_404(ag_id)
    agendamento.status = "Cancelado"
    db.session.commit()
    flash(f"Agendamento de {agendamento.paciente.nome} cancelado com sucesso!", "success")
    return redirect(url_for('agenda'))

# Excluir Agendamento
@app.route('/agendamentos/excluir/<int:ag_id>', methods=['POST'])
@require_login(role=['admin','recepcao'])
def excluir_agendamento(ag_id):
    agendamento = Agendamento.query.get_or_404(ag_id)
    
    # Verifica se o agendamento pode ser excluído
    if agendamento.status in ['Realizado', 'Confirmado']:
        return jsonify({'success': False, 'message': 'Não é possível excluir agendamentos realizados ou confirmados'})
    
    paciente_nome = agendamento.paciente.nome
    db.session.delete(agendamento)
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Agendamento de {paciente_nome} excluído com sucesso!'})

# Excluir Usuário
@app.route('/usuarios/excluir/<int:user_id>', methods=['POST'])
@require_login(role=['admin'])
def excluir_usuario(user_id):
    usuario = Usuario.query.get_or_404(user_id)
    
    # Não permitir que o admin exclua a si mesmo
    if usuario.cpf == session.get('usuario'):
        flash("Você não pode excluir seu próprio usuário!", "warning")
        return redirect(url_for('usuarios'))
    
    db.session.delete(usuario)
    db.session.commit()
    flash(f"Usuário {usuario.nome} excluído com sucesso!", "success")
    return redirect(url_for('usuarios'))

# Reset de senha
@app.route('/usuarios/resetar-senha/<int:user_id>', methods=['POST'])
@require_login(role=['admin'])
def resetar_senha_usuario(user_id):
    usuario = Usuario.query.get_or_404(user_id)
    
    # Gerar nova senha inicial
    senha_inicial = gerar_senha_inicial(usuario.cpf)
    usuario.senha = generate_password_hash(senha_inicial)
    usuario.primeiro_acesso = True
    
    db.session.commit()
    flash(f"Senha de {usuario.nome} resetada para: {senha_inicial}", "success")
    return redirect(url_for('usuarios'))

# ---------------- API ENDPOINTS ----------------

# API para criar agendamentos
@app.route('/api/agendamentos', methods=['POST'])
@require_login(role=['admin','recepcao','profissional'])
def api_criar_agendamento():
    try:
        # Validações básicas
        if not all([request.form.get('paciente_id'), request.form.get('profissional_id'), 
                   request.form.get('servico_id'), request.form.get('data'), request.form.get('hora')]):
            return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'})
        
        # Verifica conflito de horário
        if conflito(request.form.get('profissional_id'), request.form.get('data'), 
                   request.form.get('hora'), int(request.form.get('duracao_min') or 30)):
            return jsonify({'success': False, 'message': 'Horário indisponível para este profissional'})
        
        # Cria o agendamento
        agendamento = Agendamento(
            paciente_id=request.form.get('paciente_id'),
            profissional_id=request.form.get('profissional_id'),
            servico_id=request.form.get('servico_id'),
            data=request.form.get('data'),
            hora=request.form.get('hora'),
            duracao=int(request.form.get('duracao_min') or 30),
            status=request.form.get('status') or 'Agendado',
            origem=request.form.get('origem') or 'online',
            valor_pago=float(request.form.get('valor_pago') or 0),
            observacoes=request.form.get('observacoes')
        )
        
        db.session.add(agendamento)
        db.session.commit()
        
        # Envia notificação de confirmação se configurado
        try:
            from services.notificacoes import GerenciadorNotificacoes
            gerenciador = GerenciadorNotificacoes()
            gerenciador.enviar_confirmacao_agendamento(agendamento)
        except Exception as e:
            print(f"Erro ao enviar notificação: {e}")
        
        return jsonify({'success': True, 'message': 'Agendamento criado com sucesso', 'id': agendamento.id})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao criar agendamento: {str(e)}'})

# API para atualizar status de agendamento
@app.route('/api/agendamentos/<int:ag_id>/status', methods=['PUT'])
@require_login(role=['admin','recepcao','profissional'])
def api_atualizar_status_agendamento(ag_id):
    try:
        data = request.get_json()
        status = data.get('status')
        
        if not status:
            return jsonify({'success': False, 'message': 'Status é obrigatório'})
        
        agendamento = Agendamento.query.get_or_404(ag_id)
        agendamento.status = status
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Status atualizado para {status}'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao atualizar status: {str(e)}'})

# API para criar pacientes
@app.route('/api/pacientes', methods=['POST'])
@require_login(role=['admin','recepcao'])
def api_criar_paciente():
    try:
        # Validações básicas
        if not request.form.get('nome') or not request.form.get('telefone'):
            return jsonify({'success': False, 'message': 'Nome e telefone são obrigatórios'})
        
        # Verifica se já existe paciente com este telefone
        telefone = request.form.get('telefone')
        paciente_existente = Paciente.query.filter_by(telefone=telefone).first()
        if paciente_existente:
            return jsonify({'success': False, 'message': 'Já existe um paciente com este telefone'})
        
        # Cria o paciente
        paciente = Paciente(
            nome=request.form.get('nome'),
            cpf=request.form.get('cpf') or None,
            telefone=telefone,
            email=request.form.get('email') or None,
            endereco=request.form.get('endereco') or None
        )
        
        db.session.add(paciente)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Paciente criado com sucesso', 'id': paciente.id})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao criar paciente: {str(e)}'})

# API para buscar horários disponíveis
@app.route('/api/horarios-disponiveis')
@require_login(role=['admin','recepcao','profissional'])
def api_horarios_disponiveis():
    try:
        profissional_id = request.args.get('profissional_id')
        data = request.args.get('data')
        servico_id = request.args.get('servico_id')
        
        if not all([profissional_id, data, servico_id]):
            return jsonify({'success': False, 'message': 'Parâmetros incompletos'})
        
        # Busca serviço para obter duração
        servico = Servico.query.get(servico_id)
        if not servico:
            return jsonify({'success': False, 'message': 'Serviço não encontrado'})
        
        duracao = servico.duracao_min
        
        # Gera horários disponíveis (8:00 às 18:00, intervalos de 30 min)
        horarios_disponiveis = []
        horarios_ocupados = []
        
        # Busca agendamentos existentes para o profissional na data
        agendamentos = Agendamento.query.filter_by(
            profissional_id=profissional_id, 
            data=data
        ).all()
        
        # Marca horários ocupados
        for ag in agendamentos:
            if ag.status not in ['Cancelado', 'Falta']:
                horarios_ocupados.append(ag.hora)
        
        # Gera horários disponíveis
        for hora in range(8, 18):
            for minuto in [0, 30]:
                horario = f"{hora:02d}:{minuto:02d}"
                
                # Verifica se o horário está disponível
                if horario not in horarios_ocupados:
                    horarios_disponiveis.append(horario)
        
        return jsonify({
            'success': True, 
            'horarios_disponiveis': horarios_disponiveis,
            'duracao_servico': duracao
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao buscar horários: {str(e)}'})

# API para agendamentos recorrentes
@app.route('/api/agendamentos-recorrentes', methods=['POST'])
@require_login(role=['admin','recepcao'])
def api_agendamentos_recorrentes():
    try:
        data = request.get_json()
        
        # Validações
        if not all([data.get('paciente_id'), data.get('profissional_id'), 
                   data.get('servico_id'), data.get('data_inicio'), data.get('hora')]):
            return jsonify({'success': False, 'message': 'Dados incompletos'})
        
        frequencia = data.get('frequencia', 'weekly')
        quantidade = data.get('quantidade', 4)
        dia_semana = data.get('dia_semana')
        
        agendamentos_criados = []
        data_atual = datetime.strptime(data['data_inicio'], '%Y-%m-%d')
        
        for i in range(quantidade):
            # Verifica conflito
            if conflito(data['profissional_id'], data_atual.strftime('%Y-%m-%d'), 
                       data['hora'], int(data.get('duracao_min', 30))):
                continue
            
            # Cria agendamento
            agendamento = Agendamento(
                paciente_id=data['paciente_id'],
                profissional_id=data['profissional_id'],
                servico_id=data['servico_id'],
                data=data_atual.strftime('%Y-%m-%d'),
                hora=data['hora'],
                duracao=int(data.get('duracao_min', 30)),
                status='Agendado',
                origem=data.get('origem', 'online'),
                valor_pago=float(data.get('valor_pago', 0)),
                observacoes=data.get('observacoes', '') + f' (Recorrente {i+1}/{quantidade})'
            )
            
            db.session.add(agendamento)
            agendamentos_criados.append(agendamento)
            
            # Calcula próxima data
            if frequencia == 'weekly':
                data_atual += timedelta(days=7)
            elif frequencia == 'biweekly':
                data_atual += timedelta(days=14)
            elif frequencia == 'monthly':
                # Adiciona um mês
                if data_atual.month == 12:
                    data_atual = data_atual.replace(year=data_atual.year + 1, month=1)
                else:
                    data_atual = data_atual.replace(month=data_atual.month + 1)
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'{len(agendamentos_criados)} agendamentos recorrentes criados',
            'quantidade_criada': len(agendamentos_criados)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao criar agendamentos recorrentes: {str(e)}'})

# API para estatísticas da agenda
@app.route('/api/agenda/stats')
@require_login(role=['admin','recepcao','profissional'])
def api_agenda_stats():
    try:
        data = request.args.get('data')
        profissional_id = request.args.get('profissional_id')
        
        # Query base
        query = Agendamento.query
        
        if data:
            query = query.filter_by(data=data)
        
        if profissional_id and session.get('role') == 'profissional':
            query = query.filter_by(profissional_id=profissional_id)
        
        # Estatísticas
        total = query.count()
        agendados = query.filter_by(status='Agendado').count()
        confirmados = query.filter_by(status='Confirmado').count()
        realizados = query.filter_by(status='Realizado').count()
        cancelados = query.filter_by(status='Cancelado').count()
        faltas = query.filter_by(status='Falta').count()
        
        # Receita total
        receita_total = db.session.query(db.func.sum(Agendamento.valor_pago)).filter(
            Agendamento.status.in_(['Realizado', 'Confirmado'])
        ).scalar() or 0
        
        # Receita do dia
        if data:
            receita_dia = db.session.query(db.func.sum(Agendamento.valor_pago)).filter(
                Agendamento.data == data,
                Agendamento.status.in_(['Realizado', 'Confirmado'])
            ).scalar() or 0
        else:
            receita_dia = 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total,
                'agendados': agendados,
                'confirmados': confirmados,
                'realizados': realizados,
                'cancelados': cancelados,
                'faltas': faltas,
                'receita_total': float(receita_total),
                'receita_dia': float(receita_dia)
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao buscar estatísticas: {str(e)}'})

# API para busca de pacientes
@app.route('/api/pacientes/buscar')
@require_login(role=['admin','recepcao','profissional'])
def api_buscar_pacientes():
    try:
        termo = request.args.get('q', '')
        limite = min(int(request.args.get('limit', 10)), 50)
        
        if not termo or len(termo) < 2:
            return jsonify({'success': True, 'pacientes': []})
        
        # Busca por nome, telefone ou CPF
        pacientes = Paciente.query.filter(
            db.or_(
                Paciente.nome.ilike(f'%{termo}%'),
                Paciente.telefone.ilike(f'%{termo}%'),
                Paciente.cpf.ilike(f'%{termo}%')
            )
        ).limit(limite).all()
        
        resultado = []
        for p in pacientes:
            resultado.append({
                'id': p.id,
                'nome': p.nome,
                'telefone': p.telefone,
                'cpf': p.cpf,
                'email': p.email
            })
        
        return jsonify({'success': True, 'pacientes': resultado})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro na busca: {str(e)}'})

# Exportar dados
@app.route('/exportar')
@require_login(role=['admin','recepcao'])
def exportar_dados():
    formato = request.args.get('formato', 'csv')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')
    
    # Query dos agendamentos
    query = Agendamento.query
    if inicio:
        query = query.filter(Agendamento.data >= inicio)
    if fim:
        query = query.filter(Agendamento.data <= fim)
    
    agendamentos = query.order_by(Agendamento.data.desc(), Agendamento.hora.desc()).all()
    
    if formato == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        writer.writerow(['Data', 'Hora', 'Paciente', 'Profissional', 'Serviço', 'Status', 'Valor', 'Observações'])
        
        # Dados
        for ag in agendamentos:
            writer.writerow([
                ag.data, ag.hora, ag.paciente.nome, ag.profissional.nome,
                ag.servico.nome, ag.status, ag.valor_pago, ag.observacoes or ''
            ])
        
        output.seek(0)
        # Usar UTF-8 com BOM para compatibilidade com Excel
        csv_bytes = output.getvalue().encode('utf-8-sig')
        return send_file(
            io.BytesIO(csv_bytes),
            mimetype='text/csv; charset=utf-8',
            as_attachment=True,
            download_name=f'agendamentos_{inicio}_{fim}.csv'
        )
    
    elif formato == 'pdf':
        try:
            # Gerar PDF simples usando HTML
            import tempfile
            
            # Criar HTML para o PDF com codificação UTF-8 explícita
            html_content = f"""
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                <title>Relatório de Agendamentos</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #0d6efd; text-align: center; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f8f9fa; font-weight: bold; }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>📊 Relatório de Agendamentos</h1>
                    <p><strong>Período:</strong> {inicio or 'Todos'} - {fim or 'Todos'}</p>
                    <p><strong>Total de Registros:</strong> {len(agendamentos)}</p>
                    <p><strong>Data de Geração:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>Data</th>
                            <th>Hora</th>
                            <th>Paciente</th>
                            <th>Profissional</th>
                            <th>Serviço</th>
                            <th>Status</th>
                            <th>Valor</th>
                            <th>Observações</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            # Adicionar dados com tratamento de caracteres especiais
            for ag in agendamentos:
                # Tratar caracteres especiais nos nomes
                paciente_nome = (ag.paciente.nome if ag.paciente else '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                profissional_nome = (ag.profissional.nome if ag.profissional else '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                servico_nome = (ag.servico.nome if ag.servico else '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                observacoes = (ag.observacoes or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                
                html_content += f"""
                        <tr>
                            <td>{ag.data or ''}</td>
                            <td>{ag.hora or ''}</td>
                            <td>{paciente_nome}</td>
                            <td>{profissional_nome}</td>
                            <td>{servico_nome}</td>
                            <td>{ag.status or ''}</td>
                            <td>R$ {ag.valor_pago or 0:.2f}</td>
                            <td>{observacoes}</td>
                        </tr>
                """
            
            html_content += """
                    </tbody>
                </table>
                
                <div class="footer">
                    <p>Sistema Clínica - Relatório gerado automaticamente</p>
                </div>
            </body>
            </html>
            """
            
            # Retornar HTML para download com codificação UTF-8 explícita
            html_bytes = html_content.encode('utf-8-sig')  # UTF-8 com BOM para compatibilidade
            return send_file(
                io.BytesIO(html_bytes),
                mimetype='text/html; charset=utf-8',
                as_attachment=True,
                download_name=f'relatorio_agendamentos_{inicio}_{fim}.html'
            )
                    
        except Exception as e:
            print(f"Erro ao gerar relatório: {e}")
            flash("Erro ao gerar relatório. Tente exportar como CSV.", "error")
            return redirect(url_for('relatorios'))
    
    else:
        flash("Formato de exportação não suportado. Use 'csv' ou 'pdf'.", "warning")
        return redirect(url_for('relatorios'))

# ---------------- CONFIGURAÇÕES DO SISTEMA ----------------
# Rota removida - duplicada com a rota principal de configurações

@app.route('/api/configuracoes', methods=['GET'])
@require_login()
def api_configuracoes():
    """Retorna todas as configurações do sistema"""
    try:
        # Aqui você pode carregar configurações do banco ou arquivo
        config = {
            'geral': {
                'modo': 'desenvolvimento',
                'idioma': 'pt-br',
                'fusoHorario': 'America/Sao_Paulo',
                'formatoData': 'dd/mm/yyyy',
                'tema': 'auto',
                'tamanhoFonte': 'medium',
                'tempoSessao': 8,
                'nivelLog': 'warning'
            },
            'clinica': {
                'nome': 'Clínica Saúde Total',
                'cnpj': '',
                'telefone': '+55 11 99999-9999',
                'email': '',
                'endereco': 'Rua das Clínicas, 123 - Centro',
                'cidade': 'São Paulo',
                'estado': 'SP',
                'cep': '',
                'horarioAbertura': '08:00',
                'horarioFechamento': '18:00',
                'diasFuncionamento': ['segunda', 'terca', 'quarta', 'quinta', 'sexta']
            },
            'backup': {
                'frequencia': 'diario',
                'horario': '02:00',
                'retencao': 30,
                'compressao': True,
                'backupNuvem': False,
                'notificacao': True
            }
        }
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/configuracoes/geral', methods=['POST'])
@require_login()
def api_configuracoes_geral():
    """Salva configurações gerais do sistema"""
    try:
        data = request.get_json()
        # Aqui você pode salvar no banco ou arquivo
        # Por enquanto, apenas retorna sucesso
        return jsonify({'message': 'Configurações gerais salvas com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/configuracoes/clinica', methods=['POST'])
@require_login()
def api_configuracoes_clinica():
    """Salva dados da clínica"""
    try:
        data = request.get_json()
        # Aqui você pode salvar no banco ou arquivo
        # Por enquanto, apenas retorna sucesso
        return jsonify({'message': 'Dados da clínica salvos com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/configuracoes/backup', methods=['POST'])
@require_login()
def api_configuracoes_backup():
    """Salva configurações de backup"""
    try:
        data = request.get_json()
        # Aqui você pode salvar no banco ou arquivo
        # Por enquanto, apenas retorna sucesso
        return jsonify({'message': 'Configurações de backup salvas com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------------- SISTEMA DE BACKUP ----------------
@app.route('/api/backup/executar', methods=['POST'])
@require_login()
def api_backup_executar():
    """Executa backup manual do sistema"""
    try:
        import shutil
        import os
        from datetime import datetime
        
        # Criar diretório de backup se não existir
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        # Nome do arquivo de backup com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'clinica_backup_{timestamp}.db'
        backup_path = os.path.join(backup_dir, backup_file)
        
        # Copiar banco de dados
        source_db = 'instance/clinica.db'
        if os.path.exists(source_db):
            shutil.copy2(source_db, backup_path)
            
            # Limpar backups antigos (manter apenas os últimos 10)
            backup_files = [f for f in os.listdir(backup_dir) if f.startswith('clinica_backup_')]
            backup_files.sort(reverse=True)
            
            if len(backup_files) > 10:
                for old_backup in backup_files[10:]:
                    os.remove(os.path.join(backup_dir, old_backup))
            
            return jsonify({
                'message': 'Backup executado com sucesso',
                'backup_file': backup_file,
                'timestamp': timestamp
            })
        else:
            return jsonify({'error': 'Banco de dados não encontrado'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/backup/historico')
@require_login()
def api_backup_historico():
    """Retorna histórico de backups"""
    try:
        import os
        from datetime import datetime
        
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            return jsonify([])
        
        backup_files = []
        for filename in os.listdir(backup_dir):
            if filename.startswith('clinica_backup_') and filename.endswith('.db'):
                file_path = os.path.join(backup_dir, filename)
                file_stat = os.stat(file_path)
                
                # Extrair timestamp do nome do arquivo
                timestamp_str = filename.replace('clinica_backup_', '').replace('.db', '')
                try:
                    timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                except:
                    timestamp = datetime.fromtimestamp(file_stat.st_mtime)
                
                backup_files.append({
                    'id': filename,
                    'nome': filename,
                    'tamanho': file_stat.st_size,
                    'data_criacao': timestamp.isoformat(),
                    'tamanho_mb': round(file_stat.st_size / (1024 * 1024), 2)
                })
        
        # Ordenar por data de criação (mais recente primeiro)
        backup_files.sort(key=lambda x: x['data_criacao'], reverse=True)
        
        return jsonify(backup_files)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/backup/restaurar/<backup_id>', methods=['POST'])
@require_login()
def api_backup_restaurar(backup_id):
    """Restaura backup específico"""
    try:
        import shutil
        import os
        
        backup_dir = 'backups'
        backup_path = os.path.join(backup_dir, backup_id)
        
        if not os.path.exists(backup_path):
            return jsonify({'error': 'Backup não encontrado'}), 404
        
        # Criar backup do banco atual antes de restaurar
        current_db = 'instance/clinica.db'
        if os.path.exists(current_db):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safety_backup = f'clinica_safety_{timestamp}.db'
            shutil.copy2(current_db, os.path.join(backup_dir, safety_backup))
        
        # Restaurar backup
        shutil.copy2(backup_path, current_db)
        
        return jsonify({'message': 'Backup restaurado com sucesso'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------------- ROTAS DE SISTEMA ----------------
@app.route('/api/sistema/verificar')
@require_login()
def api_sistema_verificar():
    """Verifica o status do sistema"""
    try:
        # Verificar banco de dados
        db_status = "OK"
        try:
            db.session.execute("SELECT 1")
        except Exception as e:
            db_status = f"ERRO: {str(e)}"
        
        # Verificar arquivos do sistema
        file_status = "OK"
        try:
            required_files = ['instance/clinica.db', 'config.py']
            for file_path in required_files:
                if not os.path.exists(file_path):
                    file_status = f"ERRO: {file_path} não encontrado"
                    break
        except Exception as e:
            file_status = f"ERRO: {str(e)}"
        
        # Verificar permissões
        permission_status = "OK"
        try:
            if not os.access('instance', os.W_OK):
                permission_status = "ERRO: Sem permissão de escrita em instance/"
        except Exception as e:
            permission_status = f"ERRO: {str(e)}"
        
        return jsonify({
            'status': 'OK',
            'timestamp': datetime.now().isoformat(),
            'database': db_status,
            'files': file_status,
            'permissions': permission_status
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sistema/limpar-cache')
@require_login()
def api_sistema_limpar_cache():
    """Limpa o cache do sistema"""
    try:
        # Limpar cache de sessão
        session.clear()
        
        # Limpar variáveis globais
        if hasattr(g, 'menu_items'):
            g.menu_items = []
        
        # Limpar cache de configurações
        if hasattr(app, 'config_cache'):
            delattr(app, 'config_cache')
        
        return jsonify({
            'message': 'Cache limpo com sucesso',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sistema/relatorio')
@require_login()
def api_sistema_relatorio():
    """Gera relatório do sistema em PDF"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from io import BytesIO
        import platform
        import sys
        
        # Criar buffer para o PDF
        buffer = BytesIO()
        
        # Criar documento PDF
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,  # Centralizado
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkgreen
        )
        
        normal_style = styles['Normal']
        
        # Título principal
        story.append(Paragraph("RELATÓRIO DO SISTEMA", title_style))
        story.append(Spacer(1, 20))
        
        # Informações básicas
        story.append(Paragraph("Informações Gerais", heading_style))
        story.append(Paragraph(f"<b>Data/Hora de Geração:</b> {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}", normal_style))
        
        # Capturar informações do usuário logado
        user_nome = session.get('user_nome', 'Sistema')
        user_role = session.get('user_role', 'Administrador')
        user_id = session.get('user_id', 'N/A')
        
        story.append(Paragraph(f"<b>Usuário:</b> {user_nome}", normal_style))
        story.append(Paragraph(f"<b>Função:</b> {user_role}", normal_style))
        story.append(Paragraph(f"<b>ID do Usuário:</b> {user_id}", normal_style))
        story.append(Spacer(1, 12))
        
        # Estatísticas do banco de dados
        story.append(Paragraph("Estatísticas do Banco de Dados", heading_style))
        
        try:
            # Contar registros em cada tabela
            tables = ['usuario', 'paciente', 'profissional', 'servico', 'agendamento']
            table_names = ['Usuários', 'Pacientes', 'Profissionais', 'Serviços', 'Agendamentos']
            table_data = [['Tabela', 'Registros']]
            
            for i, table in enumerate(tables):
                try:
                    # Verificar se a tabela existe primeiro
                    table_exists = db.session.execute(db.text("SELECT name FROM sqlite_master WHERE type='table' AND name=:table"), {"table": table}).fetchone()
                    if table_exists:
                        count = db.session.execute(db.text(f"SELECT COUNT(*) FROM {table}")).scalar()
                        table_data.append([table_names[i], str(count)])
                    else:
                        table_data.append([table_names[i], 'Tabela não existe'])
                except Exception as e:
                    table_data.append([table_names[i], f'Erro: {str(e)}'])
            
            # Criar tabela
            table = Table(table_data, colWidths=[2*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
            
        except Exception as e:
            story.append(Paragraph(f"Erro ao acessar banco de dados: {str(e)}", normal_style))
            story.append(Spacer(1, 12))
        
        # Estatísticas de agendamentos
        story.append(Paragraph("Estatísticas de Agendamentos", heading_style))
        
        try:
            # Verificar se a coluna status existe na tabela agendamento
            agendamento_columns = db.session.execute(db.text("PRAGMA table_info(agendamento)")).fetchall()
            agendamento_col_names = [col[1] for col in agendamento_columns]
            
            if 'status' in agendamento_col_names:
                # Agendamentos por status (usando valores reais da tabela)
                agendamentos_pendentes = db.session.execute(db.text("SELECT COUNT(*) FROM agendamento WHERE status = 'Agendado'")).scalar()
                agendamentos_confirmados = db.session.execute(db.text("SELECT COUNT(*) FROM agendamento WHERE status = 'Confirmado'")).scalar()
                agendamentos_cancelados = db.session.execute(db.text("SELECT COUNT(*) FROM agendamento WHERE status = 'Cancelado'")).scalar()
                agendamentos_realizados = db.session.execute(db.text("SELECT COUNT(*) FROM agendamento WHERE status = 'Realizado'")).scalar()
                
                # Se algum status não retornar resultados, mostrar total
                if agendamentos_pendentes == 0 and agendamentos_confirmados == 0 and agendamentos_cancelados == 0 and agendamentos_realizados == 0:
                    # Tentar descobrir quais status existem
                    cursor = db.session.execute(db.text("SELECT DISTINCT status FROM agendamento"))
                    existing_statuses = [row[0] for row in cursor.fetchall()]
                    print(f"Status encontrados: {existing_statuses}")
                    
                    # Mostrar total e status disponíveis
                    total_agendamentos = db.session.execute(db.text("SELECT COUNT(*) FROM agendamento")).scalar()
                    agendamentos_pendentes = f"Total: {total_agendamentos}"
                    agendamentos_confirmados = f"Status: {', '.join(existing_statuses)}"
                    agendamentos_cancelados = 'N/A'
                    agendamentos_realizados = 'N/A'
            else:
                # Se não existir coluna status, mostrar total de agendamentos
                total_agendamentos = db.session.execute(db.text("SELECT COUNT(*) FROM agendamento")).scalar()
                agendamentos_pendentes = total_agendamentos
                agendamentos_confirmados = 'N/A'
                agendamentos_cancelados = 'N/A'
                agendamentos_realizados = 'N/A'
            
            agendamentos_data = [
                ['Status', 'Quantidade'],
                ['Pendentes', str(agendamentos_pendentes)],
                ['Confirmados', str(agendamentos_confirmados)],
                ['Cancelados', str(agendamentos_cancelados)],
                ['Realizados', str(agendamentos_realizados)]
            ]
            
            agendamentos_table = Table(agendamentos_data, colWidths=[2*inch, 1*inch])
            agendamentos_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(agendamentos_table)
            story.append(Spacer(1, 20))
            
        except Exception as e:
            story.append(Paragraph(f"Erro ao obter estatísticas de agendamentos: {str(e)}", normal_style))
            story.append(Spacer(1, 12))
        
        # Informações do sistema da clínica
        story.append(Paragraph("Informações do Sistema da Clínica", heading_style))
        
        # Obter informações específicas da clínica
        try:
            # Verificar estrutura da tabela usuario primeiro
            try:
                # Verificar se a coluna role existe
                role_exists = db.session.execute(db.text("PRAGMA table_info(usuario)")).fetchall()
                role_columns = [col[1] for col in role_exists]
                
                if 'role' in role_columns:
                    # Contar usuários por tipo
                    admin_count = db.session.execute(db.text("SELECT COUNT(*) FROM usuario WHERE role = 'admin'")).scalar()
                    recepcao_count = db.session.execute(db.text("SELECT COUNT(*) FROM usuario WHERE role = 'recepcao'")).scalar()
                    profissional_count = db.session.execute(db.text("SELECT COUNT(*) FROM usuario WHERE role = 'profissional'")).scalar()
                else:
                    # Se não existir coluna role, contar total de usuários
                    total_users = db.session.execute(db.text("SELECT COUNT(*) FROM usuario")).scalar()
                    admin_count = total_users
                    recepcao_count = 'N/A'
                    profissional_count = 'N/A'
                    
            except Exception as e:
                admin_count = recepcao_count = profissional_count = 'Erro'
            
            # Contar agendamentos por status (com verificação de coluna)
            try:
                agendamento_columns = db.session.execute(db.text("PRAGMA table_info(agendamento)")).fetchall()
                agendamento_col_names = [col[1] for col in agendamento_columns]
                
                if 'data' in agendamento_col_names and 'hora' in agendamento_col_names:
                    # Usar as colunas data e hora separadas
                    agendamentos_hoje = db.session.execute(db.text("SELECT COUNT(*) FROM agendamento WHERE data = DATE('now')")).scalar()
                    agendamentos_semana = db.session.execute(db.text("SELECT COUNT(*) FROM agendamento WHERE data >= DATE('now', '-7 days')")).scalar()
                    pacientes_ativos = db.session.execute(db.text("SELECT COUNT(DISTINCT paciente_id) FROM agendamento WHERE data >= DATE('now', '-30 days')")).scalar()
                elif 'data_hora' in agendamento_col_names:
                    # Fallback para coluna data_hora se existir
                    agendamentos_hoje = db.session.execute(db.text("SELECT COUNT(*) FROM agendamento WHERE DATE(data_hora) = DATE('now')")).scalar()
                    agendamentos_semana = db.session.execute(db.text("SELECT COUNT(*) FROM agendamento WHERE data_hora >= datetime('now', '-7 days')")).scalar()
                    pacientes_ativos = db.session.execute(db.text("SELECT COUNT(DISTINCT paciente_id) FROM agendamento WHERE data_hora >= datetime('now', '-30 days')")).scalar()
                else:
                    agendamentos_hoje = agendamentos_semana = pacientes_ativos = 'Colunas de data não encontradas'
                    
            except Exception as e:
                agendamentos_hoje = agendamentos_semana = pacientes_ativos = 'Erro'
            
        except Exception as e:
            admin_count = recepcao_count = profissional_count = agendamentos_hoje = agendamentos_semana = pacientes_ativos = 'Erro'
        
        system_info = [
            ['Componente', 'Detalhes'],
            ['Nome do Sistema', 'Sistema de Gestão Clínica - Sistema 04'],
            ['Versão', '2.0.0'],
            ['Data de Geração', datetime.now().strftime('%d/%m/%Y %H:%M:%S')],
            ['Usuários Administradores', str(admin_count)],
            ['Usuários Recepção', str(recepcao_count)],
            ['Profissionais de Saúde', str(profissional_count)],
            ['Agendamentos Hoje', str(agendamentos_hoje)],
            ['Agendamentos Última Semana', str(agendamentos_semana)],
            ['Pacientes Ativos (30 dias)', str(pacientes_ativos)]
        ]
        
        system_table = Table(system_info, colWidths=[2*inch, 3*inch])
        system_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(system_table)
        story.append(Spacer(1, 20))
        
        # Status do sistema
        story.append(Paragraph("Status do Sistema", heading_style))
        
        # Verificar status do banco
        db_status = "OK"
        try:
            db.session.execute("SELECT 1")
        except Exception as e:
            db_status = f"ERRO: {str(e)}"
        
        # Verificar arquivos do sistema
        file_status = "OK"
        try:
            required_files = ['instance/clinica.db', 'config.py']
            for file_path in required_files:
                if not os.path.exists(file_path):
                    file_status = f"ERRO: {file_path} não encontrado"
                    break
        except Exception as e:
            file_status = f"ERRO: {str(e)}"
        
        status_data = [
            ['Componente', 'Status'],
            ['Banco de Dados', db_status],
            ['Arquivos do Sistema', file_status],
            ['Sessão do Usuário', 'Ativa' if session.get('user_id') else 'Inativa']
        ]
        
        status_table = Table(status_data, colWidths=[2*inch, 3*inch])
        status_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(status_table)
        
        # Construir PDF
        doc.build(story)
        
        # Voltar ao início do buffer
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'relatorio-sistema-{datetime.now().strftime("%Y%m%d-%H%M%S")}.pdf'
        )
        
    except ImportError:
        # Fallback para CSV se reportlab não estiver disponível
        try:
            from io import BytesIO
            import csv
            
            output = BytesIO()
            writer = csv.writer(output)
            
            # Cabeçalho
            writer.writerow(['Relatório do Sistema', 'Data/Hora'])
            writer.writerow(['', datetime.now().strftime('%d/%m/%Y %H:%M:%S')])
            writer.writerow([])
            
            # Estatísticas do banco
            writer.writerow(['ESTATÍSTICAS DO BANCO DE DADOS'])
            writer.writerow(['Tabela', 'Registros'])
            
            try:
                tables = ['usuario', 'paciente', 'profissional', 'servico', 'agendamento']
                table_names = ['Usuários', 'Pacientes', 'Profissionais', 'Serviços', 'Agendamentos']
                for i, table in enumerate(tables):
                    try:
                        # Verificar se a tabela existe primeiro
                        table_exists = db.session.execute(db.text("SELECT name FROM sqlite_master WHERE type='table' AND name=:table"), {"table": table}).fetchone()
                        if table_exists:
                            count = db.session.execute(db.text(f"SELECT COUNT(*) FROM {table}")).scalar()
                            writer.writerow([table_names[i], count])
                        else:
                            writer.writerow([table_names[i], 'Tabela não existe'])
                    except Exception as e:
                        writer.writerow([table_names[i], f'Erro: {str(e)}'])
            except Exception as e:
                writer.writerow(['', f'Erro ao acessar banco: {str(e)}'])
            
            writer.writerow([])
            
            # Informações do sistema da clínica
            writer.writerow(['INFORMAÇÕES DO SISTEMA DA CLÍNICA'])
            writer.writerow(['Nome do Sistema', 'Sistema de Gestão Clínica - Sistema 04'])
            writer.writerow(['Versão', '2.0.0'])
            writer.writerow(['Data de Geração', datetime.now().strftime('%d/%m/%Y %H:%M:%S')])
            
            # Estatísticas específicas da clínica
            try:
                # Verificar estrutura da tabela usuario primeiro
                try:
                    role_exists = db.session.execute(db.text("PRAGMA table_info(usuario)")).fetchall()
                    role_columns = [col[1] for col in role_exists]
                    
                    if 'role' in role_columns:
                        # Contar usuários por tipo
                        admin_count = db.session.execute(db.text("SELECT COUNT(*) FROM usuario WHERE role = 'admin'")).scalar()
                        recepcao_count = db.session.execute(db.text("SELECT COUNT(*) FROM usuario WHERE role = 'recepcao'")).scalar()
                        profissional_count = db.session.execute(db.text("SELECT COUNT(*) FROM usuario WHERE role = 'profissional'")).scalar()
                    else:
                        # Se não existir coluna role, contar total de usuários
                        total_users = db.session.execute(db.text("SELECT COUNT(*) FROM usuario")).scalar()
                        admin_count = total_users
                        recepcao_count = 'N/A'
                        profissional_count = 'N/A'
                        
                except Exception as e:
                    admin_count = recepcao_count = profissional_count = 'Erro'
                
                # Verificar estrutura da tabela agendamento
                try:
                    agendamento_columns = db.session.execute(db.text("PRAGMA table_info(agendamento)")).fetchall()
                    agendamento_col_names = [col[1] for col in agendamento_columns]
                    
                    if 'data' in agendamento_col_names and 'hora' in agendamento_col_names:
                        # Usar as colunas data e hora separadas
                        agendamentos_hoje = db.session.execute(db.text("SELECT COUNT(*) FROM agendamento WHERE data = DATE('now')")).scalar()
                        agendamentos_semana = db.session.execute(db.text("SELECT COUNT(*) FROM agendamento WHERE data >= DATE('now', '-7 days')")).scalar()
                        pacientes_ativos = db.session.execute(db.text("SELECT COUNT(DISTINCT paciente_id) FROM agendamento WHERE data >= DATE('now', '-30 days')")).scalar()
                    elif 'data_hora' in agendamento_col_names:
                        # Fallback para coluna data_hora se existir
                        agendamentos_hoje = db.session.execute(db.text("SELECT COUNT(*) FROM agendamento WHERE DATE(data_hora) = DATE('now')")).scalar()
                        agendamentos_semana = db.session.execute(db.text("SELECT COUNT(*) FROM agendamento WHERE data_hora >= datetime('now', '-7 days')")).scalar()
                        pacientes_ativos = db.session.execute(db.text("SELECT COUNT(DISTINCT paciente_id) FROM agendamento WHERE data_hora >= datetime('now', '-30 days')")).scalar()
                    else:
                        agendamentos_hoje = agendamentos_semana = pacientes_ativos = 'Colunas de data não encontradas'
                        
                except Exception as e:
                    agendamentos_hoje = agendamentos_semana = pacientes_ativos = 'Erro'
                
                writer.writerow(['Usuários Administradores', admin_count])
                writer.writerow(['Usuários Recepção', recepcao_count])
                writer.writerow(['Profissionais de Saúde', profissional_count])
                writer.writerow(['Agendamentos Hoje', agendamentos_hoje])
                writer.writerow(['Agendamentos Última Semana', agendamentos_semana])
                writer.writerow(['Pacientes Ativos (30 dias)', pacientes_ativos])
                
            except Exception as e:
                writer.writerow(['', f'Erro ao obter estatísticas: {str(e)}'])
            
            output.seek(0)
            
            return send_file(
                output,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'relatorio-sistema-{datetime.now().strftime("%Y%m%d-%H%M%S")}.csv'
            )
            
        except Exception as e:
            return jsonify({'error': f'Erro ao gerar relatório: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar relatório PDF: {str(e)}'}), 500

# ---------------- RECUPERAR SENHA ----------------
@app.route('/recuperar-senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        cpf = request.form.get('cpf')
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')
        
        # Validações básicas
        if not cpf or not nova_senha or not confirmar_senha:
            return render_template('recuperar_senha.html', title="Recuperar Senha", erro="Todos os campos são obrigatórios")
        
        # Valida CPF
        if not validar_cpf(cpf):
            return render_template('recuperar_senha.html', title="Recuperar Senha", erro="CPF inválido")
        
        # Valida senha
        if len(nova_senha) < 6:
            return render_template('recuperar_senha.html', title="Recuperar Senha", erro="A nova senha deve ter pelo menos 6 caracteres")
        
        # Valida confirmação
        if nova_senha != confirmar_senha:
            return render_template('recuperar_senha.html', title="Recuperar Senha", erro="A nova senha e a confirmação devem ser idênticas")
        
        # Limpa CPF para busca no banco
        cpf_limpo = re.sub(r'[^0-9]', '', cpf)
        
        # Busca usuário pelo CPF
        user = Usuario.query.filter_by(cpf=cpf_limpo).first()
        
        if user:
            # Atualiza senha
            user.senha = generate_password_hash(nova_senha)
            user.primeiro_acesso = False
            db.session.commit()
            
            flash("Senha alterada com sucesso! Faça login com sua nova senha.", "success")
            return redirect(url_for('login'))
        else:
            return render_template('recuperar_senha.html', title="Recuperar Senha", erro="CPF não encontrado no sistema")
    
    return render_template('recuperar_senha.html', title="Recuperar Senha")

# ---------------- SOBRE O DESENVOLVEDOR ----------------
@app.route('/sobre')
@require_login()
def sobre():
    return render_template('sobre.html', title="Sobre o Sistema")

@app.route('/api/relatorios/estatisticas')
@require_login(role=['admin'])
def api_estatisticas():
    """Retorna estatísticas atualizadas baseadas nos filtros aplicados"""
    try:
        from datetime import datetime, timedelta
        
        # Obter parâmetros dos filtros
        periodo = request.args.get('periodo', 30, type=int)
        profissional_id = request.args.get('profissional', type=int)
        servico_id = request.args.get('servico', type=int)
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        # Calcular datas baseadas no período
        hoje = datetime.now()
        if data_inicio and data_fim:
            inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
            fim = datetime.strptime(data_fim, '%Y-%m-%d')
        else:
            inicio = hoje - timedelta(days=periodo)
            fim = hoje
        
        # Query base para agendamentos
        query = Agendamento.query.filter(
            Agendamento.data >= inicio.strftime('%Y-%m-%d'),
            Agendamento.data <= fim.strftime('%Y-%m-%d')
        )
        
        # Aplicar filtros adicionais
        if profissional_id:
            query = query.filter(Agendamento.profissional_id == profissional_id)
        
        if servico_id:
            query = query.filter(Agendamento.servico_id == servico_id)
        
        # Calcular estatísticas
        agendamentos_periodo = query.count()
        
        # Agendamentos por status
        agendamentos_por_status = db.session.query(
            Agendamento.status,
            db.func.count(Agendamento.id).label('total')
        ).filter(
            Agendamento.data >= inicio.strftime('%Y-%m-%d'),
            Agendamento.data <= fim.strftime('%Y-%m-%d')
        )
        
        if profissional_id:
            agendamentos_por_status = agendamentos_por_status.filter(
                Agendamento.profissional_id == profissional_id
            )
        
        if servico_id:
            agendamentos_por_status = agendamentos_por_status.filter(
                Agendamento.servico_id == servico_id
            )
        
        agendamentos_por_status = agendamentos_por_status.group_by(Agendamento.status).all()
        
        # Calcular receita do período
        receita_periodo = db.session.query(
            db.func.sum(Agendamento.valor_pago)
        ).filter(
            Agendamento.data >= inicio.strftime('%Y-%m-%d'),
            Agendamento.data <= fim.strftime('%Y-%m-%d'),
            Agendamento.status == "Realizado",
            Agendamento.valor_pago > 0
        )
        
        if profissional_id:
            receita_periodo = receita_periodo.filter(
                Agendamento.profissional_id == profissional_id
            )
        
        if servico_id:
            receita_periodo = receita_periodo.filter(
                Agendamento.servico_id == servico_id
            )
        
        receita_periodo = receita_periodo.scalar() or 0
        
        # Calcular taxa de faltas
        faltas = query.filter(Agendamento.status == "Falta").count()
        taxa_faltas = (faltas / agendamentos_periodo * 100) if agendamentos_periodo > 0 else 0
        
        # Calcular taxa de confirmação
        confirmados = query.filter(Agendamento.status == "Confirmado").count()
        taxa_confirmacao = (confirmados / agendamentos_periodo * 100) if agendamentos_periodo > 0 else 0
        
        # Calcular taxa de realização
        realizados = query.filter(Agendamento.status == "Realizado").count()
        taxa_realizacao = (realizados / agendamentos_periodo * 100) if agendamentos_periodo > 0 else 0
        
        # Estatísticas por profissional (se não filtrado por profissional)
        if not profissional_id:
            stats_profissionais = db.session.query(
                Profissional.nome,
                db.func.count(Agendamento.id).label('total'),
                db.func.sum(db.case((Agendamento.status == "Realizado", 1), else_=0)).label('realizados'),
                db.func.sum(db.case((Agendamento.status == "Falta", 1), else_=0)).label('faltas')
            ).join(Agendamento).filter(
                Agendamento.data >= inicio.strftime('%Y-%m-%d'),
                Agendamento.data <= fim.strftime('%Y-%m-%d')
            )
            
            if servico_id:
                stats_profissionais = stats_profissionais.filter(
                    Agendamento.servico_id == servico_id
                )
            
            stats_profissionais = stats_profissionais.group_by(
                Profissional.id, Profissional.nome
            ).order_by(
                db.func.count(Agendamento.id).desc()
            ).limit(5).all()
        else:
            stats_profissionais = []
        
        return jsonify({
            'success': True,
            'estatisticas': {
                'agendamentos_periodo': agendamentos_periodo,
                'receita_periodo': float(receita_periodo),
                'taxa_faltas': round(taxa_faltas, 1),
                'taxa_confirmacao': round(taxa_confirmacao, 1),
                'taxa_realizacao': round(taxa_realizacao, 1),
                'faltas': faltas,
                'confirmados': confirmados,
                'realizados': realizados,
                'periodo_dias': periodo,
                'data_inicio': inicio.strftime('%Y-%m-%d'),
                'data_fim': fim.strftime('%Y-%m-%d')
            },
            'agendamentos_por_status': [
                {'status': item.status, 'total': item.total}
                for item in agendamentos_por_status
            ],
            'stats_profissionais': [
                {
                    'nome': item.nome,
                    'total': item.total,
                    'realizados': item.realizados or 0,
                    'faltas': item.faltas or 0
                }
                for item in stats_profissionais
            ]
        })
        
    except Exception as e:
        print(f"Erro ao calcular estatísticas: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/relatorios/filtros')
@require_login(role=['admin'])
def api_filtros():
    """Retorna dados para popular os filtros"""
    try:
        # Buscar profissionais
        profissionais = db.session.query(
            Profissional.id,
            Profissional.nome
        ).order_by(Profissional.nome).all()
        
        # Buscar serviços
        servicos = db.session.query(
            Servico.id,
            Servico.nome
        ).order_by(Servico.nome).all()
        
        return jsonify({
            'success': True,
            'profissionais': [
                {'id': p.id, 'nome': p.nome}
                for p in profissionais
            ],
            'servicos': [
                {'id': s.id, 'nome': s.nome}
                for s in servicos
            ]
        })
        
    except Exception as e:
        print(f"Erro ao buscar filtros: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080)
