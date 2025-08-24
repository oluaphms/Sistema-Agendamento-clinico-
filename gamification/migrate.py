"""
Script de Migração - Sistema de Gamificação
Cria as tabelas necessárias no banco de dados
"""

import os
import sys
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from gamification.models import *

def create_gamification_tables():
    """Cria todas as tabelas de gamificação"""
    try:
        print("🚀 Iniciando migração do sistema de gamificação...")
        
        # Cria a aplicação Flask
        app = create_app()
        
        with app.app_context():
            # Cria todas as tabelas
            db.create_all()
            
            print("✅ Tabelas criadas com sucesso!")
            
            # Verifica se as tabelas foram criadas
            tables = [
                'user_points',
                'points_transactions', 
                'badges',
                'user_badges',
                'achievements',
                'leaderboards',
                'gamification_events'
            ]
            
            for table in tables:
                try:
                    result = db.engine.execute(f"SELECT COUNT(*) FROM {table}")
                    count = result.scalar()
                    print(f"   📊 Tabela {table}: {count} registros")
                except Exception as e:
                    print(f"   ❌ Erro ao verificar tabela {table}: {str(e)}")
            
            print("\n🎉 Migração concluída com sucesso!")
            
    except Exception as e:
        print(f"❌ Erro durante a migração: {str(e)}")
        return False
    
    return True

def create_sample_data():
    """Cria dados de exemplo para teste"""
    try:
        print("\n🔧 Criando dados de exemplo...")
        
        app = create_app()
        
        with app.app_context():
            # Verifica se já existem badges
            if Badge.query.count() == 0:
                # Cria badges padrão
                badges_data = [
                    # Badges para Pacientes
                    {
                        'code': 'paciente_pontual',
                        'name': 'Paciente Pontual',
                        'description': '5 consultas seguidas sem faltas',
                        'icon': '⏰',
                        'category': 'attendance',
                        'user_type': 'patient',
                        'requirement_type': 'streak',
                        'requirement_value': 5,
                        'points_reward': 100,
                        'color': 'success',
                        'rarity': 'rare'
                    },
                    {
                        'code': 'paciente_fiel',
                        'name': 'Paciente Fiel',
                        'description': '10 consultas realizadas',
                        'icon': '👑',
                        'category': 'loyalty',
                        'user_type': 'patient',
                        'requirement_type': 'count',
                        'requirement_value': 10,
                        'points_reward': 200,
                        'color': 'primary',
                        'rarity': 'epic'
                    },
                    {
                        'code': 'zero_faltas',
                        'name': 'Zero Faltas',
                        'description': '30 dias sem ausências',
                        'icon': '🎯',
                        'category': 'attendance',
                        'user_type': 'patient',
                        'requirement_type': 'days',
                        'requirement_value': 30,
                        'points_reward': 300,
                        'color': 'warning',
                        'rarity': 'legendary'
                    },
                    # Badges para Profissionais
                    {
                        'code': 'top_mes',
                        'name': 'Top do Mês',
                        'description': 'Profissional com maior receita mensal',
                        'icon': '🏆',
                        'category': 'performance',
                        'user_type': 'professional',
                        'requirement_type': 'ranking',
                        'requirement_value': 1,
                        'points_reward': 500,
                        'color': 'warning',
                        'rarity': 'epic'
                    },
                    {
                        'code': 'super_agenda',
                        'name': 'Super Agenda',
                        'description': 'Profissional com mais consultas realizadas',
                        'icon': '📅',
                        'category': 'productivity',
                        'user_type': 'professional',
                        'requirement_type': 'count',
                        'requirement_value': 50,
                        'points_reward': 400,
                        'color': 'primary',
                        'rarity': 'rare'
                    }
                ]
                
                for badge_data in badges_data:
                    badge = Badge(**badge_data)
                    db.session.add(badge)
                
                db.session.commit()
                print("✅ Badges de exemplo criados com sucesso!")
            else:
                print("ℹ️  Badges já existem, pulando criação...")
            
            print("🎯 Dados de exemplo criados com sucesso!")
            
    except Exception as e:
        print(f"❌ Erro ao criar dados de exemplo: {str(e)}")
        return False
    
    return True

def verify_migration():
    """Verifica se a migração foi bem-sucedida"""
    try:
        print("\n🔍 Verificando migração...")
        
        app = create_app()
        
        with app.app_context():
            # Verifica se todas as tabelas existem
            tables = [
                UserPoints,
                PointsTransaction,
                Badge,
                UserBadge,
                Achievement,
                Leaderboard,
                GamificationEvent
            ]
            
            all_tables_exist = True
            
            for table in tables:
                try:
                    count = table.query.count()
                    print(f"   ✅ {table.__name__}: {count} registros")
                except Exception as e:
                    print(f"   ❌ {table.__name__}: Erro - {str(e)}")
                    all_tables_exist = False
            
            if all_tables_exist:
                print("\n🎉 Verificação concluída! Todas as tabelas estão funcionando.")
                return True
            else:
                print("\n⚠️  Verificação falhou! Algumas tabelas não estão funcionando.")
                return False
                
    except Exception as e:
        print(f"❌ Erro durante verificação: {str(e)}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("🏆 SISTEMA DE GAMIFICAÇÃO - SCRIPT DE MIGRAÇÃO")
    print("=" * 60)
    
    # Cria as tabelas
    if not create_gamification_tables():
        print("❌ Falha na criação das tabelas!")
        return
    
    # Cria dados de exemplo
    if not create_sample_data():
        print("❌ Falha na criação dos dados de exemplo!")
        return
    
    # Verifica a migração
    if not verify_migration():
        print("❌ Falha na verificação da migração!")
        return
    
    print("\n" + "=" * 60)
    print("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print("\n📋 Próximos passos:")
    print("   1. Verifique se o blueprint de gamificação está registrado na aplicação")
    print("   2. Teste as rotas de gamificação")
    print("   3. Configure as notificações WhatsApp se necessário")
    print("   4. Personalize os badges e regras conforme necessário")
    print("\n🚀 O sistema de gamificação está pronto para uso!")

if __name__ == "__main__":
    main()
