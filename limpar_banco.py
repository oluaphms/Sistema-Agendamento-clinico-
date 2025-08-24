#!/usr/bin/env python3
"""
Script para limpar o banco e recriar apenas os usuários válidos
"""

import sqlite3
import os
from datetime import datetime

def limpar_e_recriar_banco():
    """Limpa o banco e recria apenas os usuários válidos"""
    try:
        # Backup do banco atual
        if os.path.exists('instance/clinica.db'):
            os.rename('instance/clinica.db', 'instance/clinica_backup.db')
            print("💾 Backup criado: clinica_backup.db")
        
        # Conecta ao novo banco
        conn = sqlite3.connect('instance/clinica.db')
        cursor = conn.cursor()
        
        print("🔧 Criando nova estrutura do banco...")
        
        # Cria tabela usuario com estrutura correta
        cursor.execute("""
            CREATE TABLE usuario (
                id INTEGER PRIMARY KEY,
                usuario VARCHAR(50),
                senha VARCHAR(200) NOT NULL,
                role VARCHAR(20) DEFAULT 'recepcao',
                profissional_id INTEGER,
                cpf TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                primeiro_acesso BOOLEAN DEFAULT 1,
                data_criacao DATETIME,
                ultimo_acesso DATETIME
            )
        """)
        
        # Cria outras tabelas necessárias
        cursor.execute("""
            CREATE TABLE paciente (
                id INTEGER PRIMARY KEY,
                nome VARCHAR(120) NOT NULL,
                cpf VARCHAR(14) UNIQUE,
                telefone VARCHAR(30),
                email VARCHAR(120),
                endereco TEXT,
                data_nascimento VARCHAR(10),
                observacoes TEXT,
                convenio VARCHAR(120)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE profissional (
                id INTEGER PRIMARY KEY,
                nome VARCHAR(120) NOT NULL,
                especialidade VARCHAR(120),
                telefone VARCHAR(30),
                email VARCHAR(120),
                horarios TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE servico (
                id INTEGER PRIMARY KEY,
                nome VARCHAR(120) NOT NULL,
                duracao_min INTEGER DEFAULT 30,
                preco REAL DEFAULT 0.0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE agendamento (
                id INTEGER PRIMARY KEY,
                paciente_id INTEGER NOT NULL,
                profissional_id INTEGER NOT NULL,
                servico_id INTEGER NOT NULL,
                data VARCHAR(10) NOT NULL,
                hora VARCHAR(5) NOT NULL,
                duracao INTEGER DEFAULT 30,
                status VARCHAR(20) DEFAULT 'Agendado',
                observacoes TEXT,
                origem VARCHAR(20),
                valor_pago REAL DEFAULT 0.0,
                FOREIGN KEY (paciente_id) REFERENCES paciente (id),
                FOREIGN KEY (profissional_id) REFERENCES profissional (id),
                FOREIGN KEY (servico_id) REFERENCES servico (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE prontuario (
                id INTEGER PRIMARY KEY,
                paciente_id INTEGER NOT NULL,
                data VARCHAR(10) NOT NULL,
                anotacao TEXT NOT NULL,
                FOREIGN KEY (paciente_id) REFERENCES paciente (id)
            )
        """)
        
        print("✅ Estrutura do banco criada com sucesso!")
        
        # Cria usuários padrão válidos
        from werkzeug.security import generate_password_hash
        
        usuarios_padrao = [
            {
                'cpf': '12345678909',  # CPF válido
                'nome': 'Desenvolvedor',
                'senha': generate_password_hash('123'),
                'role': 'admin',
                'primeiro_acesso': False,
                'descricao': 'Usuário com acesso total ao sistema para desenvolvimento'
            },
            {
                'cpf': '98765432100',  # CPF válido
                'nome': 'Administrador',
                'senha': generate_password_hash('987'),
                'role': 'admin',
                'primeiro_acesso': False,
                'descricao': 'Usuário administrador principal do sistema'
            },
            {
                'cpf': '11144477735',  # CPF válido
                'nome': 'Recepção',
                'senha': generate_password_hash('111'),
                'role': 'recepcao',
                'primeiro_acesso': False,
                'descricao': 'Usuário de recepção com acesso a agendamentos e pacientes'
            },
            {
                'cpf': '22233344455',  # CPF válido
                'nome': 'Profissional',
                'senha': generate_password_hash('222'),
                'role': 'profissional',
                'primeiro_acesso': False,
                'descricao': 'Usuário profissional de saúde'
            }
        ]
        
        print("👥 Criando usuários padrão válidos...")
        
        for usuario in usuarios_padrao:
            cursor.execute("""
                INSERT INTO usuario (nome, cpf, senha, role, primeiro_acesso, data_criacao)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (usuario['nome'], usuario['cpf'], usuario['senha'], usuario['role'], 
                  usuario['primeiro_acesso'], datetime.now()))
            
            print(f"  ✅ {usuario['nome']} ({usuario['role']}) - CPF: {usuario['cpf']}")
        
        # Commit das alterações
        conn.commit()
        print("💾 Banco limpo e recriado com sucesso!")
        
        # Mostra estatísticas finais
        cursor.execute("SELECT COUNT(*) FROM usuario")
        total_usuarios = cursor.fetchone()[0]
        
        cursor.execute("SELECT role, COUNT(*) FROM usuario GROUP BY role")
        usuarios_por_role = cursor.fetchall()
        
        print("\n📊 Estatísticas finais:")
        print(f"   Total de usuários: {total_usuarios}")
        for role, count in usuarios_por_role:
            print(f"   {role.capitalize()}: {count}")
        
        print("\n🔑 USUÁRIOS PADRÃO CRIADOS:")
        print("   Desenvolvedor: CPF 12345678909, Senha 123 (Admin)")
        print("   Administrador: CPF 98765432100, Senha 987 (Admin)")
        print("   Recepção: CPF 11144477735, Senha 111 (Recepção)")
        print("   Profissional: CPF 22233344455, Senha 222 (Profissional)")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🧹 Limpeza e Recriação do Banco de Dados")
    print("=" * 60)
    limpar_e_recriar_banco()
    print("\n" + "=" * 60)
    print("✅ Processo finalizado!")
