"""
Rotas de Gamificação - Sistema Clínica
Endpoints para acesso ao sistema de gamificação
"""

from flask import Blueprint, render_template, jsonify, request, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from .services import GamificationService
from app import db
import logging

logger = logging.getLogger(__name__)

# Cria blueprint de gamificação
gamification_bp = Blueprint('gamification', __name__, url_prefix='/gamification')

# Inicializa serviço de gamificação
def get_gamification_service():
    return GamificationService(db)

@gamification_bp.route('/')
@login_required
def index():
    """Página principal de gamificação"""
    try:
        service = get_gamification_service()
        
        # Determina tipo de usuário baseado no papel
        user_type = 'patient' if current_user.role in ['patient', 'user'] else 'professional'
        
        # Busca perfil do usuário
        profile = service.get_user_gamification_profile(current_user.id, user_type)
        
        # Busca leaderboards
        leaderboards = service.get_leaderboards()
        
        # Busca overview de badges
        badges_overview = service.get_badges_overview()
        
        return render_template('gamification/index.html',
                             profile=profile,
                             leaderboards=leaderboards,
                             badges_overview=badges_overview,
                             user_type=user_type)
        
    except Exception as e:
        logger.error(f"Erro na página de gamificação: {str(e)}")
        flash('Erro ao carregar página de gamificação', 'error')
        return redirect(url_for('dashboard.index'))

@gamification_bp.route('/profile')
@login_required
def profile():
    """Perfil detalhado de gamificação do usuário"""
    try:
        service = get_gamification_service()
        
        user_type = 'patient' if current_user.role in ['patient', 'user'] else 'professional'
        profile = service.get_user_gamification_profile(current_user.id, user_type)
        
        if 'error' in profile:
            flash('Erro ao carregar perfil de gamificação', 'error')
            return redirect(url_for('gamification.index'))
        
        return render_template('gamification/profile.html',
                             profile=profile,
                             user_type=user_type)
        
    except Exception as e:
        logger.error(f"Erro no perfil de gamificação: {str(e)}")
        flash('Erro ao carregar perfil', 'error')
        return redirect(url_for('gamification.index'))

@gamification_bp.route('/leaderboard')
@login_required
def leaderboard():
    """Página de rankings"""
    try:
        service = get_gamification_service()
        
        # Parâmetros de filtro
        user_type = request.args.get('type', 'all')
        period = request.args.get('period', 'all_time')
        
        if user_type == 'all':
            leaderboards = service.get_leaderboards()
        else:
            leaderboards = {user_type: service.get_leaderboards(user_type)}
        
        return render_template('gamification/leaderboard.html',
                             leaderboards=leaderboards,
                             selected_type=user_type,
                             selected_period=period)
        
    except Exception as e:
        logger.error(f"Erro no leaderboard: {str(e)}")
        flash('Erro ao carregar rankings', 'error')
        return redirect(url_for('gamification.index'))

@gamification_bp.route('/badges')
@login_required
def badges():
    """Página de badges disponíveis"""
    try:
        service = get_gamification_service()
        
        user_type = 'patient' if current_user.role in ['patient', 'user'] else 'professional'
        badges_overview = service.get_badges_overview()
        
        # Busca badges conquistados pelo usuário
        profile = service.get_user_gamification_profile(current_user.id, user_type)
        user_badges = profile.get('badges', []) if 'error' not in profile else []
        
        return render_template('gamification/badges.html',
                             badges_overview=badges_overview,
                             user_badges=user_badges,
                             user_type=user_type)
        
    except Exception as e:
        logger.error(f"Erro na página de badges: {str(e)}")
        flash('Erro ao carregar badges', 'error')
        return redirect(url_for('gamification.index'))

@gamification_bp.route('/api/profile')
@login_required
def api_profile():
    """API para perfil de gamificação"""
    try:
        service = get_gamification_service()
        
        user_type = 'patient' if current_user.role in ['patient', 'user'] else 'professional'
        profile = service.get_user_gamification_profile(current_user.id, user_type)
        
        return jsonify(profile)
        
    except Exception as e:
        logger.error(f"Erro na API de perfil: {str(e)}")
        return jsonify({'error': str(e)}), 500

@gamification_bp.route('/api/leaderboard')
@login_required
def api_leaderboard():
    """API para leaderboards"""
    try:
        service = get_gamification_service()
        
        user_type = request.args.get('type')
        limit = int(request.args.get('limit', 20))
        
        leaderboards = service.get_leaderboards(user_type)
        
        return jsonify(leaderboards)
        
    except Exception as e:
        logger.error(f"Erro na API de leaderboard: {str(e)}")
        return jsonify({'error': str(e)}), 500

@gamification_bp.route('/api/badges')
@login_required
def api_badges():
    """API para badges"""
    try:
        service = get_gamification_service()
        
        badges_overview = service.get_badges_overview()
        
        return jsonify(badges_overview)
        
    except Exception as e:
        logger.error(f"Erro na API de badges: {str(e)}")
        return jsonify({'error': str(e)}), 500

@gamification_bp.route('/api/stats')
@login_required
def api_stats():
    """API para estatísticas gerais"""
    try:
        service = get_gamification_service()
        
        stats = service.get_gamification_stats()
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Erro na API de estatísticas: {str(e)}")
        return jsonify({'error': str(e)}), 500

@gamification_bp.route('/api/award-points', methods=['POST'])
@login_required
def api_award_points():
    """API para conceder pontos (usado pelo sistema)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        user_id = data.get('user_id')
        user_type = data.get('user_type')
        action = data.get('action')
        action_data = data.get('action_data')
        
        if not all([user_id, user_type, action]):
            return jsonify({'error': 'Parâmetros obrigatórios não fornecidos'}), 400
        
        service = get_gamification_service()
        result = service.handle_appointment_action(user_id, user_type, action, action_data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro ao conceder pontos: {str(e)}")
        return jsonify({'error': str(e)}), 500

@gamification_bp.route('/admin/reset-points/<int:user_id>', methods=['POST'])
@login_required
def admin_reset_points(user_id):
    """Reset de pontos de um usuário (apenas admin)"""
    try:
        if not current_user.has_role('admin'):
            flash('Acesso negado', 'error')
            return redirect(url_for('gamification.index'))
        
        data = request.get_json()
        user_type = data.get('user_type')
        
        if not user_type:
            return jsonify({'error': 'Tipo de usuário não fornecido'}), 400
        
        service = get_gamification_service()
        success = service.reset_user_points(user_id, user_type)
        
        if success:
            flash('Pontos resetados com sucesso', 'success')
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
    except Exception as e:
        logger.error(f"Erro ao resetar pontos: {str(e)}")
        return jsonify({'error': str(e)}), 500

@gamification_bp.route('/admin/stats')
@login_required
def admin_stats():
    """Página de estatísticas para administradores"""
    try:
        if not current_user.has_role('admin'):
            flash('Acesso negado', 'error')
            return redirect(url_for('gamification.index'))
        
        service = get_gamification_service()
        stats = service.get_gamification_stats()
        
        return render_template('gamification/admin_stats.html', stats=stats)
        
    except Exception as e:
        logger.error(f"Erro na página de estatísticas admin: {str(e)}")
        flash('Erro ao carregar estatísticas', 'error')
        return redirect(url_for('gamification.index'))

# Rotas de erro
@gamification_bp.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@gamification_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
