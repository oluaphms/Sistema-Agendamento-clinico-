#!/usr/bin/env python3
"""
Script de teste para verificar se o dashboard está funcionando após as correções
"""

import sqlite3
import os
from datetime import datetime

def test_dashboard_query():
    """Testa a query que estava causando o erro no dashboard"""
    
    db_path = 'instance/clinica.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado em: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🧪 Testando query do dashboard...")
        
        # Simular a query que estava causando erro
        hoje = datetime.now().strftime("%Y-%m-%d")
        
        query = """
        SELECT 
            agendamento.id AS agendamento_id,
            agendamento.paciente_id AS agendamento_paciente_id,
            agendamento.profissional_id AS agendamento_profissional_id,
            agendamento.servico_id AS agendamento_servico_id,
            agendamento.data AS agendamento_data,
            agendamento.hora AS agendamento_hora,
            agendamento.duracao AS agendamento_duracao,
            agendamento.status AS agendamento_status,
            agendamento.observacoes AS agendamento_observacoes,
            agendamento.origem AS agendamento_origem,
            agendamento.valor_pago AS agendamento_valor_pago,
            paciente.id AS paciente_id,
            paciente.nome AS paciente_nome,
            paciente.cpf AS paciente_cpf,
            paciente.telefone AS paciente_telefone,
            paciente.email AS paciente_email,
            paciente.data_nascimento AS paciente_data_nascimento,
            paciente.observacoes AS paciente_observacoes,
            paciente.convenio AS paciente_convenio,
            paciente.categoria AS paciente_categoria,
            paciente.data_cadastro AS paciente_data_cadastro,
            paciente.ultima_atualizacao AS paciente_ultima_atualizacao,
            profissional.id AS profissional_id,
            profissional.nome AS profissional_nome,
            profissional.especialidade AS profissional_especialidade,
            profissional.telefone AS profissional_telefone,
            profissional.email AS profissional_email,
            profissional.horarios AS profissional_horarios,
            servico.id AS servico_id,
            servico.nome AS servico_nome,
            servico.duracao_min AS servico_duracao_min,
            servico.preco AS servico_preco
        FROM agendamento 
        LEFT OUTER JOIN paciente ON paciente.id = agendamento.paciente_id 
        LEFT OUTER JOIN profissional ON profissional.id = agendamento.profissional_id 
        LEFT OUTER JOIN servico ON servico.id = agendamento.servico_id 
        WHERE agendamento.data = ?
        ORDER BY agendamento.hora ASC
        """
        
        try:
            cursor.execute(query, (hoje,))
            results = cursor.fetchall()
            print(f"✅ Query executada com sucesso! Resultados: {len(results)}")
            
            if results:
                print("📋 Primeiro resultado:")
                for i, col in enumerate(cursor.description):
                    print(f"  {col[0]}: {results[0][i]}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro na query: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return False
        
    finally:
        if conn:
            conn.close()

def test_patient_table():
    """Testa se a tabela paciente tem todas as colunas necessárias"""
    
    db_path = 'instance/clinica.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔍 Verificando estrutura da tabela paciente...")
        
        cursor.execute("PRAGMA table_info(paciente)")
        columns = [col[1] for col in cursor.fetchall()]
        
        required_columns = ['categoria', 'data_cadastro', 'ultima_atualizacao']
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            print(f"❌ Colunas faltando: {missing_columns}")
            return False
        else:
            print("✅ Todas as colunas necessárias estão presentes")
            print(f"📋 Colunas: {columns}")
            return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar tabela: {e}")
        return False
        
    finally:
        if conn:
            conn.close()

def main():
    """Função principal de teste"""
    
    print("🚀 Teste de Correção do Dashboard")
    print("=" * 40)
    
    # Testar estrutura da tabela
    table_ok = test_patient_table()
    
    # Testar query do dashboard
    query_ok = test_dashboard_query()
    
    print("\n" + "=" * 40)
    
    if table_ok and query_ok:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Dashboard deve estar funcionando corretamente")
        print("✅ Erro de coluna 'categoria' foi corrigido")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        if not table_ok:
            print("❌ Problema na estrutura da tabela paciente")
        if not query_ok:
            print("❌ Problema na query do dashboard")
    
    return table_ok and query_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
