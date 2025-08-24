import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
from datetime import datetime, timedelta

class NotificationManager:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        self.mail_server = app.config.get('MAIL_SERVER')
        self.mail_port = app.config.get('MAIL_PORT')
        self.mail_username = app.config.get('MAIL_USERNAME')
        self.mail_password = app.config.get('MAIL_PASSWORD')
        self.mail_use_tls = app.config.get('MAIL_USE_TLS', True)
        
        self.whatsapp_api_key = app.config.get('WHATSAPP_API_KEY')
        self.whatsapp_phone = app.config.get('WHATSAPP_PHONE_NUMBER')
    
    def send_email(self, to_email, subject, body, html_body=None):
        """Envia email usando SMTP"""
        if not all([self.mail_server, self.mail_username, self.mail_password]):
            current_app.logger.warning("Configurações de email não encontradas")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.mail_username
            msg['To'] = to_email
            
            # Adiciona versão texto e HTML
            text_part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            if html_body:
                html_part = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Conecta ao servidor SMTP
            server = smtplib.SMTP(self.mail_server, self.mail_port)
            if self.mail_use_tls:
                server.starttls()
            
            server.login(self.mail_username, self.mail_password)
            server.send_message(msg)
            server.quit()
            
            current_app.logger.info(f"Email enviado para {to_email}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Erro ao enviar email: {str(e)}")
            return False
    
    def send_whatsapp(self, phone_number, message):
        """Envia mensagem via WhatsApp Business API"""
        if not all([self.whatsapp_api_key, self.whatsapp_phone]):
            current_app.logger.warning("Configurações de WhatsApp não encontradas")
            return False
        
        try:
            # Exemplo usando WhatsApp Business API
            # Você precisará adaptar para a API específica que usar
            url = "https://graph.facebook.com/v17.0/YOUR_PHONE_NUMBER_ID/messages"
            
            headers = {
                "Authorization": f"Bearer {self.whatsapp_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {"body": message}
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                current_app.logger.info(f"WhatsApp enviado para {phone_number}")
                return True
            else:
                current_app.logger.error(f"Erro WhatsApp API: {response.text}")
                return False
                
        except Exception as e:
            current_app.logger.error(f"Erro ao enviar WhatsApp: {str(e)}")
            return False
    
    def send_appointment_confirmation(self, agendamento, paciente, profissional, servico):
        """Envia confirmação de agendamento"""
        subject = f"Confirmação de Agendamento - {servico.nome}"
        
        # Formata data e hora
        data_obj = datetime.strptime(agendamento.data, "%Y-%m-%d")
        data_formatada = data_obj.strftime("%d/%m/%Y")
        
        # Corpo do email em texto
        body = f"""
Olá {paciente.nome},

Seu agendamento foi confirmado com sucesso!

Detalhes:
- Serviço: {servico.nome}
- Profissional: {profissional.nome}
- Data: {data_formatada}
- Horário: {agendamento.hora}
- Duração: {agendamento.duracao} minutos

Por favor, chegue com 10 minutos de antecedência.

Em caso de cancelamento, entre em contato conosco com pelo menos 24h de antecedência.

Atenciosamente,
Equipe da Clínica
        """
        
        # Corpo do email em HTML
        html_body = f"""
        <html>
        <body>
            <h2>Confirmação de Agendamento</h2>
            <p>Olá <strong>{paciente.nome}</strong>,</p>
            <p>Seu agendamento foi confirmado com sucesso!</p>
            
            <h3>Detalhes:</h3>
            <ul>
                <li><strong>Serviço:</strong> {servico.nome}</li>
                <li><strong>Profissional:</strong> {profissional.nome}</li>
                <li><strong>Data:</strong> {data_formatada}</li>
                <li><strong>Horário:</strong> {agendamento.hora}</li>
                <li><strong>Duração:</strong> {agendamento.duracao} minutos</li>
            </ul>
            
            <p><strong>Importante:</strong> Chegue com 10 minutos de antecedência.</p>
            
            <p>Em caso de cancelamento, entre em contato conosco com pelo menos 24h de antecedência.</p>
            
            <p>Atenciosamente,<br>
            <strong>Equipe da Clínica</strong></p>
        </body>
        </html>
        """
        
        # Envia email
        if paciente.email:
            self.send_email(paciente.email, subject, body, html_body)
        
        # Envia WhatsApp
        if paciente.telefone:
            whatsapp_message = f"Olá {paciente.nome}! Seu agendamento para {servico.nome} com {profissional.nome} foi confirmado para {data_formatada} às {agendamento.hora}. Chegue com 10 min de antecedência."
            self.send_whatsapp(paciente.telefone, whatsapp_message)
    
    def send_appointment_reminder(self, agendamento, paciente, profissional, servico):
        """Envia lembrete de agendamento (24h antes)"""
        subject = f"Lembrete de Agendamento - {servico.nome}"
        
        data_obj = datetime.strptime(agendamento.data, "%Y-%m-%d")
        data_formatada = data_obj.strftime("%d/%m/%Y")
        
        body = f"""
Olá {paciente.nome},

Lembrete do seu agendamento amanhã!

Detalhes:
- Serviço: {servico.nome}
- Profissional: {profissional.nome}
- Data: {data_formatada}
- Horário: {agendamento.hora}

Não se esqueça de chegar com 10 minutos de antecedência.

Atenciosamente,
Equipe da Clínica
        """
        
        if paciente.email:
            self.send_email(paciente.email, subject, body)
        
        if paciente.telefone:
            whatsapp_message = f"Olá {paciente.nome}! Lembrete: seu agendamento para {servico.nome} é amanhã ({data_formatada}) às {agendamento.hora}. Chegue com 10 min de antecedência."
            self.send_whatsapp(paciente.telefone, whatsapp_message)
    
    def send_appointment_cancellation(self, agendamento, paciente, profissional, servico):
        """Envia notificação de cancelamento"""
        subject = f"Agendamento Cancelado - {servico.nome}"
        
        data_obj = datetime.strptime(agendamento.data, "%Y-%m-%d")
        data_formatada = data_obj.strftime("%d/%m/%Y")
        
        body = f"""
Olá {paciente.nome},

Seu agendamento foi cancelado.

Detalhes do agendamento cancelado:
- Serviço: {servico.nome}
- Profissional: {profissional.nome}
- Data: {data_formatada}
- Horário: {agendamento.hora}

Para reagendar, entre em contato conosco.

Atenciosamente,
Equipe da Clínica
        """
        
        if paciente.email:
            self.send_email(paciente.email, subject, body)
        
        if paciente.telefone:
            whatsapp_message = f"Olá {paciente.nome}! Seu agendamento para {servico.nome} com {profissional.nome} em {data_formatada} às {agendamento.hora} foi cancelado. Para reagendar, entre em contato conosco."
            self.send_whatsapp(paciente.telefone, whatsapp_message)

# Instância global
notifications = NotificationManager()
