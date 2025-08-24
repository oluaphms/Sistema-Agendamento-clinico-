"""
Modelo de Usuário - Sistema Clínica
Versão Modernizada - Fase 1
"""

from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

class User(UserMixin, db.Model):
    """Modelo de usuário do sistema"""
    
    __tablename__ = 'users'
    
    # Campos básicos
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Campos de perfil
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    avatar = db.Column(db.String(255))
    
    # Campos de segurança
    role = db.Column(db.String(20), default='user', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    email_verified_at = db.Column(db.DateTime)
    
    # Campos de autenticação
    last_login = db.Column(db.DateTime)
    login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    
    # Campos de 2FA
    two_factor_secret = db.Column(db.String(32))
    two_factor_enabled = db.Column(db.Boolean, default=False)
    
    # Campos de auditoria
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id'))
    professional = db.relationship('Professional', backref='users')
    
    # Tokens de reset
    reset_tokens = db.relationship('PasswordResetToken', backref='user', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.username:
            self.username = self.email.split('@')[0]
    
    @property
    def full_name(self):
        """Retorna o nome completo do usuário"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_locked(self):
        """Verifica se a conta está bloqueada"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
    
    def set_password(self, password):
        """Define a senha do usuário"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    def generate_two_factor_secret(self):
        """Gera chave secreta para 2FA"""
        self.two_factor_secret = secrets.token_hex(16)
        return self.two_factor_secret
    
    def enable_two_factor(self):
        """Habilita autenticação de dois fatores"""
        if not self.two_factor_secret:
            self.generate_two_factor_secret()
        self.two_factor_enabled = True
    
    def disable_two_factor(self):
        """Desabilita autenticação de dois fatores"""
        self.two_factor_enabled = False
        self.two_factor_secret = None
    
    def increment_login_attempts(self):
        """Incrementa tentativas de login"""
        self.login_attempts += 1
        if self.login_attempts >= 5:
            from datetime import timedelta
            self.locked_until = datetime.utcnow() + timedelta(minutes=15)
    
    def reset_login_attempts(self):
        """Reseta tentativas de login"""
        self.login_attempts = 0
        self.locked_until = None
    
    def update_last_login(self):
        """Atualiza último login"""
        self.last_login = datetime.utcnow()
        self.reset_login_attempts()
    
    def has_role(self, role):
        """Verifica se o usuário tem um determinado papel"""
        return self.role == role or self.role == 'admin'
    
    def can_access(self, resource):
        """Verifica se o usuário pode acessar um recurso"""
        if self.role == 'admin':
            return True
        
        # Define permissões por recurso
        permissions = {
            'patients': ['admin', 'receptionist', 'professional'],
            'professionals': ['admin'],
            'appointments': ['admin', 'receptionist', 'professional'],
            'reports': ['admin', 'receptionist'],
            'users': ['admin']
        }
        
        return resource in permissions and self.role in permissions[resource]
    
    def to_dict(self):
        """Converte o usuário para dicionário"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'two_factor_enabled': self.two_factor_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class PasswordResetToken(db.Model):
    """Token para reset de senha"""
    
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user_id, expires_in_hours=24):
        self.user_id = user_id
        self.token = secrets.token_urlsafe(32)
        from datetime import timedelta
        self.expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
    
    @property
    def is_expired(self):
        """Verifica se o token expirou"""
        return datetime.utcnow() > self.expires_at
    
    def use(self):
        """Marca o token como usado"""
        self.used = True

@login_manager.user_loader
def load_user(user_id):
    """Carrega o usuário para o Flask-Login"""
    return User.query.get(int(user_id))
