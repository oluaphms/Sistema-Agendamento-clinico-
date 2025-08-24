import re
import secrets
import string
from datetime import datetime, timedelta
from flask import request, session, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp
import qrcode
from io import BytesIO
import base64

class SecurityManager:
    def __init__(self):
        self.max_login_attempts = 5
        self.lockout_duration = 15  # minutos
        
    def generate_secure_password(self, length=12):
        """Gera uma senha segura com caracteres especiais"""
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    def validate_password_strength(self, password):
        """Valida a força da senha"""
        if len(password) < 8:
            return False, "Senha deve ter pelo menos 8 caracteres"
        
        if not re.search(r"[A-Z]", password):
            return False, "Senha deve conter pelo menos uma letra maiúscula"
            
        if not re.search(r"[a-z]", password):
            return False, "Senha deve conter pelo menos uma letra minúscula"
            
        if not re.search(r"\d", password):
            return False, "Senha deve conter pelo menos um número"
            
        if not re.search(r"[!@#$%^&*]", password):
            return False, "Senha deve conter pelo menos um caractere especial"
            
        return True, "Senha válida"
    
    def sanitize_input(self, text):
        """Sanitiza entrada do usuário para evitar XSS"""
        if not text:
            return text
            
        # Remove tags HTML perigosas
        dangerous_tags = ['<script>', '</script>', '<iframe>', '</iframe>', '<object>', '</object>']
        for tag in dangerous_tags:
            text = text.replace(tag, '')
            
        # Remove caracteres perigosos
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        
        return text
    
    def validate_email(self, email):
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_phone(self, phone):
        """Valida formato de telefone brasileiro"""
        # Remove caracteres não numéricos
        phone_clean = re.sub(r'\D', '', phone)
        
        # Verifica se tem 10 ou 11 dígitos (com DDD)
        if len(phone_clean) in [10, 11]:
            return True
        return False
    
    def generate_2fa_secret(self):
        """Gera chave secreta para autenticação de dois fatores"""
        return pyotp.random_base32()
    
    def generate_2fa_qr(self, secret, username):
        """Gera QR code para configuração do 2FA"""
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=username,
            issuer_name="Sistema Clínica"
        )
        
        # Gera QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Converte para base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def verify_2fa_code(self, secret, code):
        """Verifica código 2FA"""
        totp = pyotp.TOTP(secret)
        return totp.verify(code)
    
    def check_rate_limit(self, key, max_requests, window):
        """Verifica rate limiting simples"""
        current_time = datetime.now()
        
        if key not in session:
            session[key] = {'count': 0, 'reset_time': current_time + timedelta(minutes=window)}
        
        if current_time > session[key]['reset_time']:
            session[key] = {'count': 0, 'reset_time': current_time + timedelta(minutes=window)}
        
        if session[key]['count'] >= max_requests:
            return False
        
        session[key]['count'] += 1
        return True

# Instância global
security = SecurityManager()

def require_2fa(f):
    """Decorator para exigir 2FA em rotas específicas"""
    def decorated_function(*args, **kwargs):
        if 'usuario' in session and not session.get('2fa_verified'):
            flash("Autenticação de dois fatores necessária", "warning")
            return redirect(url_for('verify_2fa'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def validate_csrf_token():
    """Valida token CSRF"""
    if request.method == 'POST':
        token = request.form.get('csrf_token')
        if not token or token != session.get('csrf_token'):
            flash("Token de segurança inválido", "danger")
            return False
    return True

def generate_csrf_token():
    """Gera token CSRF"""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']
