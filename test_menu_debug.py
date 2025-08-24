from flask import Flask, render_template, session, g, jsonify
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Simular dados do menu
MENU_ITEMS = [
    {"key": "dashboard", "name": "Dashboard", "icon": "bi-speedometer2", "url": "/dashboard"},
    {"key": "pacientes", "name": "Pacientes", "icon": "bi-people", "url": "/pacientes"},
    {"key": "logout", "name": "Sair", "icon": "bi-box-arrow-right", "url": "/logout"},
]

@app.before_request
def build_menu_items():
    """Simula a construção do menu"""
    # Simular sessão
    session['role'] = 'admin'
    
    # Construir menu baseado no role
    allowed_keys = {"dashboard", "pacientes", "logout"}
    items = [i for i in MENU_ITEMS if i["key"] in allowed_keys]
    
    # Garantir que não há valores None/Undefined
    for item in items:
        for key, value in item.items():
            if value is None:
                item[key] = ""
            elif not isinstance(value, (str, int, float, bool)):
                item[key] = str(value)
    
    g.menu_items = items
    print(f"Menu items: {g.menu_items}")

@app.route('/')
def index():
    """Página de teste"""
    return render_template('test_menu_debug.html')

@app.route('/api/menu')
def api_menu():
    """API para retornar menu em JSON"""
    try:
        # Garantir que todos os valores são serializáveis
        menu_data = []
        for item in g.menu_items:
            safe_item = {}
            for key, value in item.items():
                if value is None:
                    safe_item[key] = ""
                elif isinstance(value, (str, int, float, bool)):
                    safe_item[key] = value
                else:
                    safe_item[key] = str(value)
            menu_data.append(safe_item)
        
        return jsonify({
            'success': True,
            'menu_items': menu_data,
            'total_items': len(menu_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'menu_items': []
        }), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
