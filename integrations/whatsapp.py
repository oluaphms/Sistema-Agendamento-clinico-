import requests
import json
import logging
from datetime import datetime, timedelta
from flask import current_app
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class WhatsAppIntegration:
    """Integração com WhatsApp Business API"""
    
    def __init__(self):
        self.api_key = current_app.config.get('WHATSAPP_API_KEY')
        self.phone_number_id = current_app.config.get('WHATSAPP_PHONE_NUMBER_ID')
        self.access_token = current_app.config.get('WHATSAPP_ACCESS_TOKEN')
        self.base_url = "https://graph.facebook.com/v17.0"
        
    def is_configured(self) -> bool:
        """Verifica se a integração está configurada"""
        return all([self.api_key, self.phone_number_id, self.access_token])
    
    def send_message(self, phone_number: str, message: str, template_name: str = None) -> Dict:
        """Envia mensagem via WhatsApp"""
        if not self.is_configured():
            logger.error("WhatsApp não configurado")
            return {"success": False, "error": "WhatsApp não configurado"}
        
        try:
            # Formata o número do telefone
            formatted_phone = self._format_phone_number(phone_number)
            
            if template_name:
                # Usa template predefinido
                payload = self._create_template_payload(formatted_phone, template_name)
            else:
                # Mensagem personalizada
                payload = self._create_text_payload(formatted_phone, message)
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"Mensagem enviada para {phone_number}")
                return {"success": True, "message_id": response.json().get("messages", [{}])[0].get("id")}
            else:
                logger.error(f"Erro ao enviar mensagem: {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Erro na integração WhatsApp: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def send_appointment_confirmation(self, phone_number: str, appointment_data: Dict) -> Dict:
        """Envia confirmação de agendamento"""
        message = self._format_appointment_confirmation(appointment_data)
        return self.send_message(phone_number, message)
    
    def send_appointment_reminder(self, phone_number: str, appointment_data: Dict) -> Dict:
        """Envia lembrete de agendamento"""
        message = self._format_appointment_reminder(appointment_data)
        return self.send_message(phone_number, message)
    
    def send_appointment_cancellation(self, phone_number: str, appointment_data: Dict) -> Dict:
        """Envia notificação de cancelamento"""
        message = self._format_appointment_cancellation(appointment_data)
        return self.send_message(phone_number, message)
    
    def send_health_tips(self, phone_number: str, tip: str) -> Dict:
        """Envia dicas de saúde personalizadas"""
        message = f"💡 Dica de Saúde:\n\n{tip}\n\nPara mais informações, entre em contato conosco."
        return self.send_message(phone_number, message)
    
    def _format_phone_number(self, phone: str) -> str:
        """Formata número de telefone para o padrão WhatsApp"""
        # Remove caracteres não numéricos
        phone = ''.join(filter(str.isdigit, phone))
        
        # Adiciona código do país se não existir
        if not phone.startswith('55'):
            phone = '55' + phone
            
        return phone
    
    def _create_text_payload(self, phone: str, message: str) -> Dict:
        """Cria payload para mensagem de texto"""
        return {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "text",
            "text": {"body": message}
        }
    
    def _create_template_payload(self, phone: str, template_name: str) -> Dict:
        """Cria payload para template predefinido"""
        return {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "pt_BR"}
            }
        }
    
    def _format_appointment_confirmation(self, appointment: Dict) -> str:
        """Formata mensagem de confirmação de agendamento"""
        data = datetime.strptime(appointment['data'], '%Y-%m-%d').strftime('%d/%m/%Y')
        hora = appointment['hora']
        paciente = appointment['paciente']['nome']
        profissional = appointment['profissional']['nome']
        servico = appointment['servico']['nome']
        
        return f"""✅ *Agendamento Confirmado!*

🏥 *Clínica Avançada*
👤 *Paciente:* {paciente}
👨‍⚕️ *Profissional:* {profissional}
🩺 *Serviço:* {servico}
📅 *Data:* {data}
🕐 *Horário:* {hora}

📍 *Local:* Rua das Clínicas, 123
📞 *Contato:* (11) 99999-9999

⚠️ *Importante:* Chegue com 15 minutos de antecedência.

Para reagendar ou cancelar, responda a esta mensagem ou entre em contato conosco."""
    
    def _format_appointment_reminder(self, appointment: Dict) -> str:
        """Formata mensagem de lembrete de agendamento"""
        data = datetime.strptime(appointment['data'], '%Y-%m-%d').strftime('%d/%m/%Y')
        hora = appointment['hora']
        paciente = appointment['paciente']['nome']
        profissional = appointment['profissional']['nome']
        servico = appointment['servico']['nome']
        
        return f"""⏰ *Lembrete de Consulta*

Olá {paciente}! 

Sua consulta está marcada para:
📅 *Data:* {data}
🕐 *Horário:* {hora}
👨‍⚕️ *Profissional:* {profissional}
🩺 *Serviço:* {servico}

📍 *Local:* Rua das Clínicas, 123

⚠️ *Lembre-se:* Chegue com 15 minutos de antecedência.

Para confirmar, reagendar ou cancelar, responda a esta mensagem."""
    
    def _format_appointment_cancellation(self, appointment: Dict) -> str:
        """Formata mensagem de cancelamento de agendamento"""
        data = datetime.strptime(appointment['data'], '%Y-%m-%d').strftime('%d/%m/%Y')
        hora = appointment['hora']
        paciente = appointment['paciente']['nome']
        servico = appointment['servico']['nome']
        
        return f"""❌ *Agendamento Cancelado*

Olá {paciente},

Seu agendamento foi cancelado:
📅 *Data:* {data}
🕐 *Horário:* {hora}
🩺 *Serviço:* {servico}

Para reagendar, entre em contato conosco:
📞 (11) 99999-9999
💬 Responda a esta mensagem

Agradecemos sua compreensão."""
    
    def get_message_status(self, message_id: str) -> Dict:
        """Verifica status de uma mensagem enviada"""
        if not self.is_configured():
            return {"success": False, "error": "WhatsApp não configurado"}
        
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            url = f"{self.base_url}/{message_id}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return {"success": True, "status": response.json()}
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Erro ao verificar status: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def send_bulk_messages(self, phone_numbers: List[str], message: str) -> List[Dict]:
        """Envia mensagem em massa para múltiplos números"""
        results = []
        for phone in phone_numbers:
            result = self.send_message(phone, message)
            results.append({"phone": phone, "result": result})
            # Aguarda um pouco para evitar rate limiting
            import time
            time.sleep(1)
        return results
