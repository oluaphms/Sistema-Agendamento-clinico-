#!/usr/bin/env python3
"""
Teste da funcionalidade de exportação de relatórios
Sistema Clínica - Verificação de funcionalidades
"""

import requests
import json
from datetime import datetime, timedelta

def test_exportacao_api():
    """Testa as APIs de exportação"""
    
    base_url = "http://127.0.0.1:8080"
    
    print("🧪 Testando APIs de Exportação...")
    print("=" * 50)
    
    # Teste 1: Exportar CSV
    print("\n1️⃣ Testando exportação CSV...")
    try:
        response = requests.get(f"{base_url}/exportar?formato=csv")
        if response.status_code == 200:
            print("✅ CSV exportado com sucesso!")
            print(f"   Tamanho: {len(response.content)} bytes")
            print(f"   Content-Type: {response.headers.get('content-type')}")
        else:
            print(f"❌ Erro ao exportar CSV: {response.status_code}")
            print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro na requisição CSV: {e}")
    
    # Teste 2: Exportar PDF (HTML)
    print("\n2️⃣ Testando exportação PDF (HTML)...")
    try:
        response = requests.get(f"{base_url}/exportar?formato=pdf")
        if response.status_code == 200:
            print("✅ HTML exportado com sucesso!")
            print(f"   Tamanho: {len(response.content)} bytes")
            print(f"   Content-Type: {response.headers.get('content-type')}")
            
            # Verificar se contém conteúdo HTML
            content = response.text
            if "<html" in content and "<table" in content:
                print("   ✅ Conteúdo HTML válido")
            else:
                print("   ⚠️ Conteúdo HTML pode estar incompleto")
        else:
            print(f"❌ Erro ao exportar PDF: {response.status_code}")
            print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro na requisição PDF: {e}")
    
    # Teste 3: Exportar com filtros de data
    print("\n3️⃣ Testando exportação com filtros de data...")
    try:
        hoje = datetime.now()
        inicio = hoje - timedelta(days=7)
        
        params = {
            'formato': 'csv',
            'inicio': inicio.strftime('%Y-%m-%d'),
            'fim': hoje.strftime('%Y-%m-%d')
        }
        
        response = requests.get(f"{base_url}/exportar", params=params)
        if response.status_code == 200:
            print("✅ Exportação com filtros funcionando!")
            print(f"   Período: {inicio.strftime('%d/%m/%Y')} - {hoje.strftime('%d/%m/%Y')}")
            print(f"   Tamanho: {len(response.content)} bytes")
        else:
            print(f"❌ Erro com filtros: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro na requisição com filtros: {e}")
    
    # Teste 4: Formato inválido
    print("\n4️⃣ Testando formato inválido...")
    try:
        response = requests.get(f"{base_url}/exportar?formato=invalid")
        if response.status_code == 302:  # Redirecionamento esperado
            print("✅ Redirecionamento correto para formato inválido")
        else:
            print(f"⚠️ Comportamento inesperado: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no teste de formato inválido: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Testes concluídos!")

def test_relatorios_page():
    """Testa se a página de relatórios está acessível"""
    
    base_url = "http://127.0.0.1:8080"
    
    print("\n🌐 Testando página de relatórios...")
    print("=" * 50)
    
    try:
        response = requests.get(f"{base_url}/relatorios")
        if response.status_code == 200:
            print("✅ Página de relatórios acessível!")
            
            # Verificar se contém elementos importantes
            content = response.text
            
            checks = [
                ("📊 Analytics & Relatórios", "Título da página"),
                ("exportarRelatorio", "Função JavaScript de exportação"),
                ("dataInicioExport", "Campo de data início"),
                ("dataFimExport", "Campo de data fim"),
                ("relatorios.css", "Arquivo CSS específico")
            ]
            
            for check, description in checks:
                if check in content:
                    print(f"   ✅ {description}: Encontrado")
                else:
                    print(f"   ❌ {description}: Não encontrado")
                    
        else:
            print(f"❌ Erro ao acessar página: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar página: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando testes de exportação...")
    print("⚠️  Certifique-se de que o servidor está rodando na porta 8080")
    print()
    
    try:
        test_relatorios_page()
        test_exportacao_api()
        
    except KeyboardInterrupt:
        print("\n⏹️  Testes interrompidos pelo usuário")
    except Exception as e:
        print(f"\n💥 Erro geral nos testes: {e}")
    
    print("\n✨ Testes finalizados!")
