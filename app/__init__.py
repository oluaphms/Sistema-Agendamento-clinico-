"""
Aplicação principal Flask - Sistema Clínica
Versão Modernizada - Fase 1: Interface e PWA
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
# from flask_caching import Cache
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address
# from flask_talisman import Talisman
# from flask_compress import Compress
import os

# Inicialização de extensões
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
# cache = Cache()
# limiter = Limiter(key_func=get_remote_address)
# talisman = Talisman()
# compress = Compress()

def create_app(config_name=None):
    """Factory pattern para criar a aplicação Flask"""
    
    # Cria a aplicação Flask
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # Configura a aplicação
    if config_name is None:
        from config import get_config
        config_name = get_config()
    else:
        from config import config
        config_name = config[config_name]
    
    app.config.from_object(config_name)
    
    # Inicializa extensões
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    # cache.init_app(app)
    # limiter.init_app(app)
    # talisman.init_app(app)
    # compress.init_app(app)
    
    # Configura o login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    # Configura o Talisman (segurança)
    # if app.config.get('DEBUG'):
    #     talisman.content_security_policy = None
    
    # Registra blueprints
    register_blueprints(app)
    
    # Configura handlers de erro
    register_error_handlers(app)
    
    # Configura context processors
    register_context_processors(app)
    
    # Configura before_request para menu
    register_before_request(app)
    
    # Cria diretórios necessários
    create_directories(app)
    
    # Inicializa o banco de dados
    with app.app_context():
        db.create_all()
        create_default_admin(app)
    
    return app

def register_blueprints(app):
    """Registra os blueprints da aplicação"""
    
    # Importa blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.patients import patients_bp
    from app.routes.professionals import professionals_bp
    from app.routes.appointments import appointments_bp
    from app.routes.reports import reports_bp
    
    # Registra blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(patients_bp, url_prefix='/patients')
    app.register_blueprint(professionals_bp, url_prefix='/professionals')
    app.register_blueprint(appointments_bp, url_prefix='/appointments')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    
    # Rota raiz
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

def register_error_handlers(app):
    """Registra handlers de erro"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

def register_context_processors(app):
    """Registra context processors globais"""
    
    @app.context_processor
    def inject_config():
        """Injeta configurações no template"""
        return {
            'app_name': app.config.get('PWA_NAME', 'Sistema Clínica'),
            'app_version': '1.0.0 - Fase 1',
            'current_year': datetime.now().year
        }
    
    @app.context_processor
    def inject_user():
        """Injeta informações do usuário no template"""
        from flask_login import current_user
        return {'current_user': current_user}

def register_before_request(app):
    """Registra before_request para construir itens do menu"""
    
    @app.before_request
    def build_menu_items():
        from flask import g, session
        from app.menu_config import MENU_ITEMS, ROLE_PERMISSIONS
        
        role = session.get("role", "recepcao")  # fallback conservador
        allowed = ROLE_PERMISSIONS.get(role, set())
        items = [i for i in MENU_ITEMS if i["key"] in allowed]
        
        # Fallback para evitar lista vazia:
        if not items:
            items = [i for i in MENU_ITEMS if i["key"] in {"dashboard","logout"}]
        
        # Garantir que todos os valores são serializáveis e não são None/Undefined
        safe_items = []
        for item in items:
            safe_item = {}
            for key, value in item.items():
                if value is None:
                    safe_item[key] = ""
                elif not isinstance(value, (str, int, float, bool)):
                    safe_item[key] = str(value)
                else:
                    safe_item[key] = value
            safe_items.append(safe_item)
        
        g.menu_items = safe_items
        
        # Log para diagnóstico
        import logging
        logging.getLogger().info("MENU_ITEMS_RESOLVED: role=%s items=%s", role, [i["key"] for i in safe_items])

def create_directories(app):
    """Cria diretórios necessários"""
    
    directories = [
        app.config.get('UPLOAD_FOLDER'),
        'app/static/icons',
        'app/static/images',
        'logs'
    ]
    
    for directory in directories:
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

def create_default_admin(app):
    """Cria usuário admin padrão se não existir"""
    
    from app.models.user import User
    from werkzeug.security import generate_password_hash
    
    # Verifica se já existe um admin
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@clinica.com',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Usuário admin criado com sucesso!")

# Importações necessárias
from flask import redirect, url_for, render_template
from datetime import datetime
