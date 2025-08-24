#!/usr/bin/env python3
"""
Ponto de entrada principal da aplicação Sistema Clínica
Versão Modernizada - Fase 1: Interface e PWA
"""

import os
from dotenv import load_dotenv
from app import create_app

# Carrega variáveis de ambiente
load_dotenv()

# Cria a aplicação Flask
app = create_app()

if __name__ == '__main__':
    # Configurações de desenvolvimento
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    print("🚀 SISTEMA CLÍNICA - VERSÃO MODERNIZADA")
    print("=" * 50)
    print(f"🌐 Servidor rodando em: http://{host}:{port}")
    print(f"🔧 Debug mode: {'ON' if debug else 'OFF'}")
    print(f"📱 PWA: Habilitado")
    print("=" * 50)
    print("Pressione CTRL+C para parar")
    
    # Inicia o servidor
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=True
    )
