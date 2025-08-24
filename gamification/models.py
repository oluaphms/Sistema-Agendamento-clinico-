"""
Modelos de Gamificação - Sistema Clínica
Tabelas para pontos, badges, conquistas e rankings
"""

from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class UserPoints(db.Model):
    """Tabela de pontos dos usuários"""
    
    __tablename__ = 'user_points'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'patient' ou 'professional'
    
    # Pontuação
    total_points = db.Column(db.Integer, default=0, nullable=False)
    current_points = db.Column(db.Integer, default=0, nullable=False)
    level = db.Column(db.Integer, default=1, nullable=False)
    
    # Estatísticas
    appointments_attended = db.Column(db.Integer, default=0, nullable=False)
    appointments_missed = db.Column(db.Integer, default=0, nullable=False)
    consecutive_attendance = db.Column(db.Integer, default=0, nullable=False)
    longest_streak = db.Column(db.Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='points')
    transactions = db.relationship('PointsTransaction', backref='user_points', lazy='dynamic')
    badges = db.relationship('UserBadge', backref='user_points', lazy='dynamic')
    
    def __repr__(self):
        return f'<UserPoints {self.user_id}:{self.user_type}>'

class PointsTransaction(db.Model):
    """Transações de pontos"""
    
    __tablename__ = 'points_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_points_id = db.Column(db.Integer, db.ForeignKey('user_points.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))
    metadata = db.Column(JSON)  # Dados adicionais da ação
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<PointsTransaction {self.action}:{self.points}>'

class Badge(db.Model):
    """Definições de badges disponíveis"""
    
    __tablename__ = 'badges'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(10))  # Emoji ou código do ícone
    category = db.Column(db.String(30), nullable=False)  # 'attendance', 'loyalty', 'performance'
    user_type = db.Column(db.String(20), nullable=False)  # 'patient' ou 'professional'
    
    # Requisitos para desbloquear
    requirement_type = db.Column(db.String(30), nullable=False)  # 'points', 'count', 'streak'
    requirement_value = db.Column(db.Integer, nullable=False)
    
    # Recompensa
    points_reward = db.Column(db.Integer, default=0)
    
    # Visual
    color = db.Column(db.String(20), default='primary')  # primary, success, warning, danger, info
    rarity = db.Column(db.String(20), default='common')  # common, rare, epic, legendary
    
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Badge {self.code}:{self.name}>'

class UserBadge(db.Model):
    """Badges conquistados pelos usuários"""
    
    __tablename__ = 'user_badges'
    
    id = db.Column(db.Integer, primary_key=True)
    user_points_id = db.Column(db.Integer, db.ForeignKey('user_points.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)
    
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    notification_sent = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relacionamentos
    badge = db.relationship('Badge', backref='user_badges')
    
    def __repr__(self):
        return f'<UserBadge {self.badge.code}:{self.user_points_id}>'

class Achievement(db.Model):
    """Conquistas e marcos dos usuários"""
    
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_points_id = db.Column(db.Integer, db.ForeignKey('user_points.id'), nullable=False)
    achievement_type = db.Column(db.String(50), nullable=False)
    achievement_value = db.Column(db.Integer, nullable=False)
    points_earned = db.Column(db.Integer, nullable=False)
    
    achieved_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Achievement {self.achievement_type}:{self.achievement_value}>'

class Leaderboard(db.Model):
    """Ranking dos usuários (atualizado periodicamente)"""
    
    __tablename__ = 'leaderboards'
    
    id = db.Column(db.Integer, primary_key=True)
    user_points_id = db.Column(db.Integer, db.ForeignKey('user_points.id'), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    
    # Ranking
    position = db.Column(db.Integer, nullable=False)
    total_points = db.Column(db.Integer, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    
    # Período
    period = db.Column(db.String(20), nullable=False)  # 'daily', 'weekly', 'monthly', 'all_time'
    period_date = db.Column(db.Date, nullable=False)
    
    # Estatísticas do período
    appointments_count = db.Column(db.Integer, default=0)
    attendance_rate = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Leaderboard {self.user_type}:{self.position}>'

class GamificationEvent(db.Model):
    """Eventos de gamificação para auditoria"""
    
    __tablename__ = 'gamification_events'
    
    id = db.Column(db.Integer, primary_key=True)
    user_points_id = db.Column(db.Integer, db.ForeignKey('user_points.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # 'points_earned', 'badge_unlocked', 'level_up'
    event_data = db.Column(JSON, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<GamificationEvent {self.event_type}:{self.user_points_id}>'
