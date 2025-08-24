#!/usr/bin/env python3
"""
Teste para verificar se a correção do menu está funcionando
"""

from flask import Flask, g
import json

app = Flask(__name__)

@app.before_request
def set_menu_items():
    """Define g.menu_items com valor padrão antes de cada requisição"""
    if not hasattr(g, 'menu_items') or g.menu_items is None:
        g.menu_items = []

@app.route('/test')
def test_menu():
    """Rota de teste para verificar g.menu_items"""
    # Simular alguns itens de menu
    g.menu_items = [
        {"key": "dashboard", "name": "Dashboard", "icon": "bi-speedometer2", "url": "/dashboard"},
        {"key": "logout", "name": "Sair", "icon": "bi-box-arrow-right", "url": "/logout"}
    ]
    
    # Testar serialização JSON
    try:
        menu_json = json.dumps(g.menu_items)
        return {
            "status": "success",
            "message": "Menu items configurados com sucesso",
            "menu_items": g.menu_items,
            "json_serialized": menu_json,
            "length": len(g.menu_items)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao serializar menu: {str(e)}",
            "error_type": type(e).__name__
        }

@app.route('/test-empty')
def test_empty_menu():
    """Rota de teste para verificar comportamento com menu vazio"""
    # Não definir g.menu_items para testar o fallback
    try:
        # Tentar serializar g.menu_items (deve ser lista vazia por padrão)
        menu_json = json.dumps(g.menu_items)
        return {
            "status": "success",
            "message": "Menu vazio configurado com sucesso",
            "menu_items": g.menu_items,
            "json_serialized": menu_json,
            "length": len(g.menu_items)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao serializar menu vazio: {str(e)}",
            "error_type": type(e).__name__
        }

if __name__ == '__main__':
    print("🧪 Testando correção do menu...")
    print("📱 Acesse http://localhost:5000/test para testar menu com itens")
    print("📱 Acesse http://localhost:5000/test-empty para testar menu vazio")
    app.run(debug=True, port=5000)
