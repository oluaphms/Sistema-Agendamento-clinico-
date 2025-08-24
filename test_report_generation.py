#!/usr/bin/env python3
"""
Teste para verificar a geração de relatórios do sistema
"""

import requests
import os

def test_report_generation():
    """Testa a geração de relatórios"""
    
    # URL base (ajuste conforme necessário)
    base_url = "http://localhost:8080"
    
    # Endpoint do relatório
    report_url = f"{base_url}/api/sistema/relatorio"
    
    print("🧪 Testando geração de relatórios...")
    print(f"📡 URL: {report_url}")
    
    try:
        # Fazer requisição para gerar relatório
        response = requests.get(report_url)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers:")
        for key, value in response.headers.items():
            print(f"   {key}: {value}")
        
        if response.status_code == 200:
            # Verificar tipo de conteúdo
            content_type = response.headers.get('content-type', '')
            content_disposition = response.headers.get('content-disposition', '')
            
            print(f"✅ Relatório gerado com sucesso!")
            print(f"📄 Tipo de conteúdo: {content_type}")
            print(f"📁 Disposição: {content_disposition}")
            
            # Salvar arquivo para inspeção
            if 'application/pdf' in content_type:
                filename = "teste-relatorio.pdf"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"💾 PDF salvo como: {filename}")
                
            elif 'text/csv' in content_type:
                filename = "teste-relatorio.csv"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"💾 CSV salvo como: {filename}")
                
            else:
                print(f"⚠️ Tipo de conteúdo não reconhecido: {content_type}")
                # Salvar como arquivo genérico para inspeção
                filename = "teste-relatorio.bin"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"💾 Arquivo salvo como: {filename}")
                
        else:
            print(f"❌ Erro na geração do relatório")
            try:
                error_data = response.json()
                print(f"🔍 Detalhes do erro: {error_data}")
            except:
                print(f"🔍 Conteúdo da resposta: {response.text[:200]}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - Servidor não está rodando")
        print("💡 Execute 'python app.py' primeiro")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_report_generation()
