#!/usr/bin/env python3
"""
Configuração dos usuários padrão do sistema
CPFs e senhas padrão para desenvolvimento e teste
"""

# Usuários padrão do sistema
USUARIOS_PADRAO = {
    'admin': {
        'cpf': '00000000000',
        'nome': 'Administrador',
        'senha': '000',
        'role': 'admin',
        'primeiro_acesso': True,
        'descricao': 'Usuário administrador principal do sistema com acesso total'
    },
    'recepcao': {
        'cpf': '11111111111',
        'nome': 'Recepção',
        'senha': '111',
        'role': 'recepcao',
        'primeiro_acesso': True,
        'descricao': 'Usuário de recepção com acesso operacional e administrativo básico'
    },
    'profissional': {
        'cpf': '22222222222',
        'nome': 'Profissional de Saúde',
        'senha': '222',
        'role': 'profissional',
        'primeiro_acesso': True,
        'descricao': 'Usuário profissional de saúde com acesso operacional específico'
    },
    'desenvolvedor': {
        'cpf': '33333333333',
        'nome': 'Desenvolvedor',
        'senha': '333',
        'role': 'admin',
        'primeiro_acesso': True,
        'descricao': 'Usuário com acesso total para desenvolvimento e testes'
    }
}

# Regras de acesso por perfil
REGRA_ACESSO = {
    'admin': {
        'descricao': 'Administrador',
        'permissoes': [
            'Gerenciar usuários (criar, editar, excluir)',
            'Acessar todas as funcionalidades',
            'Configurações do sistema',
            'Relatórios completos',
            'Backup e manutenção',
            'Gerenciar pacientes, profissionais e serviços',
            'Visualizar e gerenciar agendamentos',
            'Acessar analytics e relatórios'
        ],
        'cor': 'danger',
        'icone': 'shield-fill'
    },
    'recepcao': {
        'descricao': 'Recepção',
        'permissoes': [
            'Gerenciar pacientes',
            'Criar e gerenciar agendamentos',
            'Cadastrar e gerenciar serviços',
            'Relatórios básicos',
            'Atendimento ao cliente'
        ],
        'cor': 'primary',
        'icone': 'person-badge'
    },
    'profissional': {
        'descricao': 'Profissional de Saúde',
        'permissoes': [
            'Visualizar agenda pessoal',
            'Gerenciar prontuários',
            'Relatórios de atendimento',
            'Histórico de pacientes',
            'Atualizar status de consultas'
        ],
        'cor': 'success',
        'icone': 'heart-pulse'
    }
}

# Configurações de primeiro acesso
PRIMEIRO_ACESSO_CONFIG = {
    'senha_minima': 6,
    'forca_senha': {
        'minima': 'Mínimo 6 caracteres',
        'recomendada': 'Recomendado: letras + números + símbolos',
        'forte': 'Forte: 8+ caracteres com variação'
    },
    'mensagem_boas_vindas': 'Bem-vindo ao sistema! Por segurança, você deve alterar sua senha no primeiro acesso.',
    'regras_senha_inicial': {
        'descricao': 'Senha inicial: sempre os 3 primeiros dígitos do CPF',
        'exemplo': 'CPF 12345678900 → Senha inicial: 123',
        'obrigatorio_alterar': 'Usuário é obrigado a alterar a senha no primeiro acesso'
    }
}

# Validações específicas por perfil
VALIDACOES_PERFIL = {
    'admin': {
        'pode_criar_usuarios': True,
        'pode_deletar_usuarios': True,
        'pode_alterar_permissoes': True,
        'acesso_total': True,
        'pode_gerenciar_sistema': True,
        'pode_acessar_analytics': True,
        'pode_fazer_backup': True
    },
    'recepcao': {
        'pode_criar_usuarios': False,
        'pode_deletar_usuarios': False,
        'pode_alterar_permissoes': False,
        'acesso_total': False,
        'pode_gerenciar_sistema': False,
        'pode_acessar_analytics': False,
        'pode_fazer_backup': False,
        'pode_gerenciar_pacientes': True,
        'pode_gerenciar_agendamentos': True,
        'pode_gerenciar_servicos': True
    },
    'profissional': {
        'pode_criar_usuarios': False,
        'pode_deletar_usuarios': False,
        'pode_alterar_permissoes': False,
        'acesso_total': False,
        'pode_gerenciar_sistema': False,
        'pode_acessar_analytics': False,
        'pode_fazer_backup': False,
        'pode_criar_pacientes': False,
        'pode_visualizar_agenda_pessoal': True,
        'pode_gerenciar_prontuarios': True,
        'pode_atualizar_consultas': True
    }
}

def obter_usuario_padrao(perfil):
    """Retorna as informações do usuário padrão para um perfil específico"""
    return USUARIOS_PADRAO.get(perfil, None)

def obter_regra_acesso(role):
    """Retorna as regras de acesso para um perfil específico"""
    return REGRA_ACESSO.get(role, {})

def obter_validacoes_perfil(role):
    """Retorna as validações específicas para um perfil"""
    return VALIDACOES_PERFIL.get(role, {})

def listar_usuarios_padrao():
    """Lista todos os usuários padrão disponíveis"""
    return USUARIOS_PADRAO

def verificar_perfil_valido(role):
    """Verifica se um perfil é válido"""
    return role in REGRA_ACESSO

if __name__ == "__main__":
    print("🔧 Configuração dos Usuários Padrão do Sistema")
    print("=" * 60)
    print("📋 Seguindo padrão do README_SISTEMA_ACESSO.md")
    print("=" * 60)
    
    for perfil, dados in USUARIOS_PADRAO.items():
        print(f"\n👤 {dados['nome']} ({perfil.upper()})")
        print(f"   CPF: {dados['cpf']}")
        print(f"   Senha Inicial: {dados['senha']} (3 primeiros dígitos do CPF)")
        print(f"   Perfil: {dados['role']}")
        print(f"   Primeiro Acesso: {'Sim' if dados['primeiro_acesso'] else 'Não'}")
        print(f"   Descrição: {dados['descricao']}")
    
    print("\n" + "=" * 60)
    print("🔑 Sistema de Primeiro Acesso:")
    print("   • Senha inicial: 3 primeiros dígitos do CPF")
    print("   • Usuário obrigado a alterar senha no primeiro acesso")
    print("   • Senha mínima: 6 caracteres")
    print("=" * 60)
    print("✅ Configuração carregada com sucesso!")
    print("🎯 Sistema segue padrão do README_SISTEMA_ACESSO.md")
