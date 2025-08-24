#!/usr/bin/env python3
"""
Script para verificar se todas as tabelas do banco de dados estão sincronizadas
com os modelos SQLAlchemy definidos no app.py
"""

import sqlite3
import os
from datetime import datetime

def get_model_columns():
    """Retorna as colunas esperadas para cada modelo baseado no app.py"""
    return {
        'usuario': [
            'id', 'nome', 'cpf', 'senha', 'role', 'profissional_id', 
            'primeiro_acesso', 'data_criacao', 'ultimo_acesso'
        ],
        'paciente': [
            'id', 'nome', 'cpf', 'telefone', 'email', 'data_nascimento', 
            'observacoes', 'convenio', 'categoria', 'data_cadastro', 'ultima_atualizacao'
        ],
        'profissional': [
            'id', 'nome', 'especialidade', 'telefone', 'email', 'horarios'
        ],
        'servico': [
            'id', 'nome', 'duracao_min', 'preco'
        ],
        'agendamento': [
            'id', 'paciente_id', 'profissional_id', 'servico_id', 'data', 
            'hora', 'duracao', 'status', 'observacoes', 'origem', 'valor_pago'
        ],
        'prontuario': [
            'id', 'paciente_id', 'data', 'anotacao'
        ]
    }

def verify_table_structure():
    """Verifica se todas as tabelas têm as colunas corretas"""
    
    db_path = 'instance/clinica.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado em: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Verificando sincronização do banco de dados...")
        print("=" * 60)
        
        expected_columns = get_model_columns()
        all_synced = True
        
        for table_name, expected_cols in expected_columns.items():
            print(f"\n📋 Verificando tabela: {table_name.upper()}")
            
            # Verificar se a tabela existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cursor.fetchone():
                print(f"❌ Tabela '{table_name}' não existe!")
                all_synced = False
                continue
            
            # Obter colunas atuais
            cursor.execute(f"PRAGMA table_info({table_name})")
            current_columns = [col[1] for col in cursor.fetchall()]
            
            # Verificar colunas faltantes
            missing_columns = [col for col in expected_cols if col not in current_columns]
            extra_columns = [col for col in current_columns if col not in expected_cols]
            
            if missing_columns:
                print(f"❌ Colunas faltando: {missing_columns}")
                all_synced = False
            else:
                print(f"✅ Todas as colunas esperadas estão presentes")
            
            if extra_columns:
                print(f"⚠️ Colunas extras (não críticas): {extra_columns}")
            
            print(f"📊 Colunas atuais: {current_columns}")
        
        print("\n" + "=" * 60)
        
        if all_synced:
            print("🎉 Todas as tabelas estão sincronizadas com os modelos!")
        else:
            print("❌ Algumas tabelas precisam ser atualizadas!")
            print("💡 Execute os scripts de migração apropriados")
        
        return all_synced
        
    except Exception as e:
        print(f"❌ Erro durante a verificação: {e}")
        return False
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🚀 Verificador de Sincronização do Banco de Dados")
    print("=" * 60)
    
    # Verificar estrutura atual
    is_synced = verify_table_structure()
    
    print("\n🔍 Verificação concluída!")
