import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from flask import current_app
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json

logger = logging.getLogger(__name__)

class GoogleIntegration:
    """Integração com Google Calendar e Google Sheets"""
    
    # Escopo das APIs do Google
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    def __init__(self):
        self.client_id = current_app.config.get('GOOGLE_CLIENT_ID')
        self.client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET')
        self.calendar_id = current_app.config.get('GOOGLE_CALENDAR_ID')
        self.credentials = None
        self.calendar_service = None
        self.sheets_service = None
        
    def is_configured(self) -> bool:
        """Verifica se a integração está configurada"""
        return all([self.client_id, self.client_secret])
    
    def authenticate(self) -> bool:
        """Autentica com Google OAuth2"""
        if not self.is_configured():
            logger.error("Google não configurado")
            return False
        
        try:
            # Verifica se já existe token salvo
            token_path = 'token.json'
            if os.path.exists(token_path):
                self.credentials = Credentials.from_authorized_user_file(token_path, self.SCOPES)
            
            # Se não há credenciais válidas, faz o fluxo de autenticação
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_config(
                        {
                            "installed": {
                                "client_id": self.client_id,
                                "client_secret": self.client_secret,
                                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                "token_uri": "https://oauth2.googleapis.com/token",
                                "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
                            }
                        },
                        self.SCOPES
                    )
                    self.credentials = flow.run_local_server(port=0)
                
                # Salva as credenciais para próxima execução
                with open(token_path, 'w') as token:
                    token.write(self.credentials.to_json())
            
            # Inicializa os serviços
            self.calendar_service = build('calendar', 'v3', credentials=self.credentials)
            self.sheets_service = build('sheets', 'v4', credentials=self.credentials)
            
            logger.info("Autenticação Google realizada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro na autenticação Google: {str(e)}")
            return False
    
    def create_calendar_event(self, appointment_data: Dict) -> Dict:
        """Cria evento no Google Calendar"""
        if not self.authenticate():
            return {"success": False, "error": "Falha na autenticação"}
        
        try:
            # Formata data e hora
            start_time = datetime.strptime(f"{appointment_data['data']} {appointment_data['hora']}", "%Y-%m-%d %H:%M")
            end_time = start_time + timedelta(minutes=appointment_data.get('duracao', 30))
            
            event = {
                'summary': f"{appointment_data['paciente']['nome']} - {appointment_data['servico']['nome']}",
                'description': f"""
                Paciente: {appointment_data['paciente']['nome']}
                Profissional: {appointment_data['profissional']['nome']}
                Serviço: {appointment_data['servico']['nome']}
                Observações: {appointment_data.get('observacoes', 'Nenhuma')}
                """,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'attendees': [
                    {'email': appointment_data['paciente'].get('email')},
                    {'email': appointment_data['profissional'].get('email')}
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 dia antes
                        {'method': 'popup', 'minutes': 60},       # 1 hora antes
                    ],
                },
                'colorId': '1',  # Azul
                'status': 'confirmed'
            }
            
            # Remove campos vazios
            event = {k: v for k, v in event.items() if v}
            
            calendar_id = self.calendar_id or 'primary'
            event_result = self.calendar_service.events().insert(
                calendarId=calendar_id,
                body=event,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"Evento criado no Google Calendar: {event_result.get('id')}")
            return {
                "success": True,
                "event_id": event_result.get('id'),
                "html_link": event_result.get('htmlLink')
            }
            
        except HttpError as e:
            logger.error(f"Erro HTTP ao criar evento: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Erro ao criar evento: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def update_calendar_event(self, event_id: str, appointment_data: Dict) -> Dict:
        """Atualiza evento existente no Google Calendar"""
        if not self.authenticate():
            return {"success": False, "error": "Falha na autenticação"}
        
        try:
            # Busca o evento existente
            calendar_id = self.calendar_id or 'primary'
            event = self.calendar_service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            # Atualiza os dados
            start_time = datetime.strptime(f"{appointment_data['data']} {appointment_data['hora']}", "%Y-%m-%d %H:%M")
            end_time = start_time + timedelta(minutes=appointment_data.get('duracao', 30))
            
            event['summary'] = f"{appointment_data['paciente']['nome']} - {appointment_data['servico']['nome']}"
            event['start']['dateTime'] = start_time.isoformat()
            event['end']['dateTime'] = end_time.isoformat()
            
            # Atualiza o evento
            updated_event = self.calendar_service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"Evento atualizado no Google Calendar: {event_id}")
            return {"success": True, "event": updated_event}
            
        except HttpError as e:
            logger.error(f"Erro HTTP ao atualizar evento: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Erro ao atualizar evento: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def delete_calendar_event(self, event_id: str) -> Dict:
        """Remove evento do Google Calendar"""
        if not self.authenticate():
            return {"success": False, "error": "Falha na autenticação"}
        
        try:
            calendar_id = self.calendar_id or 'primary'
            self.calendar_service.events().delete(
                calendarId=calendar_id,
                eventId=event_id,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"Evento removido do Google Calendar: {event_id}")
            return {"success": True}
            
        except HttpError as e:
            logger.error(f"Erro HTTP ao remover evento: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Erro ao remover evento: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def sync_appointments_to_sheets(self, appointments: List[Dict], spreadsheet_id: str = None) -> Dict:
        """Sincroniza agendamentos para Google Sheets"""
        if not self.authenticate():
            return {"success": False, "error": "Falha na autenticação"}
        
        try:
            # Cria nova planilha se não fornecida
            if not spreadsheet_id:
                spreadsheet = self.sheets_service.spreadsheets().create(body={
                    'properties': {
                        'title': f'Agendamentos Clínica - {datetime.now().strftime("%d/%m/%Y")}'
                    },
                    'sheets': [
                        {
                            'properties': {
                                'title': 'Agendamentos',
                                'gridProperties': {
                                    'rowCount': 1000,
                                    'columnCount': 10
                                }
                            }
                        }
                    ]
                }).execute()
                spreadsheet_id = spreadsheet['spreadsheetId']
            
            # Prepara dados para a planilha
            values = [
                ['ID', 'Data', 'Hora', 'Paciente', 'Profissional', 'Serviço', 'Status', 'Valor', 'Observações', 'Data Criação']
            ]
            
            for apt in appointments:
                values.append([
                    apt['id'],
                    apt['data'],
                    apt['hora'],
                    apt['paciente']['nome'],
                    apt['profissional']['nome'],
                    apt['servico']['nome'],
                    apt['status'],
                    apt.get('valor_pago', 0),
                    apt.get('observacoes', ''),
                    datetime.now().strftime("%d/%m/%Y %H:%M")
                ])
            
            # Atualiza a planilha
            range_name = 'Agendamentos!A1'
            body = {'values': values}
            
            result = self.sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Planilha atualizada: {result.get('updatedCells')} células")
            return {
                "success": True,
                "spreadsheet_id": spreadsheet_id,
                "updated_cells": result.get('updatedCells')
            }
            
        except HttpError as e:
            logger.error(f"Erro HTTP ao sincronizar planilha: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Erro ao sincronizar planilha: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_calendar_events(self, start_date: str, end_date: str) -> Dict:
        """Busca eventos do Google Calendar em um período"""
        if not self.authenticate():
            return {"success": False, "error": "Falha na autenticação"}
        
        try:
            calendar_id = self.calendar_id or 'primary'
            
            events_result = self.calendar_service.events().list(
                calendarId=calendar_id,
                timeMin=start_date,
                timeMax=end_date,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            logger.info(f"Eventos encontrados: {len(events)}")
            return {
                "success": True,
                "events": events,
                "count": len(events)
            }
            
        except HttpError as e:
            logger.error(f"Erro HTTP ao buscar eventos: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Erro ao buscar eventos: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def create_recurring_event(self, appointment_data: Dict, recurrence: str) -> Dict:
        """Cria evento recorrente no Google Calendar"""
        if not self.authenticate():
            return {"success": False, "error": "Falha na autenticação"}
        
        try:
            start_time = datetime.strptime(f"{appointment_data['data']} {appointment_data['hora']}", "%Y-%m-%d %H:%M")
            end_time = start_time + timedelta(minutes=appointment_data.get('duracao', 30))
            
            event = {
                'summary': f"{appointment_data['paciente']['nome']} - {appointment_data['servico']['nome']} (Recorrente)",
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'recurrence': [recurrence],  # Ex: 'RRULE:FREQ=WEEKLY;COUNT=10'
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 60},
                    ],
                }
            }
            
            calendar_id = self.calendar_id or 'primary'
            event_result = self.calendar_service.events().insert(
                calendarId=calendar_id,
                body=event,
                sendUpdates='all'
            ).execute()
            
            logger.info(f"Evento recorrente criado: {event_result.get('id')}")
            return {
                "success": True,
                "event_id": event_result.get('id'),
                "html_link": event_result.get('htmlLink')
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar evento recorrente: {str(e)}")
            return {"success": False, "error": str(e)}
