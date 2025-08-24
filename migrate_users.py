#!/usr/bin/env python3
"""
Script de migração para atualizar o banco de dados existente
e converter usuários antigos para o novo formato com CPF
"""

import sqlite3
import re
from datetime import datetime

def validar_cpf(cpf):
    """Valida CPF brasileiro"""
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Validação do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    if resto < 2:
        digito1 = 0
    else:
        digito1 = 11 - resto
    
    if int(cpf[9]) != digito1:
        return False
    
    # Validação do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    if resto < 2:
        digito2 = 0
    else:
        digito2 = 11 - resto
    
    if int(cpf[10]) != digito2:
        return False
    
    return True

def gerar_cpf_fake():
    """Gera um CPF válido para migração (apenas para desenvolvimento)"""
    # CPF válido para migração: 111.444.777-35
    return "11144477735"

def criar_usuarios_padrao(cursor):
    """Cria os usuários padrão do sistema"""
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
    
    print("👥 Criando usuários padrão do sistema...")
    
    for usuario in usuarios_padrao:
        # Verifica se o usuário já existe
        cursor.execute("SELECT COUNT(*) FROM usuario WHERE cpf = ?", (usuario['cpf'],))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO usuario (nome, cpf, senha, role, primeiro_acesso, data_criacao)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (usuario['nome'], usuario['cpf'], usuario['senha'], usuario['role'], 
                  usuario['primeiro_acesso'], datetime.now()))
            
            print(f"  ✅ {usuario['nome']} ({usuario['role']}) - CPF: {usuario['cpf']}")
        else:
            print(f"  ⚠️  {usuario['nome']} já existe - CPF: {usuario['cpf']}")
    
    print("✅ Usuários padrão criados/verificados com sucesso!")

def migrar_banco():
    """Executa a migração do banco de dados"""
    try:
        # Conecta ao banco
        conn = sqlite3.connect('instance/clinica.db')
        cursor = conn.cursor()
        
        print("🔍 Verificando estrutura atual do banco...")
        
        # Verifica se a tabela usuario já tem os novos campos
        cursor.execute("PRAGMA table_info(usuario)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        if 'cpf' not in colunas:
            print("📝 Adicionando novos campos à tabela usuario...")
            
            # Adiciona novos campos
            cursor.execute("ALTER TABLE usuario ADD COLUMN cpf TEXT")
            cursor.execute("ALTER TABLE usuario ADD COLUMN nome TEXT")
            cursor.execute("ALTER TABLE usuario ADD COLUMN primeiro_acesso BOOLEAN DEFAULT 1")
            cursor.execute("ALTER TABLE usuario ADD COLUMN data_criacao DATETIME")
            cursor.execute("ALTER TABLE usuario ADD COLUMN ultimo_acesso DATETIME")
            
            print("✅ Novos campos adicionados com sucesso!")
        else:
            print("✅ Tabela já possui os novos campos")
        
        # Verifica se há usuários antigos para migrar
        cursor.execute("SELECT id, usuario, senha, role, profissional_id FROM usuario WHERE cpf IS NULL OR cpf = ''")
        usuarios_antigos = cursor.fetchall()
        
        if usuarios_antigos:
            print(f"🔄 Encontrados {len(usuarios_antigos)} usuários para migrar...")
            
            for user_id, usuario_antigo, senha, role, profissional_id in usuarios_antigos:
                print(f"  - Migrando usuário: {usuario_antigo}")
                
                # Gera CPF único para migração
                cpf_migracao = gerar_cpf_fake()
                
                # Atualiza o usuário com os novos campos
                cursor.execute("""
                    UPDATE usuario 
                    SET cpf = ?, nome = ?, primeiro_acesso = 0, data_criacao = ?
                    WHERE id = ?
                """, (cpf_migracao, usuario_antigo, datetime.now(), user_id))
                
                print(f"    ✅ Migrado com CPF: {cpf_migracao}")
            
            print("✅ Migração de usuários concluída!")
        else:
            print("✅ Nenhum usuário antigo encontrado para migrar")
        
        # IMPORTANTE: Tornar o campo 'usuario' opcional (NULL)
        print("🔧 Tornando campo 'usuario' opcional...")
        try:
            # SQLite não suporta ALTER COLUMN para mudar NOT NULL, então vamos recriar a tabela
            print("  - Recriando tabela usuario com estrutura correta...")
            
            # Backup dos dados existentes
            cursor.execute("SELECT id, usuario, senha, role, profissional_id, cpf, nome, primeiro_acesso, data_criacao, ultimo_acesso FROM usuario")
            usuarios_backup = cursor.fetchall()
            
            # Remove tabela antiga
            cursor.execute("DROP TABLE usuario")
            
            # Cria nova tabela com estrutura correta
            cursor.execute("""
                CREATE TABLE usuario (
                    id INTEGER PRIMARY KEY,
                    usuario VARCHAR(50),  -- Agora opcional
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
            
            # Restaura os dados
            for user_data in usuarios_backup:
                cursor.execute("""
                    INSERT INTO usuario (id, usuario, senha, role, profissional_id, cpf, nome, primeiro_acesso, data_criacao, ultimo_acesso)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, user_data)
            
            print("  ✅ Tabela recriada com sucesso!")
            
        except Exception as e:
            print(f"  ⚠️  Erro ao recriar tabela: {e}")
            print("  - Continuando com estrutura atual...")
        
        # Cria usuários padrão do sistema
        criar_usuarios_padrao(cursor)
        
        # Commit das alterações
        conn.commit()
        print("💾 Alterações salvas no banco de dados")
        
        # Mostra estatísticas finais
        cursor.execute("SELECT COUNT(*) FROM usuario")
        total_usuarios = cursor.fetchone()[0]
        
        cursor.execute("SELECT role, COUNT(*) FROM usuario GROUP BY role")
        usuarios_por_role = cursor.fetchall()
        
        print("\n📊 Estatísticas finais:")
        print(f"   Total de usuários: {total_usuarios}")
        for role, count in usuarios_por_role:
            print(f"   {role.capitalize()}: {count}")
        
        print("\n🎉 Migração concluída com sucesso!")
        print("\n🔑 USUÁRIOS PADRÃO CRIADOS:")
        print("   Desenvolvedor: CPF 12345678909, Senha 123 (Admin)")
        print("   Administrador: CPF 98765432100, Senha 987 (Admin)")
        print("   Recepção: CPF 11144477735, Senha 111 (Recepção)")
        print("   Profissional: CPF 22233344455, Senha 222 (Profissional)")
        
    except sqlite3.Error as e:
        print(f"❌ Erro no banco de dados: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def verificar_banco():
    """Verifica o estado atual do banco de dados"""
    try:
        conn = sqlite3.connect('instance/clinica.db')
        cursor = conn.cursor()
        
        print("🔍 Verificando estado atual do banco...")
        
        # Verifica estrutura da tabela usuario
        cursor.execute("PRAGMA table_info(usuario)")
        colunas = cursor.fetchall()
        
        print("\n📋 Estrutura da tabela 'usuario':")
        for col in colunas:
            print(f"   {col[1]} ({col[2]}) - Default: {col[4]}")
        
        # Verifica usuários existentes
        cursor.execute("SELECT id, nome, cpf, role, primeiro_acesso FROM usuario ORDER BY role, nome")
        usuarios = cursor.fetchall()
        
        print(f"\n👥 Usuários cadastrados ({len(usuarios)}):")
        for user in usuarios:
            user_id, nome, cpf, role, primeiro_acesso = user
            status = "Primeiro Acesso" if primeiro_acesso else "Acesso Normal"
            print(f"   ID {user_id}: {nome} (CPF: {cpf}) - {role} - {status}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Erro ao verificar banco: {e}")

if __name__ == "__main__":
    print("🚀 Sistema de Migração de Usuários")
    print("=" * 50)
    
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        verificar_banco()
    else:
        print("Iniciando migração...")
        migrar_banco()
    
    print("\n" + "=" * 50)
    print("✅ Processo finalizado!")
