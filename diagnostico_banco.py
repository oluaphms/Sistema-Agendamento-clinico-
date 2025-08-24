#!/usr/bin/env python3
"""
Diagnóstico da estrutura do banco de dados
Verifica a estrutura real das tabelas para identificar problemas
"""

import sqlite3
import os

def diagnosticar_banco():
    """Diagnostica a estrutura do banco de dados"""
    
    db_path = 'instance/clinica.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado em: {db_path}")
        return
    
    print("🔍 Diagnosticando estrutura do banco de dados...")
    print(f"📁 Caminho: {db_path}")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"📊 Tabelas encontradas: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        
        print("\n" + "=" * 60)
        
        # Verificar estrutura da tabela usuario
        if ('usuario',) in tables:
            print("👥 ESTRUTURA DA TABELA 'usuario':")
            cursor.execute("PRAGMA table_info(usuario)")
            columns = cursor.fetchall()
            
            for col in columns:
                print(f"   {col[1]} ({col[2]}) - Nullable: {col[3]} - Default: {col[4]}")
            
            # Verificar dados de exemplo
            cursor.execute("SELECT * FROM usuario LIMIT 3")
            users = cursor.fetchall()
            print(f"\n📋 Dados de exemplo (máx 3):")
            for user in users:
                print(f"   {user}")
                
        else:
            print("❌ Tabela 'usuario' não encontrada!")
        
        print("\n" + "=" * 60)
        
        # Verificar estrutura da tabela agendamento
        if ('agendamento',) in tables:
            print("📅 ESTRUTURA DA TABELA 'agendamento':")
            cursor.execute("PRAGMA table_info(agendamento)")
            columns = cursor.fetchall()
            
            for col in columns:
                print(f"   {col[1]} ({col[2]}) - Nullable: {col[3]} - Default: {col[4]}")
            
            # Verificar dados de exemplo
            cursor.execute("SELECT * FROM agendamento LIMIT 3")
            appointments = cursor.fetchall()
            print(f"\n📋 Dados de exemplo (máx 3):")
            for appt in appointments:
                print(f"   {appt}")
                
        else:
            print("❌ Tabela 'agendamento' não encontrada!")
        
        print("\n" + "=" * 60)
        
        # Verificar estrutura da tabela paciente
        if ('paciente',) in tables:
            print("🏥 ESTRUTURA DA TABELA 'paciente':")
            cursor.execute("PRAGMA table_info(paciente)")
            columns = cursor.fetchall()
            
            for col in columns:
                print(f"   {col[1]} ({col[2]}) - Nullable: {col[3]} - Default: {col[4]}")
                
        else:
            print("❌ Tabela 'paciente' não encontrada!")
        
        print("\n" + "=" * 60)
        
        # Verificar estrutura da tabela profissional
        if ('profissional',) in tables:
            print("👨‍⚕️ ESTRUTURA DA TABELA 'profissional':")
            cursor.execute("PRAGMA table_info(profissional)")
            columns = cursor.fetchall()
            
            for col in columns:
                print(f"   {col[1]} ({col[2]}) - Nullable: {col[3]} - Default: {col[4]}")
                
        else:
            print("❌ Tabela 'profissional' não encontrada!")
        
        print("\n" + "=" * 60)
        
        # Verificar estrutura da tabela servico
        if ('servico',) in tables:
            print("🔧 ESTRUTURA DA TABELA 'servico':")
            cursor.execute("PRAGMA table_info(servico)")
            columns = cursor.fetchall()
            
            for col in columns:
                print(f"   {col[1]} ({col[2]}) - Nullable: {col[3]} - Default: {col[4]}")
                
        else:
            print("❌ Tabela 'servico' não encontrada!")
        
        print("\n" + "=" * 60)
        
        # Testar consultas problemáticas
        print("🧪 TESTANDO CONSULTAS PROBLEMÁTICAS:")
        
        try:
            # Testar contagem de usuários por role
            cursor.execute("SELECT role, COUNT(*) FROM usuario GROUP BY role")
            role_counts = cursor.fetchall()
            print("✅ Contagem por role:")
            for role, count in role_counts:
                print(f"   {role}: {count}")
        except Exception as e:
            print(f"❌ Erro na contagem por role: {e}")
        
        try:
            # Testar contagem de agendamentos por status
            cursor.execute("SELECT status, COUNT(*) FROM agendamento GROUP BY status")
            status_counts = cursor.fetchall()
            print("✅ Contagem por status:")
            for status, count in status_counts:
                print(f"   {status}: {count}")
        except Exception as e:
            print(f"❌ Erro na contagem por status: {e}")
        
        try:
            # Testar contagem de agendamentos por data
            cursor.execute("SELECT COUNT(*) FROM agendamento WHERE DATE(data_hora) = DATE('now')")
            today_count = cursor.fetchone()[0]
            print(f"✅ Agendamentos hoje: {today_count}")
        except Exception as e:
            print(f"❌ Erro na contagem por data: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")

if __name__ == "__main__":
    diagnosticar_banco()
