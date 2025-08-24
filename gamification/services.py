"""
Serviço de Gamificação - Sistema Clínica
Integra com o sistema existente e gerencia notificações
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from .models import UserPoints, Badge, UserBadge, GamificationEvent
from .points_system import GamificationSystem

logger = logging.getLogger(__name__)

class GamificationService:
    """Serviço principal de gamificação"""
    
    def __init__(self, db: SQLAlchemy):
        self.db = db
        self.points_system = GamificationSystem(db)
        self._initialize_badges()
    
    def _initialize_badges(self):
        """Inicializa badges no banco de dados se não existirem"""
        try:
            # Verifica se já existem badges
            if Badge.query.count() == 0:
                self._create_default_badges()
                logger.info("Badges padrão criados com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar badges: {str(e)}")
    
    def _create_default_badges(self):
        """Cria badges padrão no banco de dados"""
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
            self.db.session.add(badge)
        
        self.db.session.commit()
    
    def handle_appointment_action(self, user_id: int, user_type: str, action: str, appointment_data: Dict = None) -> Dict:
        """Processa ação relacionada a agendamento e concede pontos"""
        try:
            # Concede pontos baseado na ação
            result = self.points_system.award_points(user_id, user_type, action, appointment_data)
            
            if result.get('success') and result.get('new_badges'):
                # Envia notificação WhatsApp para novos badges
                self._send_badge_notification(user_id, user_type, result['new_badges'])
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao processar ação de agendamento: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_user_gamification_profile(self, user_id: int, user_type: str) -> Dict:
        """Retorna perfil completo de gamificação do usuário"""
        try:
            profile = self.points_system.get_user_profile(user_id, user_type)
            
            if 'error' not in profile:
                # Adiciona ranking
                profile['ranking'] = self.points_system.get_user_ranking(user_id, user_type)
                
                # Adiciona progresso para próximos badges
                profile['next_badges'] = self._get_next_badges(user_id, user_type)
                
                # Adiciona histórico de eventos
                profile['recent_events'] = self._get_recent_events(user_id, user_type)
            
            return profile
            
        except Exception as e:
            logger.error(f"Erro ao buscar perfil de gamificação: {str(e)}")
            return {"error": str(e)}
    
    def get_leaderboards(self, user_type: str = None) -> Dict:
        """Retorna rankings de gamificação"""
        try:
            leaderboards = {}
            
            if user_type:
                leaderboards[user_type] = self.points_system.get_leaderboard(user_type, 20)
            else:
                leaderboards['patient'] = self.points_system.get_leaderboard('patient', 20)
                leaderboards['professional'] = self.points_system.get_leaderboard('professional', 20)
            
            return leaderboards
            
        except Exception as e:
            logger.error(f"Erro ao buscar leaderboards: {str(e)}")
            return {}
    
    def get_badges_overview(self) -> Dict:
        """Retorna visão geral de todos os badges disponíveis"""
        try:
            badges = Badge.query.filter_by(is_active=True).all()
            
            overview = {
                'patient': [],
                'professional': []
            }
            
            for badge in badges:
                badge_info = {
                    'id': badge.id,
                    'code': badge.code,
                    'name': badge.name,
                    'description': badge.description,
                    'icon': badge.icon,
                    'category': badge.category,
                    'requirement_type': badge.requirement_type,
                    'requirement_value': badge.requirement_value,
                    'points_reward': badge.points_reward,
                    'color': badge.color,
                    'rarity': badge.rarity
                }
                
                overview[badge.user_type].append(badge_info)
            
            return overview
            
        except Exception as e:
            logger.error(f"Erro ao buscar overview de badges: {str(e)}")
            return {'patient': [], 'professional': []}
    
    def get_gamification_stats(self) -> Dict:
        """Retorna estatísticas gerais do sistema de gamificação"""
        try:
            stats = {
                'total_users': {
                    'patient': UserPoints.query.filter_by(user_type='patient').count(),
                    'professional': UserPoints.query.filter_by(user_type='professional').count()
                },
                'total_badges_awarded': UserBadge.query.count(),
                'total_points_awarded': self.db.session.query(UserPoints.total_points).sum()[0] or 0,
                'recent_activity': self._get_recent_system_activity()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao buscar estatísticas de gamificação: {str(e)}")
            return {}
    
    def _get_next_badges(self, user_id: int, user_type: str) -> List[Dict]:
        """Retorna próximos badges que o usuário pode conquistar"""
        try:
            # Busca badges não conquistados
            user_points = UserPoints.query.filter_by(user_id=user_id, user_type=user_type).first()
            if not user_points:
                return []
            
            conquered_badges = UserBadge.query.filter_by(user_points_id=user_points.id).all()
            conquered_badge_ids = [ub.badge_id for ub in conquered_badges]
            
            available_badges = Badge.query.filter(
                Badge.user_type == user_type,
                Badge.is_active == True,
                ~Badge.id.in_(conquered_badge_ids)
            ).all()
            
            next_badges = []
            for badge in available_badges:
                progress = self._calculate_badge_progress(user_points, badge)
                if progress['achievable']:
                    next_badges.append({
                        'badge': {
                            'id': badge.id,
                            'name': badge.name,
                            'description': badge.description,
                            'icon': badge.icon,
                            'color': badge.color,
                            'rarity': badge.rarity
                        },
                        'progress': progress
                    })
            
            # Ordena por facilidade de conquista
            next_badges.sort(key=lambda x: x['progress']['remaining'])
            return next_badges[:5]  # Retorna apenas os 5 mais próximos
            
        except Exception as e:
            logger.error(f"Erro ao buscar próximos badges: {str(e)}")
            return []
    
    def _calculate_badge_progress(self, user_points: UserPoints, badge: Badge) -> Dict:
        """Calcula progresso para um badge específico"""
        try:
            if badge.requirement_type == 'streak':
                current = user_points.consecutive_attendance
                required = badge.requirement_value
                remaining = max(0, required - current)
                percentage = min(100, (current / required) * 100) if required > 0 else 100
                
            elif badge.requirement_type == 'count':
                current = user_points.appointments_attended
                required = badge.requirement_value
                remaining = max(0, required - current)
                percentage = min(100, (current / required) * 100) if required > 0 else 100
                
            elif badge.requirement_type == 'days':
                # Implementar cálculo de dias sem falta
                current = 0  # Placeholder
                required = badge.requirement_value
                remaining = required
                percentage = 0
                
            else:
                current = 0
                required = badge.requirement_value
                remaining = required
                percentage = 0
            
            return {
                'current': current,
                'required': required,
                'remaining': remaining,
                'percentage': percentage,
                'achievable': remaining <= 0
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular progresso do badge: {str(e)}")
            return {'current': 0, 'required': 0, 'remaining': 0, 'percentage': 0, 'achievable': False}
    
    def _get_recent_events(self, user_id: int, user_type: str, limit: int = 10) -> List[Dict]:
        """Retorna eventos recentes de gamificação do usuário"""
        try:
            user_points = UserPoints.query.filter_by(user_id=user_id, user_type=user_type).first()
            if not user_points:
                return []
            
            events = GamificationEvent.query.filter_by(user_points_id=user_points.id)\
                .order_by(GamificationEvent.created_at.desc())\
                .limit(limit)\
                .all()
            
            events_list = []
            for event in events:
                events_list.append({
                    'type': event.event_type,
                    'data': event.event_data,
                    'created_at': event.created_at.isoformat()
                })
            
            return events_list
            
        except Exception as e:
            logger.error(f"Erro ao buscar eventos recentes: {str(e)}")
            return []
    
    def _get_recent_system_activity(self, limit: int = 10) -> List[Dict]:
        """Retorna atividade recente do sistema de gamificação"""
        try:
            events = GamificationEvent.query\
                .order_by(GamificationEvent.created_at.desc())\
                .limit(limit)\
                .all()
            
            activity = []
            for event in events:
                activity.append({
                    'type': event.event_type,
                    'data': event.event_data,
                    'created_at': event.created_at.isoformat()
                })
            
            return activity
            
        except Exception as e:
            logger.error(f"Erro ao buscar atividade recente: {str(e)}")
            return []
    
    def _send_badge_notification(self, user_id: int, user_type: str, new_badges: List[Dict]):
        """Envia notificação WhatsApp quando usuário desbloqueia badge"""
        try:
            # Busca informações do usuário
            user_points = UserPoints.query.filter_by(user_id=user_id, user_type=user_type).first()
            if not user_points or not user_points.user:
                return
            
            user = user_points.user
            
            # Prepara mensagem
            if len(new_badges) == 1:
                badge = new_badges[0]
                message = f"🎉 Parabéns! Você desbloqueou o badge '{badge['name']}' ({badge['icon']})!\n\n"
                message += f"Descrição: {badge['description']}\n"
                if badge['points_reward'] > 0:
                    message += f"Recompensa: +{badge['points_reward']} pontos"
            else:
                message = f"🎉 Parabéns! Você desbloqueou {len(new_badges)} novos badges!\n\n"
                for badge in new_badges:
                    message += f"• {badge['name']} ({badge['icon']})\n"
            
            # Envia via WhatsApp se disponível
            if hasattr(current_app, 'whatsapp_service'):
                try:
                    current_app.whatsapp_service.send_message(
                        phone=user.phone,
                        message=message
                    )
                    logger.info(f"Notificação WhatsApp enviada para usuário {user_id}")
                except Exception as e:
                    logger.warning(f"Não foi possível enviar notificação WhatsApp: {str(e)}")
            
            # Marca notificação como enviada
            for badge in new_badges:
                user_badge = UserBadge.query.filter_by(
                    user_points_id=user_points.id,
                    badge_id=badge['id']
                ).first()
                if user_badge:
                    user_badge.notification_sent = True
            
            self.db.session.commit()
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de badge: {str(e)}")
    
    def reset_user_points(self, user_id: int, user_type: str) -> bool:
        """Reseta pontos de um usuário (para administradores)"""
        try:
            user_points = UserPoints.query.filter_by(user_id=user_id, user_type=user_type).first()
            if user_points:
                user_points.total_points = 0
                user_points.current_points = 0
                user_points.level = 1
                user_points.appointments_attended = 0
                user_points.appointments_missed = 0
                user_points.consecutive_attendance = 0
                user_points.longest_streak = 0
                
                self.db.session.commit()
                logger.info(f"Pontos resetados para usuário {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao resetar pontos: {str(e)}")
            self.db.session.rollback()
            return False
