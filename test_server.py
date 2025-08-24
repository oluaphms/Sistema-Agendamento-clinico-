from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Servidor Flask funcionando!</h1><p>Se você vê esta mensagem, o Flask está funcionando perfeitamente.</p>'

@app.route('/test')
def test():
    return '<h2>Página de teste</h2><p>Esta é uma página de teste simples.</p>'

if __name__ == '__main__':
    print("Iniciando servidor de teste...")
    print("Acesse: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
