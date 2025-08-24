#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({'message': 'Flask está funcionando!'})

@app.route('/test')
def test():
    return jsonify({'status': 'success', 'message': 'Teste OK'})

if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask de teste...")
    app.run(debug=True, host='0.0.0.0', port=5000)
