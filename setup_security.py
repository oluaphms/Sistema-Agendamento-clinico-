#!/usr/bin/env python3
"""
Script para configurar melhorias de segurança no sistema
Execute este script após a instalação para configurar recursos de segurança
"""

import os
import secrets
import string
from datetime import datetime
from app import app, db, Usuario
from security import security
from werkzeug.security import generate_password_hash

def generate_secure_secret_key(length=32):
    """Gera uma chave secreta segura"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(characters) for _ in range(length))

def setup_2fa_for_admin():
    """Configura 2FA para o usuário admin"""
    with app.app_context():
        admin = Usuario.query.filter_by(usuario='admin').first()
        if admin:
            # Gera chave secreta para 2FA
            secret_2fa = security.generate_2fa_secret()
            
            # Aqui você pode salvar a chave no banco ou em arquivo de configuração
            print(f"Chave 2FA para admin: {secret_2fa}")
            
            # Gera QR code
            qr_code = security.generate_2fa_qr(secret_2fa, 'admin')
            print("QR Code 2FA gerado com sucesso!")
            
            return secret_2fa
        else:
            print("Usuário admin não encontrado!")
            return None

def create_secure_admin_password():
    """Cria uma senha segura para o admin"""
    secure_password = security.generate_secure_password(16)
    print(f"Nova senha segura para admin: {secure_password}")
    
    with app.app_context():
        admin = Usuario.query.filter_by(usuario='admin').first()
        if admin:
            admin.senha = generate_password_hash(secure_password)
            db.session.commit()
            print("Senha do admin atualizada com sucesso!")
        else:
            print("Usuário admin não encontrado!")

def validate_system_security():
    """Valida as configurações de segurança do sistema"""
    print("\n=== VALIDAÇÃO DE SEGURANÇA ===")
    
    # Verifica configurações
    config = app.config
    
    print(f"Debug mode: {config.get('DEBUG', 'Não configurado')}")
    print(f"Secret key length: {len(config.get('SECRET_KEY', ''))}")
    print(f"Session cookie secure: {config.get('SESSION_COOKIE_SECURE', 'Não configurado')}")
    print(f"Session cookie httponly: {config.get('SESSION_COOKIE_HTTPONLY', 'Não configurado')}")
    
    # Verifica se as dependências estão instaladas
    try:
        import pyotp
        print("✓ PyOTP instalado")
    except ImportError:
        print("✗ PyOTP não instalado")
    
    try:
        import qrcode
        print("✓ QRCode instalado")
    except ImportError:
        print("✗ QRCode não instalado")
    
    try:
        import reportlab
        print("✓ ReportLab instalado")
    except ImportError:
        print("✗ ReportLab não instalado")
    
    try:
        import openpyxl
        print("✓ OpenPyXL instalado")
    except ImportError:
        print("✗ OpenPyXL não instalado")

def create_env_file():
    """Cria arquivo .env com configurações seguras"""
    env_content = f"""# Configurações de Segurança
SECRET_KEY={generate_secure_secret_key(64)}
FLASK_ENV=production
FLASK_DEBUG=False

# Configurações de Banco de Dados
DATABASE_URL=sqlite:///clinica.db

# Configurações de Email (para notificações)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-app

# Configurações de WhatsApp Business API (opcional)
WHATSAPP_API_KEY=sua-chave-api-whatsapp
WHATSAPP_PHONE_NUMBER=seu-numero-whatsapp

# Configurações de Rate Limiting
RATELIMIT_STORAGE_URL=memory://
RATELIMIT_DEFAULT=200 per day;50 per hour;10 per minute

# Configurações de Segurança Adicional
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=3600
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("Arquivo .env criado com configurações seguras!")

def main():
    """Função principal"""
    print("🔒 CONFIGURADOR DE SEGURANÇA - SISTEMA CLÍNICA")
    print("=" * 50)
    
    while True:
        print("\nEscolha uma opção:")
        print("1. Gerar chave secreta segura")
        print("2. Configurar 2FA para admin")
        print("3. Criar senha segura para admin")
        print("4. Validar configurações de segurança")
        print("5. Criar arquivo .env")
        print("6. Executar todas as configurações")
        print("0. Sair")
        
        choice = input("\nOpção: ").strip()
        
        if choice == '1':
            secret = generate_secure_secret_key()
            print(f"\nChave secreta gerada: {secret}")
            print("Copie esta chave para o arquivo .env ou config.py")
            
        elif choice == '2':
            print("\nConfigurando 2FA para admin...")
            setup_2fa_for_admin()
            
        elif choice == '3':
            print("\nCriando senha segura para admin...")
            create_secure_admin_password()
            
        elif choice == '4':
            print("\nValidando configurações...")
            validate_system_security()
            
        elif choice == '5':
            print("\nCriando arquivo .env...")
            create_env_file()
            
        elif choice == '6':
            print("\nExecutando todas as configurações...")
            print("1. Gerando chave secreta...")
            secret = generate_secure_secret_key()
            print("2. Configurando 2FA...")
            setup_2fa_for_admin()
            print("3. Criando senha segura...")
            create_secure_admin_password()
            print("4. Criando arquivo .env...")
            create_env_file()
            print("5. Validando configurações...")
            validate_system_security()
            print("\n✅ Todas as configurações foram executadas!")
            
        elif choice == '0':
            print("\n👋 Saindo...")
            break
            
        else:
            print("\n❌ Opção inválida!")
        
        input("\nPressione Enter para continuar...")

if __name__ == '__main__':
    main()
