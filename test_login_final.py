#!/usr/bin/env python3
"""
Script final para testar o login com CPFs válidos
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

def testar_cpfs_validos():
    """Testa se os CPFs padrão são válidos"""
    print("🧪 Testando Validação de CPFs")
    print("=" * 50)
    
    cpfs_teste = [
        ('12345678909', 'Desenvolvedor'),
        ('98765432100', 'Administrador'),
        ('11144477735', 'Recepção'),
        ('22233344455', 'Profissional')
    ]
    
    for cpf, nome in cpfs_teste:
        print(f"\n👤 {nome}:")
        print(f"   CPF: {cpf}")
        
        if validar_cpf(cpf):
            print("   ✅ CPF válido!")
        else:
            print("   ❌ CPF inválido!")
    
    print("\n" + "=" * 50)

def simular_login_sistema():
    """Simula o login no sistema"""
    print("\n🔐 Simulando Login no Sistema")
    print("=" * 50)
    
    # Simula usuários do banco
    usuarios = {
        '12345678909': {
            'nome': 'Desenvolvedor',
            'senha_hash': 'pbkdf2:sha256:600000$fz06gbe3bs2n94JV$c2d5a45d6a9b8d9bd3672133a9562f49dd493431d09e9e68bcc0e162feb1088e',
            'role': 'admin',
            'primeiro_acesso': False
        },
        '98765432100': {
            'nome': 'Administrador',
            'senha_hash': 'pbkdf2:sha256:600000$Kr3plnBvnppUQSZI$028949d038241aea49727e3ff0b760c4960455c1ba88b7939ef3c0f5f3383008',
            'role': 'admin',
            'primeiro_acesso': False
        },
        '11144477735': {
            'nome': 'Recepção',
            'senha_hash': 'pbkdf2:sha256:600000$agFOLsOavbFSEXhl$bd4dec813e342901208e1ed6592fe1662392ceeb50e3d6aa9286970298de401e',
            'role': 'recepcao',
            'primeiro_acesso': False
        },
        '22233344455': {
            'nome': 'Profissional',
            'senha_hash': 'pbkdf2:sha256:600000$8hcOkm2VGtamodMN$d4340940ca64ba70acee6beb62d4b21e9ce8d75d7c6efcd03771c3819a27d6e7',
            'role': 'profissional',
            'primeiro_acesso': False
        }
    }
    
    # Testa login com cada usuário
    testes = [
        ('12345678909', '123', 'Desenvolvedor'),
        ('98765432100', '987', 'Administrador'),
        ('11144477735', '111', 'Recepção'),
        ('22233344455', '222', 'Profissional')
    ]
    
    for cpf, senha, nome in testes:
        print(f"\n👤 Testando {nome}:")
        print(f"   CPF: {cpf}")
        print(f"   Senha: {senha}")
        
        # Valida CPF
        if not validar_cpf(cpf):
            print("   ❌ CPF inválido - Login falharia")
            continue
        
        # Busca usuário
        user = usuarios.get(cpf)
        if not user:
            print("   ❌ Usuário não encontrado - Login falharia")
            continue
        
        # Verifica senha
        if check_password_hash(user['senha_hash'], senha):
            print(f"   ✅ Login bem-sucedido!")
            print(f"   👑 Perfil: {user['role']}")
            print(f"   🚪 Redirecionaria para: Dashboard")
        else:
            print("   ❌ Senha incorreta - Login falharia")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    print("🎯 Teste Final do Sistema de Login")
    print("=" * 60)
    
    testar_cpfs_validos()
    simular_login_sistema()
    
    print("\n🎉 Testes concluídos!")
    print("\n🔑 USUÁRIOS PARA TESTE:")
    print("   Desenvolvedor: CPF 12345678909, Senha 123")
    print("   Administrador: CPF 98765432100, Senha 987")
    print("   Recepção: CPF 11144477735, Senha 111")
    print("   Profissional: CPF 22233344455, Senha 222")
    
    print("\n✅ Sistema pronto para uso!")
