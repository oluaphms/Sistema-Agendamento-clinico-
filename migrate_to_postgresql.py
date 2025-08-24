#!/usr/bin/env python3
"""
Script para migrar do SQLite para PostgreSQL
Execute este script quando quiser migrar para um banco mais robusto
"""

import os
import sys
import sqlite3
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    try:
        import psycopg2
        print("✓ psycopg2 instalado")
        return True
    except ImportError:
        print("✗ psycopg2 não instalado")
        print("Instale com: pip install psycopg2-binary")
        return False

def get_sqlite_data(db_path):
    """Extrai dados do SQLite"""
    if not os.path.exists(db_path):
        print(f"❌ Arquivo {db_path} não encontrado!")
        return None
    
    print(f"📊 Conectando ao SQLite: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Lista todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row['name'] for row in cursor.fetchall()]
        
        print(f"📋 Tabelas encontradas: {', '.join(tables)}")
        
        data = {}
        for table in tables:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            data[table] = [dict(row) for row in rows]
            print(f"  - {table}: {len(rows)} registros")
        
        conn.close()
        return data
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao SQLite: {e}")
        return None

def create_postgresql_tables(cursor):
    """Cria tabelas no PostgreSQL"""
    print("🔨 Criando tabelas no PostgreSQL...")
    
    # Scripts de criação das tabelas
    tables_sql = {
        'usuario': """
        CREATE TABLE IF NOT EXISTS usuario (
            id SERIAL PRIMARY KEY,
            usuario VARCHAR(50) UNIQUE NOT NULL,
            senha VARCHAR(200) NOT NULL,
            role VARCHAR(20) DEFAULT 'recepcao',
            profissional_id INTEGER
        );
        """,
        
        'paciente': """
        CREATE TABLE IF NOT EXISTS paciente (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(120) NOT NULL,
            telefone VARCHAR(30),
            email VARCHAR(120),
            nascimento VARCHAR(10),
            observacoes TEXT,
            convenio VARCHAR(120)
        );
        """,
        
        'profissional': """
        CREATE TABLE IF NOT EXISTS profissional (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(120) NOT NULL,
            especialidade VARCHAR(120),
            telefone VARCHAR(30),
            email VARCHAR(120),
            horarios TEXT
        );
        """,
        
        'servico': """
        CREATE TABLE IF NOT EXISTS servico (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(120) NOT NULL,
            duracao_min INTEGER DEFAULT 30,
            preco DECIMAL(10,2) DEFAULT 0.0
        );
        """,
        
        'agendamento': """
        CREATE TABLE IF NOT EXISTS agendamento (
            id SERIAL PRIMARY KEY,
            paciente_id INTEGER NOT NULL,
            profissional_id INTEGER NOT NULL,
            servico_id INTEGER NOT NULL,
            data VARCHAR(10) NOT NULL,
            hora VARCHAR(5) NOT NULL,
            duracao INTEGER DEFAULT 30,
            status VARCHAR(20) DEFAULT 'Agendado',
            observacoes TEXT,
            origem VARCHAR(20),
            valor_pago DECIMAL(10,2) DEFAULT 0.0
        );
        """,
        
        'prontuario': """
        CREATE TABLE IF NOT EXISTS prontuario (
            id SERIAL PRIMARY KEY,
            paciente_id INTEGER NOT NULL,
            data VARCHAR(10) NOT NULL,
            anotacao TEXT NOT NULL
        );
        """
    }
    
    for table_name, sql in tables_sql.items():
        try:
            cursor.execute(sql)
            print(f"  ✓ Tabela {table_name} criada")
        except Exception as e:
            print(f"  ✗ Erro ao criar tabela {table_name}: {e}")

def insert_data_to_postgresql(cursor, data):
    """Insere dados no PostgreSQL"""
    print("📤 Inserindo dados no PostgreSQL...")
    
    for table_name, rows in data.items():
        if not rows:
            continue
            
        print(f"  📋 Inserindo {len(rows)} registros na tabela {table_name}")
        
        for row in rows:
            try:
                # Remove o ID para deixar o PostgreSQL gerar
                if 'id' in row:
                    del row['id']
                
                # Prepara campos e valores
                fields = list(row.keys())
                values = list(row.values())
                placeholders = ', '.join(['%s'] * len(fields))
                
                sql = f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({placeholders})"
                cursor.execute(sql, values)
                
            except Exception as e:
                print(f"    ✗ Erro ao inserir registro: {e}")
                print(f"    Dados: {row}")
    
    print("  ✅ Dados inseridos com sucesso!")

def migrate_database():
    """Função principal de migração"""
    print("🚀 MIGRADOR SQLITE → POSTGRESQL")
    print("=" * 40)
    
    # Verifica dependências
    if not check_dependencies():
        return
    
    # Configurações do PostgreSQL
    print("\n📝 Configurações do PostgreSQL:")
    host = input("Host (localhost): ").strip() or "localhost"
    port = input("Porta (5432): ").strip() or "5432"
    database = input("Nome do banco: ").strip()
    username = input("Usuário: ").strip()
    password = input("Senha: ").strip()
    
    if not all([database, username, password]):
        print("❌ Todas as informações são obrigatórias!")
        return
    
    # Caminho do SQLite
    sqlite_path = input("Caminho do arquivo SQLite (clinica.db): ").strip() or "clinica.db"
    
    # Extrai dados do SQLite
    data = get_sqlite_data(sqlite_path)
    if not data:
        return
    
    # Conecta ao PostgreSQL
    print(f"\n🔌 Conectando ao PostgreSQL: {host}:{port}/{database}")
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=username,
            password=password
        )
        cursor = conn.cursor()
        print("✅ Conectado ao PostgreSQL!")
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao PostgreSQL: {e}")
        return
    
    try:
        # Cria tabelas
        create_postgresql_tables(cursor)
        
        # Insere dados
        insert_data_to_postgresql(cursor, data)
        
        # Commit das alterações
        conn.commit()
        print("\n🎉 Migração concluída com sucesso!")
        
        # Atualiza configuração
        print("\n📝 Atualize o arquivo config.py ou .env:")
        print(f"DATABASE_URL=postgresql://{username}:{password}@{host}:{port}/{database}")
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

def create_backup_script():
    """Cria script de backup para PostgreSQL"""
    backup_script = """#!/bin/bash
# Script de backup para PostgreSQL
# Execute diariamente para manter backup atualizado

BACKUP_DIR="./backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="clinica"
DB_USER="seu_usuario"
DB_HOST="localhost"

# Cria diretório de backup se não existir
mkdir -p $BACKUP_DIR

# Executa backup
pg_dump -h $DB_HOST -U $DB_USER $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Comprime backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Remove backups antigos (mantém últimos 7 dias)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup criado: $BACKUP_DIR/backup_$DATE.sql.gz"
"""
    
    with open('backup_postgresql.sh', 'w') as f:
        f.write(backup_script)
    
    print("📜 Script de backup criado: backup_postgresql.sh")

def main():
    """Menu principal"""
    while True:
        print("\nEscolha uma opção:")
        print("1. Migrar SQLite → PostgreSQL")
        print("2. Criar script de backup PostgreSQL")
        print("3. Verificar dependências")
        print("0. Sair")
        
        choice = input("\nOpção: ").strip()
        
        if choice == '1':
            migrate_database()
        elif choice == '2':
            create_backup_script()
        elif choice == '3':
            check_dependencies()
        elif choice == '0':
            print("👋 Saindo...")
            break
        else:
            print("❌ Opção inválida!")
        
        input("\nPressione Enter para continuar...")

if __name__ == '__main__':
    main()
