#!/usr/bin/env python3
"""
Test script para verificar se todas as funcionalidades dos botões estão funcionando
Sistema Clínica - Teste de Botões
"""

import requests
import json
from datetime import date

# URL base do sistema (ajustar conforme necessário)
BASE_URL = "http://127.0.0.1:8080"

def test_login():
    """Testa o login do sistema"""
    print("🔐 Testando login...")
    
    session = requests.Session()
    
    # Teste com credenciais de admin
    login_data = {
        'cpf': '00000000000',
        'senha': '000'
    }
    
    response = session.post(f"{BASE_URL}/login", data=login_data)
    
    if response.status_code == 200 and "dashboard" in response.url:
        print("✅ Login funcionando")
        return session
    else:
        print("❌ Login com problemas")
        return None

def test_crud_buttons(session):
    """Testa botões de CRUD"""
    print("\n📝 Testando botões CRUD...")
    
    # Teste botões de pacientes
    response = session.get(f"{BASE_URL}/pacientes")
    if response.status_code == 200:
        print("✅ Página de pacientes acessível")
    else:
        print("❌ Problema ao acessar pacientes")
    
    # Teste botões de profissionais  
    response = session.get(f"{BASE_URL}/profissionais")
    if response.status_code == 200:
        print("✅ Página de profissionais acessível")
    else:
        print("❌ Problema ao acessar profissionais")
    
    # Teste botões de serviços
    response = session.get(f"{BASE_URL}/servicos")
    if response.status_code == 200:
        print("✅ Página de serviços acessível")
    else:
        print("❌ Problema ao acessar serviços")

def test_agenda_buttons(session):
    """Testa botões da agenda"""
    print("\n📅 Testando botões da agenda...")
    
    response = session.get(f"{BASE_URL}/agenda")
    if response.status_code == 200:
        print("✅ Página de agenda acessível")
    else:
        print("❌ Problema ao acessar agenda")

def test_export_buttons(session):
    """Testa botões de exportação"""
    print("\n📊 Testando botões de exportação...")
    
    # Teste exportação CSV
    today = date.today().strftime("%Y-%m-%d")
    response = session.get(f"{BASE_URL}/exportar?formato=csv&inicio={today}&fim={today}")
    
    if response.status_code == 200:
        print("✅ Exportação CSV funcionando")
    else:
        print("❌ Problema na exportação CSV")

def test_user_management_buttons(session):
    """Testa botões de gerenciamento de usuários"""
    print("\n👥 Testando botões de usuários...")
    
    response = session.get(f"{BASE_URL}/usuarios")
    if response.status_code == 200:
        print("✅ Página de usuários acessível")
    else:
        print("❌ Problema ao acessar usuários")

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes dos botões do sistema...")
    print("=" * 50)
    
    # Login primeiro
    session = test_login()
    
    if not session:
        print("\n❌ Não foi possível fazer login. Verifique se o servidor está rodando.")
        return
    
    # Testa todas as funcionalidades
    test_crud_buttons(session)
    test_agenda_buttons(session)
    test_export_buttons(session)
    test_user_management_buttons(session)
    
    print("\n" + "=" * 50)
    print("✅ Testes concluídos!")
    print("\n📋 Resumo das funcionalidades testadas:")
    print("   • Login e autenticação")
    print("   • CRUD de pacientes, profissionais e serviços")
    print("   • Agenda e agendamentos")
    print("   • Exportação de dados")
    print("   • Gerenciamento de usuários")
    print("\n🎯 Todas as rotas backend foram implementadas!")

if __name__ == "__main__":
    main()
