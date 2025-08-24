#!/usr/bin/env python3
"""
Script de verificação automática de sincronização do banco de dados
Este script deve ser executado antes de iniciar a aplicação Flask
"""

import sqlite3
import os
import sys
from datetime import datetime

def check_database_sync():
    """Verifica se o banco está sincronizado e corrige automaticamente se necessário"""
    
    db_path = 'instance/clinica.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado em: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Verificando sincronização do banco de dados...")
        
        # Verificar tabela paciente (problema principal identificado)
        cursor.execute("PRAGMA table_info(paciente)")
        paciente_columns = [col[1] for col in cursor.fetchall()]
        
        required_columns = ['categoria', 'data_cadastro', 'ultima_atualizacao']
        missing_columns = [col for col in required_columns if col not in paciente_columns]
        
        if missing_columns:
            print(f"⚠️ Colunas faltando na tabela paciente: {missing_columns}")
            print("🔧 Corrigindo automaticamente...")
            
            # Adicionar colunas faltantes
            for col in missing_columns:
                try:
                    if col in ['data_cadastro', 'ultima_atualizacao']:
                        cursor.execute(f"ALTER TABLE paciente ADD COLUMN {col} DATETIME")
                    else:
                        cursor.execute(f"ALTER TABLE paciente ADD COLUMN {col} TEXT")
                    print(f"✅ Coluna {col} adicionada")
                except Exception as e:
                    print(f"ℹ️ Coluna {col}: {e}")
            
            # Atualizar registros existentes
            now = datetime.now().isoformat()
            cursor.execute("UPDATE paciente SET categoria = 'particular' WHERE categoria IS NULL")
            cursor.execute("UPDATE paciente SET data_cadastro = ? WHERE data_cadastro IS NULL", (now,))
            cursor.execute("UPDATE paciente SET ultima_atualizacao = ? WHERE ultima_atualizacao IS NULL", (now,))
            
            conn.commit()
            print("✅ Correções aplicadas com sucesso!")
        else:
            print("✅ Tabela paciente está sincronizada")
        
        # Verificar outras tabelas críticas
        tables_to_check = ['usuario', 'profissional', 'servico', 'agendamento']
        
        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if cursor.fetchone():
                    print(f"✅ Tabela {table} existe")
                else:
                    print(f"⚠️ Tabela {table} não existe - pode causar problemas")
            except Exception as e:
                print(f"⚠️ Erro ao verificar tabela {table}: {e}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro durante verificação: {e}")
        return False

def main():
    """Função principal que verifica e corrige o banco"""
    
    print("🚀 Verificação Automática de Sincronização do Banco")
    print("=" * 50)
    
    if check_database_sync():
        print("\n✅ Banco de dados verificado e corrigido com sucesso!")
        print("🚀 Aplicação pode ser iniciada com segurança")
        return True
    else:
        print("\n❌ Problemas encontrados no banco de dados!")
        print("💡 Verifique os logs acima e corrija manualmente se necessário")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
