#!/usr/bin/env python3
"""
Script de migração para atualizar a tabela de pacientes
Adiciona os campos: cpf, categoria, data_cadastro, ultima_atualizacao
"""

import sqlite3
import os
from datetime import datetime

def migrate_pacientes():
    """Migra a tabela de pacientes para incluir novos campos"""
    
    # Caminho do banco
    db_path = 'instance/clinica.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado em: {db_path}")
        return False
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Iniciando migração da tabela pacientes...")
        
        # Verificar se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='paciente'")
        if not cursor.fetchone():
            print("❌ Tabela 'paciente' não encontrada")
            return False
        
        # Verificar estrutura atual da tabela
        cursor.execute("PRAGMA table_info(paciente)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 Colunas atuais: {columns}")
        
        # Adicionar novos campos se não existirem
        new_fields = [
            ('cpf', 'TEXT UNIQUE'),
            ('categoria', 'TEXT DEFAULT "particular"'),
            ('data_cadastro', 'DATETIME'),
            ('ultima_atualizacao', 'DATETIME')
        ]
        
        for field_name, field_type in new_fields:
            if field_name not in columns:
                print(f"➕ Adicionando campo: {field_name}")
                try:
                    cursor.execute(f"ALTER TABLE paciente ADD COLUMN {field_name} {field_type}")
                    print(f"✅ Campo {field_name} adicionado com sucesso")
                except Exception as e:
                    print(f"⚠️ Erro ao adicionar campo {field_name}: {e}")
            else:
                print(f"ℹ️ Campo {field_name} já existe")
        
        # Atualizar registros existentes com valores padrão
        now = datetime.now().isoformat()
        
        # Adicionar CPF temporário para registros existentes
        cursor.execute("UPDATE paciente SET cpf = '00000000000' WHERE cpf IS NULL")
        print("✅ CPFs temporários adicionados para registros existentes")
        
        # Adicionar categoria padrão
        cursor.execute("UPDATE paciente SET categoria = 'particular' WHERE categoria IS NULL")
        print("✅ Categorias padrão definidas")
        
        # Adicionar datas de cadastro
        cursor.execute("UPDATE paciente SET data_cadastro = ? WHERE data_cadastro IS NULL", (now,))
        cursor.execute("UPDATE paciente SET ultima_atualizacao = ? WHERE ultima_atualizacao IS NULL", (now,))
        print("✅ Datas de cadastro e atualização definidas")
        
        # Commit das alterações
        conn.commit()
        
        # Verificar estrutura final
        cursor.execute("PRAGMA table_info(paciente)")
        final_columns = [col[1] for col in cursor.fetchall()]
        print(f"📋 Colunas finais: {final_columns}")
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM paciente")
        count = cursor.fetchone()[0]
        print(f"📊 Total de pacientes: {count}")
        
        print("🎉 Migração concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()

def create_backup():
    """Cria backup do banco antes da migração"""
    
    db_path = 'instance/clinica.db'
    backup_path = f'instance/clinica_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    
    if os.path.exists(db_path):
        try:
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"💾 Backup criado: {backup_path}")
            return True
        except Exception as e:
            print(f"⚠️ Erro ao criar backup: {e}")
            return False
    return False

if __name__ == "__main__":
    print("🚀 Script de Migração - Tabela Pacientes")
    print("=" * 50)
    
    # Criar backup
    if create_backup():
        print("✅ Backup criado com sucesso")
    else:
        print("⚠️ Backup não foi criado")
    
    print()
    
    # Executar migração
    if migrate_pacientes():
        print("\n🎯 Migração executada com sucesso!")
        print("⚠️ IMPORTANTE: Atualize os CPFs dos pacientes existentes manualmente!")
        print("⚠️ Os CPFs temporários (00000000000) devem ser alterados")
    else:
        print("\n❌ Falha na migração!")
        print("💡 Verifique os logs acima para identificar o problema")
