"""
Sistema de Pontos - Gamificação Sistema Clínica
Implementa as regras específicas de pontuação solicitadas
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from .models import UserPoints, PointsTransaction, Badge, UserBadge, Achievement, GamificationEvent
import json

logger = logging.getLogger(__name__)

class GamificationSystem:
    """Sistema de gamificação para engajamento de pacientes e profissionais"""
    
    def __init__(self, db: SQLAlchemy):
        self.db = db
        self.badges = self._initialize_badges()
        self.achievements = self._initialize_achievements()
    
    def _initialize_badges(self) -> Dict:
        """Inicializa sistema de badges conforme especificações"""
        return {
            'patient': {
                'paciente_pontual': {
                    'name': 'Paciente Pontual',
                    'description': '5 consultas seguidas sem faltas',
                    'icon': '⏰',
                    'points': 100,
                    'category': 'attendance',
                    'requirement_type': 'streak',
                    'requirement_value': 5,
                    'color': 'success',
                    'rarity': 'rare'
                },
                'paciente_fiel': {
                    'name': 'Paciente Fiel',
                    'description': '10 consultas realizadas',
                    'icon': '👑',
                    'points': 200,
                    'category': 'loyalty',
                    'requirement_type': 'count',
                    'requirement_value': 10,
                    'color': 'primary',
                    'rarity': 'epic'
                },
                'zero_faltas': {
                    'name': 'Zero Faltas',
                    'description': '30 dias sem ausências',
                    'icon': '🎯',
                    'description': '30 dias sem ausências',
                    'icon': '🎯',
                    'points': 300,
                    'category': 'attendance',
                    'requirement_type': 'days',
                    'requirement_value': 30,
                    'color': 'warning',
                    'rarity': 'legendary'
                }
            },
            'professional': {
                'top_mes': {
                    'name': 'Top do Mês',
                    'description': 'Profissional com maior receita mensal',
                    'icon': '🏆',
                    'points': 500,
                    'category': 'performance',
                    'requirement_type': 'ranking',
                    'requirement_value': 1,
                    'color': 'warning',
                    'rarity': 'epic'
                },
                'super_agenda': {
                    'name': 'Super Agenda',
                    'description': 'Profissional com mais consultas realizadas',
                    'icon': '📅',
                    'points': 400,
                    'category': 'productivity',
                    'requirement_type': 'count',
                    'requirement_value': 50,
                    'color': 'primary',
                    'rarity': 'rare'
                }
            }
        }
    
    def _initialize_achievements(self) -> Dict:
        """Inicializa sistema de conquistas"""
        return {
            'patient': {
                'consultation_streak': {
                    'name': 'Sequência de Consultas',
                    'levels': [
                        {'level': 1, 'requirement': 3, 'points': 50, 'icon': '🔥'},
                        {'level': 2, 'requirement': 5, 'points': 100, 'icon': '🔥🔥'},
                        {'level': 3, 'requirement': 10, 'points': 200, 'icon': '🔥🔥🔥'}
                    ]
                },
                'perfect_month': {
                    'name': 'Mês Perfeito',
                    'description': 'Compareceu a todas as consultas do mês',
                    'points': 150,
                    'icon': '⭐'
                }
            },
            'professional': {
                'excellence_month': {
                    'name': 'Excelência Mensal',
                    'description': 'Taxa de faltas abaixo de 5% no mês',
                    'points': 300,
                    'icon': '🌟'
                },
                'patient_care': {
                    'name': 'Cuidado com Pacientes',
                    'levels': [
                        {'level': 1, 'requirement': 50, 'points': 200, 'icon': '💙'},
                        {'level': 2, 'requirement': 100, 'points': 400, 'icon': '💙💙'},
                        {'level': 3, 'requirement': 200, 'points': 800, 'icon': '💙💙💙'}
                    ]
                }
            }
        }
    
    def award_points(self, user_id: int, user_type: str, action: str, action_data: Dict = None) -> Dict:
        """Concede pontos para uma ação do usuário seguindo as regras específicas"""
        try:
            points = self._calculate_points(user_type, action, action_data)
            
            if points != 0:
                # Busca ou cria registro de pontos do usuário
                user_points = self._get_or_create_user_points(user_id, user_type)
                
                # Atualiza pontos
                user_points.total_points += points
                user_points.current_points += points
                
                # Atualiza estatísticas baseado na ação
                self._update_user_stats(user_points, action, action_data)
                
                # Adiciona transação de pontos
                transaction = self._create_points_transaction(user_points.id, action, points, action_data)
                
                # Verifica se conquistou badges
                new_badges = self._check_badges(user_points, action, action_data)
                
                # Verifica se completou conquistas
                new_achievements = self._check_achievements(user_points, action, action_data)
                
                # Verifica se subiu de nível
                level_up = self._check_level_up(user_points)
                
                # Registra evento
                self._log_gamification_event(user_points.id, 'points_earned', {
                    'action': action,
                    'points': points,
                    'new_badges': len(new_badges),
                    'new_achievements': len(new_achievements),
                    'level_up': level_up
                })
                
                self.db.session.commit()
                
                return {
                    "success": True,
                    "points_awarded": points,
                    "total_points": user_points.total_points,
                    "current_points": user_points.current_points,
                    "level": user_points.level,
                    "new_badges": new_badges,
                    "new_achievements": new_achievements,
                    "level_up": level_up
                }
            
            return {"success": True, "points_awarded": 0}
            
        except Exception as e:
            logger.error(f"Erro ao conceder pontos: {str(e)}")
            self.db.session.rollback()
            return {"success": False, "error": str(e)}
    
    def _calculate_points(self, user_type: str, action: str, action_data: Dict = None) -> int:
        """Calcula pontos seguindo as regras específicas solicitadas"""
        
        # Regras para PACIENTES
        if user_type == 'patient':
            patient_rules = {
                'confirm_presence': 10,      # +10 pontos ao confirmar presença
                'attend_appointment': 5,     # +5 pontos ao comparecer na consulta
                'miss_appointment': -10,     # -10 pontos em caso de falta sem aviso
                'reschedule_advance': 3      # +3 pontos ao reagendar com antecedência
            }
            return patient_rules.get(action, 0)
        
        # Regras para PROFISSIONAIS
        elif user_type == 'professional':
            professional_rules = {
                'complete_appointment': 25,  # +25 pontos por consulta realizada
                'low_absence_rate': 50,      # +50 pontos se taxa de faltas < 5%
                'high_productivity': 100     # +100 pontos por alta produtividade
            }
            return professional_rules.get(action, 0)
        
        return 0
    
    def _get_or_create_user_points(self, user_id: int, user_type: str) -> UserPoints:
        """Busca ou cria registro de pontos do usuário"""
        user_points = UserPoints.query.filter_by(
            user_id=user_id, 
            user_type=user_type
        ).first()
        
        if not user_points:
            user_points = UserPoints(
                user_id=user_id,
                user_type=user_type,
                total_points=0,
                current_points=0,
                level=1
            )
            self.db.session.add(user_points)
            self.db.session.flush()  # Para obter o ID
        
        return user_points
    
    def _update_user_stats(self, user_points: UserPoints, action: str, action_data: Dict = None):
        """Atualiza estatísticas do usuário baseado na ação"""
        
        if action == 'attend_appointment':
            user_points.appointments_attended += 1
            user_points.consecutive_attendance += 1
            if user_points.consecutive_attendance > user_points.longest_streak:
                user_points.longest_streak = user_points.consecutive_attendance
        
        elif action == 'miss_appointment':
            user_points.appointments_missed += 1
            user_points.consecutive_attendance = 0
        
        elif action == 'confirm_presence':
            # Apenas confirmação, não altera estatísticas de atendimento
            pass
    
    def _create_points_transaction(self, user_points_id: int, action: str, points: int, action_data: Dict = None) -> PointsTransaction:
        """Cria transação de pontos"""
        
        descriptions = {
            'confirm_presence': 'Confirmação de presença na consulta',
            'attend_appointment': 'Compareceu à consulta',
            'miss_appointment': 'Faltou à consulta sem aviso',
            'reschedule_advance': 'Reagendou consulta com antecedência',
            'complete_appointment': 'Consultas realizadas sem cancelamento',
            'low_absence_rate': 'Taxa de faltas baixa (< 5%)',
            'high_productivity': 'Alta produtividade mensal'
        }
        
        transaction = PointsTransaction(
            user_points_id=user_points_id,
            action=action,
            points=points,
            description=descriptions.get(action, f'Ação: {action}'),
            metadata=action_data or {}
        )
        
        self.db.session.add(transaction)
        return transaction
    
    def _check_badges(self, user_points: UserPoints, action: str, action_data: Dict = None) -> List[Dict]:
        """Verifica se usuário conquistou novos badges"""
        new_badges = []
        
        # Busca badges disponíveis para o tipo de usuário
        available_badges = Badge.query.filter_by(
            user_type=user_points.user_type,
            is_active=True
        ).all()
        
        # Busca badges já conquistados
        user_badges = UserBadge.query.filter_by(user_points_id=user_points.id).all()
        conquered_badge_ids = [ub.badge_id for ub in user_badges]
        
        for badge in available_badges:
            if badge.id not in conquered_badge_ids:
                if self._check_badge_requirement(user_points, badge, action, action_data):
                    # Concede o badge
                    user_badge = UserBadge(
                        user_points_id=user_points.id,
                        badge_id=badge.id
                    )
                    self.db.session.add(user_badge)
                    
                    # Adiciona pontos de recompensa se houver
                    if badge.points_reward > 0:
                        user_points.total_points += badge.points_reward
                        user_points.current_points += badge.points_reward
                    
                    new_badges.append({
                        'id': badge.id,
                        'name': badge.name,
                        'description': badge.description,
                        'icon': badge.icon,
                        'color': badge.color,
                        'rarity': badge.rarity,
                        'points_reward': badge.points_reward
                    })
                    
                    # Registra evento
                    self._log_gamification_event(user_points.id, 'badge_unlocked', {
                        'badge_id': badge.id,
                        'badge_name': badge.name,
                        'points_reward': badge.points_reward
                    })
        
        return new_badges
    
    def _check_badge_requirement(self, user_points: UserPoints, badge: Badge, action: str, action_data: Dict = None) -> bool:
        """Verifica se usuário atende requisitos para um badge"""
        
        if badge.requirement_type == 'streak':
            # Requisito de sequência (ex: 5 consultas seguidas)
            return user_points.consecutive_attendance >= badge.requirement_value
        
        elif badge.requirement_type == 'count':
            # Requisito de contagem (ex: 10 consultas realizadas)
            return user_points.appointments_attended >= badge.requirement_value
        
        elif badge.requirement_type == 'days':
            # Requisito de dias (ex: 30 dias sem ausências)
            # Implementar lógica baseada em data da última falta
            return self._check_days_without_absence(user_points, badge.requirement_value)
        
        elif badge.requirement_type == 'ranking':
            # Requisito de ranking (ex: 1º lugar)
            return self._check_ranking_position(user_points, badge.requirement_value)
        
        return False
    
    def _check_days_without_absence(self, user_points: UserPoints, required_days: int) -> bool:
        """Verifica se usuário não faltou por X dias"""
        # Busca última transação de falta
        last_miss = PointsTransaction.query.filter_by(
            user_points_id=user_points.id,
            action='miss_appointment'
        ).order_by(PointsTransaction.created_at.desc()).first()
        
        if not last_miss:
            # Nunca faltou
            return True
        
        days_since_last_miss = (datetime.utcnow() - last_miss.created_at).days
        return days_since_last_miss >= required_days
    
    def _check_ranking_position(self, user_points: UserPoints, required_position: int) -> bool:
        """Verifica se usuário está em determinada posição no ranking"""
        # Implementar lógica de ranking
        # Por enquanto, retorna False
        return False
    
    def _check_achievements(self, user_points: UserPoints, action: str, action_data: Dict = None) -> List[Dict]:
        """Verifica se usuário completou conquistas"""
        new_achievements = []
        
        # Verifica conquistas baseadas em estatísticas
        if user_points.appointments_attended == 5:
            achievement = Achievement(
                user_points_id=user_points.id,
                achievement_type='consultation_milestone',
                achievement_value=5,
                points_earned=50
            )
            self.db.session.add(achievement)
            new_achievements.append({
                'type': 'consultation_milestone',
                'value': 5,
                'points': 50
            })
        
        return new_achievements
    
    def _check_level_up(self, user_points: UserPoints) -> bool:
        """Verifica se usuário subiu de nível"""
        new_level = 1 + (user_points.total_points // 100)
        
        if new_level > user_points.level:
            old_level = user_points.level
            user_points.level = new_level
            
            # Registra evento de level up
            self._log_gamification_event(user_points.id, 'level_up', {
                'old_level': old_level,
                'new_level': new_level,
                'points_required': new_level * 100
            })
            
            return True
        
        return False
    
    def _log_gamification_event(self, user_points_id: int, event_type: str, event_data: Dict):
        """Registra evento de gamificação"""
        event = GamificationEvent(
            user_points_id=user_points_id,
            event_type=event_type,
            event_data=event_data
        )
        self.db.session.add(event)
    
    def get_user_profile(self, user_id: int, user_type: str) -> Dict:
        """Retorna perfil gamificado do usuário"""
        try:
            user_points = UserPoints.query.filter_by(
                user_id=user_id, 
                user_type=user_type
            ).first()
            
            if not user_points:
                return {"error": "Usuário não encontrado no sistema de gamificação"}
            
            # Busca badges conquistados
            user_badges = UserBadge.query.filter_by(user_points_id=user_points.id).all()
            badges = []
            for ub in user_badges:
                badges.append({
                    'id': ub.badge.id,
                    'name': ub.badge.name,
                    'description': ub.badge.description,
                    'icon': ub.badge.icon,
                    'color': ub.badge.color,
                    'rarity': ub.badge.rarity,
                    'unlocked_at': ub.unlocked_at.isoformat()
                })
            
            # Busca conquistas
            achievements = Achievement.query.filter_by(user_points_id=user_points.id).all()
            achievements_list = []
            for a in achievements:
                achievements_list.append({
                    'type': a.achievement_type,
                    'value': a.achievement_value,
                    'points': a.points_earned,
                    'achieved_at': a.achieved_at.isoformat()
                })
            
            # Calcula pontos para próximo nível
            points_to_next_level = max(0, (user_points.level + 1) * 100 - user_points.total_points)
            
            return {
                "user_id": user_id,
                "user_type": user_type,
                "level": user_points.level,
                "total_points": user_points.total_points,
                "current_points": user_points.current_points,
                "points_to_next_level": points_to_next_level,
                "badges": badges,
                "achievements": achievements_list,
                "stats": {
                    "appointments_attended": user_points.appointments_attended,
                    "appointments_missed": user_points.appointments_missed,
                    "consecutive_attendance": user_points.consecutive_attendance,
                    "longest_streak": user_points.longest_streak,
                    "attendance_rate": self._calculate_attendance_rate(user_points)
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar perfil do usuário: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_attendance_rate(self, user_points: UserPoints) -> float:
        """Calcula taxa de comparecimento"""
        total = user_points.appointments_attended + user_points.appointments_missed
        if total == 0:
            return 100.0
        return (user_points.appointments_attended / total) * 100
    
    def get_leaderboard(self, user_type: str, limit: int = 10) -> List[Dict]:
        """Retorna ranking dos usuários com mais pontos"""
        try:
            leaderboard = UserPoints.query.filter_by(user_type=user_type)\
                .order_by(UserPoints.total_points.desc())\
                .limit(limit)\
                .all()
            
            result = []
            for i, user_points in enumerate(leaderboard, 1):
                result.append({
                    "position": i,
                    "user_id": user_points.user_id,
                    "username": user_points.user.username if user_points.user else f"Usuário {user_points.user_id}",
                    "points": user_points.total_points,
                    "level": user_points.level,
                    "appointments_attended": user_points.appointments_attended
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao buscar leaderboard: {str(e)}")
            return []
    
    def get_user_ranking(self, user_id: int, user_type: str) -> Dict:
        """Retorna posição do usuário no ranking"""
        try:
            # Busca posição do usuário
            user_position = self.db.session.query(UserPoints)\
                .filter(UserPoints.total_points > UserPoints.total_points)\
                .filter_by(user_type=user_type)\
                .count() + 1
            
            # Total de usuários do tipo
            total_users = UserPoints.query.filter_by(user_type=user_type).count()
            
            return {
                "position": user_position,
                "total_users": total_users,
                "percentile": max(1, 100 - ((user_position - 1) / total_users * 100)) if total_users > 0 else 100
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular ranking do usuário: {str(e)}")
            return {"position": 0, "total_users": 0, "percentile": 0}
