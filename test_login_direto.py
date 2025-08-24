#!/usr/bin/env python3
"""
Script para testar a lógica de login diretamente
"""

import re
from werkzeug.security import check_password_hash

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

def gerar_senha_inicial(cpf):
    """Gera senha inicial baseada nos 3 primeiros dígitos do CPF"""
    cpf_limpo = re.sub(r'[^0-9]', '', cpf)
    return cpf_limpo[:3]

def simular_login(cpf, senha):
    """Simula o processo de login"""
    print(f"🔐 Simulando login com CPF: {cpf}, Senha: {senha}")
    
    # Validações básicas
    if not cpf or not senha:
        print("❌ CPF e senha são obrigatórios")
        return False
    
    # Valida CPF
    if not validar_cpf(cpf):
        print("❌ CPF inválido")
        return False
    
    # Limpa CPF para busca no banco
    cpf_limpo = re.sub(r'[^0-9]', '', cpf)
    print(f"✅ CPF limpo: {cpf_limpo}")
    
    # Simula busca no banco (usuários padrão)
    usuarios_padrao = {
        '00000000000': {
            'nome': 'Administrador',
            'senha_hash': 'pbkdf2:sha256:600000$fz06gbe3bs2n94JV$c2d5a45d6a9b8d9bd3672133a9562f49dd493431d09e9e68bcc0e162feb1088e',
            'role': 'admin',
            'primeiro_acesso': False
        },
        '11111111111': {
            'nome': 'Recepção',
            'senha_hash': 'pbkdf2:sha256:600000$Kr3plnBvnppUQSZI$028949d038241aea49727e3ff0b760c4960455c1ba88b7939ef3c0f5f3383008',
            'role': 'recepcao',
            'primeiro_acesso': False
        },
        '22222222222': {
            'nome': 'Profissional',
            'senha_hash': 'pbkdf2:sha256:600000$agFOLsOavbFSEXhl$bd4dec813e342901208e1ed6592fe1662392ceeb50e3d6aa9286970298de401e',
            'role': 'profissional',
            'primeiro_acesso': False
        },
        '99999999999': {
            'nome': 'Desenvolvedor',
            'senha_hash': 'pbkdf2:sha256:600000$8hcOkm2VGtamodMN$d4340940ca64ba70acee6beb62d4b21e9ce8d75d7c6efcd03771c3819a27d6e7',
            'role': 'admin',
            'primeiro_acesso': False
        }
    }
    
    # Busca usuário pelo CPF
    user = usuarios_padrao.get(cpf_limpo)
    
    if not user:
        print(f"❌ CPF {cpf_limpo} não cadastrado no sistema")
        return False
    
    print(f"✅ Usuário encontrado: {user['nome']} ({user['role']})")
    print(f"   Primeiro acesso: {'Sim' if user['primeiro_acesso'] else 'Não'}")
    
    # Verifica se é primeiro acesso
    if user['primeiro_acesso']:
        # Para primeiro acesso, senha deve ser os 3 primeiros dígitos do CPF
        senha_inicial = gerar_senha_inicial(cpf_limpo)
        print(f"🔑 Senha inicial esperada: {senha_inicial}")
        
        if senha == senha_inicial:
            print("✅ Primeiro login bem-sucedido! Redirecionaria para troca de senha")
            return True
        else:
            print(f"❌ Senha inicial incorreta. Use os 3 primeiros dígitos do seu CPF: {senha_inicial}")
            return False
    else:
        # Login normal
        print(f"🔐 Verificando senha hash...")
        print(f"   Hash no banco: {user['senha_hash'][:50]}...")
        
        if check_password_hash(user['senha_hash'], senha):
            print("✅ Login bem-sucedido! Redirecionaria para dashboard")
            return True
        else:
            print("❌ Senha incorreta")
            return False

def testar_todos_usuarios():
    """Testa login com todos os usuários padrão"""
    print("🧪 Testando Login com Todos os Usuários Padrão")
    print("=" * 60)
    
    # Testa cada usuário padrão
    testes = [
        ('00000000000', '000', 'Administrador'),
        ('11111111111', '111', 'Recepção'),
        ('22222222222', '222', 'Profissional'),
        ('99999999999', '999', 'Desenvolvedor')
    ]
    
    for cpf, senha, nome in testes:
        print(f"\n👤 Testando {nome}:")
        print("-" * 40)
        resultado = simular_login(cpf, senha)
        print(f"Resultado: {'✅ SUCESSO' if resultado else '❌ FALHOU'}")
    
    print("\n" + "=" * 60)
    print("✅ Testes concluídos!")

if __name__ == "__main__":
    testar_todos_usuarios()
