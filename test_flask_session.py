#!/usr/bin/env python3
"""
Teste simples para verificar se o Flask e as sessões estão funcionando
"""

from flask import Flask, session, g, render_template_string
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key'

# Simular configuração do menu
MENU_ITEMS = [
    {"key": "dashboard",     "name": "",        "icon": "bi-speedometer2",  "url": "/dashboard"},
    {"key": "pacientes",     "name": "",        "icon": "bi-people",        "url": "/pacientes"},
    {"key": "profissionais", "name": "",    "icon": "bi-person-badge",  "url": "/profissionais"},
    {"key": "servicos",      "name": "",         "icon": "bi-tools",         "url": "/servicos"},
    {"key": "agenda",        "name": "",           "icon": "bi-calendar3",     "url": "/agenda"},
    {"key": "usuarios",      "name": "",         "icon": "bi-person-gear",   "url": "/usuarios"},
    {"key": "relatorios",    "name": "",       "icon": "bi-graph-up",      "url": "/relatorios"},
    {"key": "notificacoes",  "name": "",     "icon": "bi-gear",          "url": "/configuracoes"},
    {"key": "sobre",         "name": "",            "icon": "bi-info-circle",   "url": "/sobre"},
    {"key": "logout",        "name": "",             "icon": "bi-box-arrow-right","url": "/logout"},
]

ROLE_PERMISSIONS = {
    "admin":       {"dashboard","pacientes","profissionais","servicos","agenda","usuarios","relatorios","notificacoes","sobre","logout"},
    "recepcao":    {"dashboard","pacientes","agenda","relatorios","notificacoes","sobre","logout"},
    "profissional":{"dashboard","agenda","pacientes","relatorios","sobre","logout"},
}

@app.before_request
def build_menu_items():
    """Construir itens do menu baseado no papel do usuário"""
    role = session.get("role", "recepcao")  # fallback conservador
    allowed = ROLE_PERMISSIONS.get(role, set())
    items = [i for i in MENU_ITEMS if i["key"] in allowed]
    
    # Fallback para evitar lista vazia:
    if not items:
        items = [i for i in MENU_ITEMS if i["key"] in {"dashboard","logout"}]
    
    g.menu_items = items
    
    # Log para diagnóstico
    print(f"MENU_ITEMS_RESOLVED: role={role} items={[i['key'] for i in items]}")

@app.route('/')
def index():
    """Página principal de teste"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Teste Flask Session</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: white; }
            .container { max-width: 800px; margin: 0 auto; }
            .role-selector { margin: 20px 0; }
            .role-btn { 
                padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer;
                background: #0d6efd; color: white;
            }
            .role-btn.active { background: #198754; }
            .menu-preview { 
                background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin: 20px 0;
            }
            .menu-item { 
                display: inline-block; margin: 5px; padding: 10px; background: rgba(255,255,255,0.2); 
                border-radius: 5px; border: 1px solid rgba(255,255,255,0.3);
            }
            .debug-info { 
                background: rgba(255,255,255,0.05); padding: 15px; border-radius: 5px; margin: 10px 0;
                font-family: monospace; font-size: 12px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧪 Teste Flask Session + Menu</h1>
            
            <div class="role-selector">
                <h3>Selecione um papel para testar:</h3>
                <button class="role-btn" onclick="setRole('admin')">👑 Admin</button>
                <button class="role-btn" onclick="setRole('recepcao')">📞 Recepção</button>
                <button class="role-btn" onclick="setRole('profissional')">👨‍⚕️ Profissional</button>
                <button class="role-btn" onclick="setRole('none')">❌ Sem papel</button>
            </div>
            
            <div class="debug-info">
                <strong>Role atual:</strong> <span id="currentRole">{{ session.get('role', 'Nenhum') }}</span><br>
                <strong>Total de itens:</strong> <span id="totalItems">{{ g.menu_items|length }}</span><br>
                <strong>Itens permitidos:</strong> <span id="allowedItems">{{ g.menu_items|map(attribute='key')|list|join(', ') }}</span>
            </div>
            
            <div class="menu-preview">
                <h3>📋 Preview do Menu ({{ g.menu_items|length }} itens):</h3>
                {% for item in g.menu_items %}
                <div class="menu-item">
                    <i class="bi {{ item.icon }}"></i>
                    {{ item.name }}
                </div>
                {% endfor %}
            </div>
            
            <div class="debug-info">
                <h4>🔍 JSON dos itens (para debug):</h4>
                <pre>{{ g.menu_items|tojson(indent=2) }}</pre>
            </div>
            
            <div class="debug-info">
                <h4>🧪 Teste do Carrossel:</h4>
                <button onclick="testCarousel()" style="padding: 10px 20px; background: #dc3545; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    🎠 Testar Carrossel
                </button>
            </div>
        </div>
        
        <script>
            function setRole(role) {
                fetch('/set-role/' + role)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            location.reload();
                        }
                    });
            }
            
            function testCarousel() {
                const items = {{ g.menu_items|tojson }};
                console.log('🎠 Testando carrossel com itens:', items);
                console.table(items);
                
                if (items.length === 0) {
                    alert('❌ ERRO: Nenhum item de menu recebido!');
                } else if (items.length === 1 && items[0].key === 'logout') {
                    alert('⚠️ AVISO: Apenas "Sair" disponível. Verificar permissões.');
                } else {
                    alert(`✅ SUCESSO: ${items.length} itens de menu carregados!`);
                }
            }
            
            // Marcar botão ativo
            document.addEventListener('DOMContentLoaded', () => {
                const currentRole = '{{ session.get("role", "none") }}';
                document.querySelectorAll('.role-btn').forEach(btn => {
                    if (btn.textContent.toLowerCase().includes(currentRole.toLowerCase())) {
                        btn.classList.add('active');
                    }
                });
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/set-role/<role>')
def set_role(role):
    """Definir papel do usuário para teste"""
    if role == 'none':
        session.pop('role', None)
    else:
        session['role'] = role
    
    return {'success': True, 'role': role}

if __name__ == '__main__':
    print("🚀 Iniciando servidor de teste...")
    print("📱 Acesse: http://localhost:5000")
    print("🔑 Teste diferentes papéis para ver as permissões do menu")
    
    app.run(debug=True, port=5000)
