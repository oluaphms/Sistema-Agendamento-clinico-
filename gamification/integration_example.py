"""
Exemplo de Integração - Sistema de Gamificação
Mostra como integrar o sistema de gamificação com funcionalidades existentes
"""

from gamification.services import GamificationService
from app import db

class GamificationIntegration:
    """Classe de exemplo para integração com sistema existente"""
    
    def __init__(self):
        self.gamification_service = GamificationService(db)
    
    def handle_appointment_confirmation(self, user_id, appointment_id):
        """
        Exemplo: Integração com confirmação de agendamento
        """
        try:
            # Lógica existente de confirmação
            # ... código do sistema existente ...
            
            # Integração com gamificação
            result = self.gamification_service.handle_appointment_action(
                user_id=user_id,
                user_type='patient',
                action='confirm_presence',
                appointment_data={
                    'appointment_id': appointment_id,
                    'specialty': 'cardiology',
                    'date': '2024-01-15'
                }
            )
            
            if result.get('success'):
                print(f"✅ Pontos concedidos: {result['points_awarded']}")
                
                if result.get('new_badges'):
                    print(f"🏆 Novos badges desbloqueados: {len(result['new_badges'])}")
                    
                if result.get('level_up'):
                    print(f"⬆️ Usuário subiu de nível!")
            else:
                print(f"❌ Erro na gamificação: {result.get('error')}")
                
        except Exception as e:
            print(f"Erro na integração: {str(e)}")
    
    def handle_appointment_attendance(self, user_id, appointment_id, attended=True):
        """
        Exemplo: Integração com comparecimento à consulta
        """
        try:
            if attended:
                # Paciente compareceu
                action = 'attend_appointment'
                message = "Paciente compareceu à consulta"
            else:
                # Paciente faltou
                action = 'miss_appointment'
                message = "Paciente faltou à consulta"
            
            # Integração com gamificação
            result = self.gamification_service.handle_appointment_action(
                user_id=user_id,
                user_type='patient',
                action=action,
                appointment_data={
                    'appointment_id': appointment_id,
                    'attended': attended,
                    'date': '2024-01-15'
                }
            )
            
            if result.get('success'):
                points = result['points_awarded']
                if points > 0:
                    print(f"✅ {message}: +{points} pontos")
                else:
                    print(f"⚠️ {message}: {points} pontos")
            else:
                print(f"❌ Erro na gamificação: {result.get('error')}")
                
        except Exception as e:
            print(f"Erro na integração: {str(e)}")
    
    def handle_appointment_reschedule(self, user_id, appointment_id, days_in_advance):
        """
        Exemplo: Integração com reagendamento antecipado
        """
        try:
            # Verifica se é reagendamento antecipado (mais de 24h)
            if days_in_advance >= 1:
                result = self.gamification_service.handle_appointment_action(
                    user_id=user_id,
                    user_type='patient',
                    action='reschedule_advance',
                    appointment_data={
                        'appointment_id': appointment_id,
                        'days_in_advance': days_in_advance,
                        'date': '2024-01-15'
                    }
                )
                
                if result.get('success'):
                    points = result['points_awarded']
                    print(f"✅ Reagendamento antecipado: +{points} pontos")
                    
        except Exception as e:
            print(f"Erro na integração: {str(e)}")
    
    def handle_professional_completion(self, user_id, appointments_completed, absence_rate):
        """
        Exemplo: Integração com conclusão de consultas por profissional
        """
        try:
            # Concede pontos por consultas realizadas
            result = self.gamification_service.handle_appointment_action(
                user_id=user_id,
                user_type='professional',
                action='complete_appointment',
                appointment_data={
                    'appointments_completed': appointments_completed,
                    'absence_rate': absence_rate,
                    'month': '2024-01'
                }
            )
            
            if result.get('success'):
                points = result['points_awarded']
                print(f"✅ Profissional completou consultas: +{points} pontos")
                
                # Verifica se merece bônus por baixa taxa de faltas
                if absence_rate < 0.05:  # Menos de 5%
                    bonus_result = self.gamification_service.handle_appointment_action(
                        user_id=user_id,
                        user_type='professional',
                        action='low_absence_rate',
                        appointment_data={
                            'absence_rate': absence_rate,
                            'month': '2024-01'
                        }
                    )
                    
                    if bonus_result.get('success'):
                        bonus_points = bonus_result['points_awarded']
                        print(f"🎯 Bônus por baixa taxa de faltas: +{bonus_points} pontos")
                        
        except Exception as e:
            print(f"Erro na integração: {str(e)}")
    
    def get_user_gamification_summary(self, user_id, user_type):
        """
        Exemplo: Obter resumo de gamificação para exibir em outras páginas
        """
        try:
            profile = self.gamification_service.get_user_gamification_profile(
                user_id, user_type
            )
            
            if 'error' not in profile:
                summary = {
                    'level': profile['level'],
                    'total_points': profile['total_points'],
                    'badges_count': len(profile['badges']),
                    'ranking_position': profile['ranking']['position'],
                    'next_badge': profile['next_badges'][0] if profile['next_badges'] else None
                }
                
                return summary
            else:
                return None
                
        except Exception as e:
            print(f"Erro ao obter resumo: {str(e)}")
            return None
    
    def display_gamification_widget(self, user_id, user_type):
        """
        Exemplo: Widget de gamificação para exibir em outras páginas
        """
        summary = self.get_user_gamification_summary(user_id, user_type)
        
        if summary:
            widget_html = f"""
            <div class="gamification-widget">
                <div class="widget-header">
                    <h5>🏆 Meu Progresso</h5>
                </div>
                <div class="widget-content">
                    <div class="level-info">
                        <span class="level-number">Nível {summary['level']}</span>
                        <span class="points-info">{summary['total_points']} pontos</span>
                    </div>
                    <div class="badges-info">
                        <span class="badges-count">{summary['badges_count']} badges</span>
                        <span class="ranking-position">#{summary['ranking_position']} no ranking</span>
                    </div>
                    {f'<div class="next-goal">Próximo: {summary["next_badge"]["badge"]["name"]}</div>' if summary['next_badge'] else ''}
                </div>
                <div class="widget-footer">
                    <a href="/gamification/" class="btn btn-sm btn-primary">Ver Detalhes</a>
                </div>
            </div>
            """
            
            return widget_html
        else:
            return "<div class='gamification-widget'>Carregando...</div>"

# Exemplo de uso
def example_usage():
    """Demonstra como usar a integração"""
    
    integration = GamificationIntegration()
    
    # Simula confirmação de agendamento
    print("📅 Simulando confirmação de agendamento...")
    integration.handle_appointment_confirmation(user_id=1, appointment_id=123)
    
    print("\n" + "="*50 + "\n")
    
    # Simula comparecimento à consulta
    print("👤 Simulando comparecimento à consulta...")
    integration.handle_appointment_attendance(user_id=1, appointment_id=123, attended=True)
    
    print("\n" + "="*50 + "\n")
    
    # Simula reagendamento antecipado
    print("🔄 Simulando reagendamento antecipado...")
    integration.handle_appointment_reschedule(user_id=1, appointment_id=123, days_in_advance=2)
    
    print("\n" + "="*50 + "\n")
    
    # Simula conclusão de consultas por profissional
    print("👨‍⚕️ Simulando conclusão de consultas por profissional...")
    integration.handle_professional_completion(user_id=2, appointments_completed=25, absence_rate=0.03)
    
    print("\n" + "="*50 + "\n")
    
    # Obtém resumo de gamificação
    print("📊 Obtendo resumo de gamificação...")
    summary = integration.get_user_gamification_summary(user_id=1, user_type='patient')
    if summary:
        print(f"   Nível: {summary['level']}")
        print(f"   Pontos: {summary['total_points']}")
        print(f"   Badges: {summary['badges_count']}")
        print(f"   Ranking: #{summary['ranking_position']}")
        if summary['next_badge']:
            print(f"   Próximo badge: {summary['next_badge']['badge']['name']}")
    
    print("\n" + "="*50 + "\n")
    
    # Exibe widget de gamificação
    print("🎨 Exibindo widget de gamificação...")
    widget = integration.display_gamification_widget(user_id=1, user_type='patient')
    print("Widget HTML gerado:")
    print(widget)

if __name__ == "__main__":
    print("🚀 EXEMPLO DE INTEGRAÇÃO - SISTEMA DE GAMIFICAÇÃO")
    print("=" * 60)
    
    try:
        example_usage()
        print("\n✅ Exemplo executado com sucesso!")
    except Exception as e:
        print(f"\n❌ Erro ao executar exemplo: {str(e)}")
        print("Certifique-se de que o sistema está configurado corretamente.")







