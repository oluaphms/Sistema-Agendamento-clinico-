import logging
from datetime import datetime
from typing import Dict, List, Optional
from flask import current_app, session
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
import json

logger = logging.getLogger(__name__)

class NotificationManager:
    """Gerenciador de notificações em tempo real via WebSockets"""
    
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.user_rooms = {}  # Mapeia usuário para suas salas
        self.notification_history = {}  # Histórico de notificações por usuário
        
    def setup_handlers(self):
        """Configura os handlers dos WebSockets"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Usuário conectou ao WebSocket"""
            user_id = session.get('usuario')
            if user_id:
                # Adiciona usuário à sala geral
                join_room('general')
                
                # Adiciona usuário à sala específica baseada no role
                role = session.get('role')
                if role:
                    join_room(f'role_{role}')
                
                # Adiciona usuário à sala específica se for profissional
                profissional_id = session.get('profissional_id')
                if profissional_id:
                    join_room(f'professional_{profissional_id}')
                
                # Registra sala do usuário
                self.user_rooms[user_id] = rooms()
                
                logger.info(f"Usuário {user_id} conectado ao WebSocket")
                emit('connection_status', {'status': 'connected', 'user_id': user_id})
            else:
                emit('connection_status', {'status': 'unauthorized'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Usuário desconectou do WebSocket"""
            user_id = session.get('usuario')
            if user_id:
                # Remove usuário das salas
                if user_id in self.user_rooms:
                    for room in self.user_rooms[user_id]:
                        leave_room(room)
                    del self.user_rooms[user_id]
                
                logger.info(f"Usuário {user_id} desconectou do WebSocket")
        
        @self.socketio.on('join_room')
        def handle_join_room(data):
            """Usuário quer entrar em uma sala específica"""
            room = data.get('room')
            user_id = session.get('usuario')
            
            if room and user_id:
                join_room(room)
                if user_id not in self.user_rooms:
                    self.user_rooms[user_id] = []
                self.user_rooms[user_id].append(room)
                
                emit('room_joined', {'room': room, 'status': 'success'})
                logger.info(f"Usuário {user_id} entrou na sala {room}")
        
        @self.socketio.on('leave_room')
        def handle_leave_room(data):
            """Usuário quer sair de uma sala específica"""
            room = data.get('room')
            user_id = session.get('usuario')
            
            if room and user_id:
                leave_room(room)
                if user_id in self.user_rooms and room in self.user_rooms[user_id]:
                    self.user_rooms[user_id].remove(room)
                
                emit('room_left', {'room': room, 'status': 'success'})
                logger.info(f"Usuário {user_id} saiu da sala {room}")
        
        @self.socketio.on('send_notification')
        def handle_send_notification(data):
            """Usuário envia notificação para outros usuários"""
            target_room = data.get('room', 'general')
            message = data.get('message', '')
            notification_type = data.get('type', 'info')
            user_id = session.get('usuario')
            
            if user_id and message:
                notification = {
                    'id': self._generate_notification_id(),
                    'message': message,
                    'type': notification_type,
                    'sender': user_id,
                    'timestamp': datetime.now().isoformat(),
                    'room': target_room
                }
                
                # Envia para a sala especificada
                self.socketio.emit('new_notification', notification, room=target_room)
                
                # Salva no histórico
                self._save_notification_history(notification, target_room)
                
                logger.info(f"Notificação enviada por {user_id} para sala {target_room}")
        
        @self.socketio.on('mark_as_read')
        def handle_mark_as_read(data):
            """Marca notificação como lida"""
            notification_id = data.get('notification_id')
            user_id = session.get('usuario')
            
            if notification_id and user_id:
                # Em produção, isso seria salvo no banco de dados
                emit('notification_read', {'notification_id': notification_id, 'status': 'success'})
    
    def send_appointment_notification(self, appointment_data: Dict, notification_type: str = 'info'):
        """Envia notificação sobre agendamento"""
        try:
            notification = {
                'id': self._generate_notification_id(),
                'type': notification_type,
                'timestamp': datetime.now().isoformat(),
                'appointment_id': appointment_data.get('id'),
                'data': appointment_data
            }
            
            # Cria mensagem baseada no tipo de notificação
            if notification_type == 'new_appointment':
                notification['message'] = f"Novo agendamento: {appointment_data['paciente']['nome']} - {appointment_data['data']} {appointment_data['hora']}"
                notification['title'] = "Novo Agendamento"
                
            elif notification_type == 'appointment_updated':
                notification['message'] = f"Agendamento atualizado: {appointment_data['paciente']['nome']} - {appointment_data['data']} {appointment_data['hora']}"
                notification['title'] = "Agendamento Atualizado"
                
            elif notification_type == 'appointment_cancelled':
                notification['message'] = f"Agendamento cancelado: {appointment_data['paciente']['nome']} - {appointment_data['data']} {appointment_data['hora']}"
                notification['title'] = "Agendamento Cancelado"
                
            elif notification_type == 'appointment_reminder':
                notification['message'] = f"Lembrete: Consulta de {appointment_data['paciente']['nome']} hoje às {appointment_data['hora']}"
                notification['title'] = "Lembrete de Consulta"
            
            # Envia para sala geral
            self.socketio.emit('appointment_notification', notification, room='general')
            
            # Envia para sala específica do profissional
            profissional_id = appointment_data.get('profissional_id')
            if profissional_id:
                self.socketio.emit('appointment_notification', notification, room=f'professional_{profissional_id}')
            
            # Envia para sala de recepção
            self.socketio.emit('appointment_notification', notification, room='role_recepcao')
            
            # Envia para sala de admin
            self.socketio.emit('appointment_notification', notification, room='role_admin')
            
            logger.info(f"Notificação de agendamento enviada: {notification_type}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de agendamento: {str(e)}")
    
    def send_system_notification(self, message: str, notification_type: str = 'info', target_rooms: List[str] = None):
        """Envia notificação do sistema"""
        try:
            notification = {
                'id': self._generate_notification_id(),
                'type': notification_type,
                'message': message,
                'title': 'Sistema',
                'timestamp': datetime.now().isoformat(),
                'is_system': True
            }
            
            if target_rooms:
                for room in target_rooms:
                    self.socketio.emit('system_notification', notification, room=room)
            else:
                # Envia para todos
                self.socketio.emit('system_notification', notification)
            
            logger.info(f"Notificação do sistema enviada: {message}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação do sistema: {str(e)}")
    
    def send_patient_notification(self, patient_id: int, message: str, notification_type: str = 'info'):
        """Envia notificação específica para um paciente"""
        try:
            notification = {
                'id': self._generate_notification_id(),
                'type': notification_type,
                'message': message,
                'title': 'Notificação da Clínica',
                'timestamp': datetime.now().isoformat(),
                'patient_id': patient_id
            }
            
            # Envia para sala específica do paciente
            self.socketio.emit('patient_notification', notification, room=f'patient_{patient_id}')
            
            logger.info(f"Notificação para paciente {patient_id} enviada")
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação para paciente: {str(e)}")
    
    def send_emergency_notification(self, message: str, priority: str = 'high'):
        """Envia notificação de emergência"""
        try:
            notification = {
                'id': self._generate_notification_id(),
                'type': 'emergency',
                'message': message,
                'title': '🚨 EMERGÊNCIA',
                'timestamp': datetime.now().isoformat(),
                'priority': priority,
                'is_emergency': True
            }
            
            # Notificação de emergência vai para todos os usuários
            self.socketio.emit('emergency_notification', notification)
            
            logger.warning(f"Notificação de emergência enviada: {message}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de emergência: {str(e)}")
    
    def send_chat_message(self, sender_id: str, message: str, target_room: str):
        """Envia mensagem de chat"""
        try:
            chat_message = {
                'id': self._generate_notification_id(),
                'type': 'chat',
                'message': message,
                'sender': sender_id,
                'timestamp': datetime.now().isoformat(),
                'room': target_room
            }
            
            # Envia para a sala de chat especificada
            self.socketio.emit('chat_message', chat_message, room=target_room)
            
            logger.info(f"Mensagem de chat enviada por {sender_id} para sala {target_room}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem de chat: {str(e)}")
    
    def broadcast_to_role(self, role: str, notification: Dict):
        """Envia notificação para todos os usuários de um determinado role"""
        try:
            room_name = f'role_{role}'
            self.socketio.emit('role_notification', notification, room=room_name)
            logger.info(f"Notificação enviada para role {role}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação para role {role}: {str(e)}")
    
    def get_user_notifications(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Retorna notificações de um usuário"""
        try:
            if user_id in self.notification_history:
                # Retorna as últimas notificações
                return self.notification_history[user_id][-limit:]
            return []
            
        except Exception as e:
            logger.error(f"Erro ao buscar notificações do usuário {user_id}: {str(e)}")
            return []
    
    def _generate_notification_id(self) -> str:
        """Gera ID único para notificação"""
        import uuid
        return str(uuid.uuid4())
    
    def _save_notification_history(self, notification: Dict, room: str):
        """Salva notificação no histórico"""
        try:
            # Em produção, isso seria salvo no banco de dados
            # Por enquanto, salva em memória
            for user_id, user_rooms in self.user_rooms.items():
                if room in user_rooms:
                    if user_id not in self.notification_history:
                        self.notification_history[user_id] = []
                    
                    self.notification_history[user_id].append(notification)
                    
                    # Limita histórico a 100 notificações por usuário
                    if len(self.notification_history[user_id]) > 100:
                        self.notification_history[user_id] = self.notification_history[user_id][-100:]
                        
        except Exception as e:
            logger.error(f"Erro ao salvar histórico de notificação: {str(e)}")
    
    def get_online_users(self) -> List[str]:
        """Retorna lista de usuários online"""
        return list(self.user_rooms.keys())
    
    def get_user_rooms(self, user_id: str) -> List[str]:
        """Retorna salas de um usuário"""
        return self.user_rooms.get(user_id, [])
    
    def is_user_online(self, user_id: str) -> bool:
        """Verifica se usuário está online"""
        return user_id in self.user_rooms
