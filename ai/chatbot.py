import openai
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from flask import current_app
import re

logger = logging.getLogger(__name__)

class IntelligentChatbot:
    """Chatbot inteligente com OpenAI para suporte ao paciente"""
    
    def __init__(self):
        self.api_key = current_app.config.get('OPENAI_API_KEY')
        self.client = None
        self.conversation_history = {}
        
        if self.api_key:
            try:
                openai.api_key = self.api_key
                self.client = openai.OpenAI(api_key=self.api_key)
                logger.info("Chatbot OpenAI inicializado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao inicializar OpenAI: {str(e)}")
    
    def is_configured(self) -> bool:
        """Verifica se o chatbot está configurado"""
        return self.client is not None and self.api_key is not None
    
    def get_response(self, user_message: str, user_id: str, context: Dict = None) -> Dict:
        """Processa mensagem do usuário e retorna resposta inteligente"""
        if not self.is_configured():
            return self._get_fallback_response(user_message)
        
        try:
            # Adiciona contexto da conversa
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            # Adiciona mensagem do usuário ao histórico
            self.conversation_history[user_id].append({
                "role": "user",
                "content": user_message
            })
            
            # Prepara contexto do sistema
            system_prompt = self._create_system_prompt(context)
            
            # Limita histórico para não exceder limites da API
            max_history = 10
            if len(self.conversation_history[user_id]) > max_history:
                self.conversation_history[user_id] = self.conversation_history[user_id][-max_history:]
            
            # Monta mensagens para a API
            messages = [{"role": "system", "content": system_prompt}] + self.conversation_history[user_id]
            
            # Chama API da OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            assistant_message = response.choices[0].message.content
            
            # Adiciona resposta ao histórico
            self.conversation_history[user_id].append({
                "role": "assistant",
                "content": assistant_message
            })
            
            # Analisa intenção da mensagem
            intent = self._analyze_intent(user_message)
            
            # Processa ações específicas baseadas na intenção
            actions = self._process_intent(intent, user_message, context)
            
            return {
                "success": True,
                "response": assistant_message,
                "intent": intent,
                "actions": actions,
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"Erro no chatbot: {str(e)}")
            return self._get_fallback_response(user_message)
    
    def _create_system_prompt(self, context: Dict = None) -> str:
        """Cria prompt do sistema para o chatbot"""
        base_prompt = """Você é um assistente virtual inteligente de uma clínica médica chamada "Clínica Avançada". 

Sua função é:
1. Responder perguntas sobre serviços médicos
2. Ajudar com agendamentos de consultas
3. Fornecer informações sobre a clínica
4. Orientar pacientes sobre procedimentos
5. Responder dúvidas sobre convênios médicos

Informações da clínica:
- Endereço: Rua das Clínicas, 123
- Telefone: (11) 99999-9999
- Horário de funcionamento: Segunda a Sexta, 8h às 18h
- Especialidades: Clínico Geral, Cardiologia, Dermatologia, Ginecologia, Ortopedia, Pediatria, Psicologia

Regras importantes:
- Sempre seja cordial e profissional
- Use linguagem clara e acessível
- Não faça diagnósticos médicos
- Para emergências, oriente a procurar um hospital
- Seja empático e compreensivo
- Use emojis ocasionalmente para tornar a conversa mais amigável

Responda sempre em português brasileiro."""
        
        if context:
            if context.get('user_type') == 'patient':
                base_prompt += "\n\nO usuário é um paciente da clínica."
            elif context.get('user_type') == 'professional':
                base_prompt += "\n\nO usuário é um profissional da clínica."
        
        return base_prompt
    
    def _analyze_intent(self, message: str) -> str:
        """Analisa a intenção da mensagem do usuário"""
        message_lower = message.lower()
        
        # Padrões para diferentes intenções
        patterns = {
            'agendamento': [
                r'\b(agendar|marcar|consulta|horário|data|hora)\b',
                r'\b(quando|quanto tempo|disponibilidade)\b'
            ],
            'informacoes_clinica': [
                r'\b(endereço|local|onde|telefone|contato)\b',
                r'\b(horário|funcionamento|aberto|fechado)\b'
            ],
            'especialidades': [
                r'\b(especialidade|médico|doutor|dr\.|dra\.)\b',
                r'\b(cardiologia|dermatologia|ginecologia|ortopedia|pediatria|psicologia)\b'
            ],
            'convênio': [
                r'\b(convênio|plano|seguro|particular|valor|preço)\b',
                r'\b(aceita|cobertura|reembolso)\b'
            ],
            'duvidas_gerais': [
                r'\b(como|o que|quem|qual|dúvida|pergunta)\b',
                r'\b(ajuda|orientação|informação)\b'
            ],
            'emergencia': [
                r'\b(emergência|urgente|grave|dor|sangue|febre alta)\b',
                r'\b(acidente|queda|desmaio|convulsão)\b'
            ]
        }
        
        # Verifica qual padrão corresponde
        for intent, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, message_lower):
                    return intent
        
        return 'conversa_geral'
    
    def _process_intent(self, intent: str, message: str, context: Dict = None) -> List[Dict]:
        """Processa ações baseadas na intenção identificada"""
        actions = []
        
        if intent == 'agendamento':
            actions.append({
                "type": "suggest_appointment",
                "description": "Sugerir agendamento de consulta",
                "data": {
                    "suggested_action": "agendar_consulta",
                    "message": "Gostaria de agendar uma consulta? Posso ajudá-lo com isso."
                }
            })
        
        elif intent == 'emergencia':
            actions.append({
                "type": "emergency_alert",
                "description": "Alerta de emergência médica",
                "data": {
                    "priority": "high",
                    "message": "ATENÇÃO: Para emergências médicas, procure imediatamente um hospital ou ligue para 192 (SAMU)."
                }
            })
        
        elif intent == 'informacoes_clinica':
            actions.append({
                "type": "provide_clinic_info",
                "description": "Fornecer informações da clínica",
                "data": {
                    "info_type": "clinic_details",
                    "message": "Posso fornecer informações sobre endereço, horários e contatos da clínica."
                }
            })
        
        return actions
    
    def _get_fallback_response(self, message: str) -> Dict:
        """Resposta de fallback quando o chatbot não está disponível"""
        fallback_responses = [
            "Desculpe, estou com dificuldades técnicas no momento. Por favor, entre em contato conosco pelo telefone (11) 99999-9999.",
            "Estou temporariamente indisponível. Para atendimento, ligue para (11) 99999-9999 ou envie um email.",
            "Ocorreu um erro técnico. Entre em contato conosco pelo telefone para melhor atendimento."
        ]
        
        import random
        return {
            "success": False,
            "response": random.choice(fallback_responses),
            "intent": "error",
            "actions": [],
            "confidence": 0.0
        }
    
    def suggest_appointment_slots(self, specialty: str, preferred_date: str = None) -> Dict:
        """Sugere horários disponíveis para agendamento"""
        try:
            # Simula busca de horários disponíveis
            available_slots = self._get_available_slots(specialty, preferred_date)
            
            if available_slots:
                return {
                    "success": True,
                    "slots": available_slots,
                    "message": f"Encontrei {len(available_slots)} horários disponíveis para {specialty}."
                }
            else:
                return {
                    "success": False,
                    "message": f"Não há horários disponíveis para {specialty} na data solicitada. Gostaria de ver outras opções?"
                }
                
        except Exception as e:
            logger.error(f"Erro ao sugerir horários: {str(e)}")
            return {
                "success": False,
                "message": "Desculpe, não consegui verificar a disponibilidade. Entre em contato conosco pelo telefone."
            }
    
    def _get_available_slots(self, specialty: str, preferred_date: str = None) -> List[Dict]:
        """Simula busca de horários disponíveis"""
        # Em produção, isso seria integrado com o sistema de agendamentos
        import random
        
        if not preferred_date:
            preferred_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Horários base da clínica
        base_hours = ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"]
        
        # Simula disponibilidade (em produção seria consulta ao banco)
        available_slots = []
        for hour in base_hours:
            if random.random() > 0.3:  # 70% de chance de estar disponível
                available_slots.append({
                    "date": preferred_date,
                    "time": hour,
                    "specialty": specialty,
                    "professional": f"Dr. {specialty.title()}",
                    "duration": 30
                })
        
        return available_slots[:5]  # Retorna máximo 5 horários
    
    def get_health_tips(self, user_profile: Dict = None) -> str:
        """Gera dicas de saúde personalizadas"""
        if not self.is_configured():
            return "Para dicas de saúde personalizadas, consulte um profissional de saúde."
        
        try:
            # Cria prompt para dicas de saúde
            health_prompt = "Gere uma dica de saúde útil e prática em português brasileiro. "
            
            if user_profile:
                if user_profile.get('age'):
                    if user_profile['age'] < 18:
                        health_prompt += "Foque em hábitos saudáveis para jovens. "
                    elif user_profile['age'] > 60:
                        health_prompt += "Foque em cuidados para idosos. "
                
                if user_profile.get('conditions'):
                    health_prompt += f"Considere que o usuário tem: {', '.join(user_profile['conditions'])}. "
            
            health_prompt += "A dica deve ser curta (máximo 2 frases), prática e motivacional."
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": health_prompt}],
                max_tokens=100,
                temperature=0.8
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Erro ao gerar dica de saúde: {str(e)}")
            return "Mantenha uma alimentação equilibrada e pratique exercícios regularmente para uma vida mais saudável."
    
    def analyze_sentiment(self, message: str) -> Dict:
        """Analisa o sentimento da mensagem do usuário"""
        if not self.is_configured():
            return {"sentiment": "neutral", "confidence": 0.0}
        
        try:
            sentiment_prompt = f"Analise o sentimento da seguinte mensagem em português e responda apenas com: POSITIVO, NEGATIVO ou NEUTRO. Mensagem: {message}"
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": sentiment_prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            sentiment = response.choices[0].message.content.strip().upper()
            
            # Mapeia resposta para formato padrão
            sentiment_map = {
                "POSITIVO": "positive",
                "NEGATIVO": "negative",
                "NEUTRO": "neutral"
            }
            
            return {
                "sentiment": sentiment_map.get(sentiment, "neutral"),
                "confidence": 0.8
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar sentimento: {str(e)}")
            return {"sentiment": "neutral", "confidence": 0.0}
    
    def clear_conversation_history(self, user_id: str) -> bool:
        """Limpa histórico de conversa de um usuário"""
        try:
            if user_id in self.conversation_history:
                del self.conversation_history[user_id]
            return True
        except Exception as e:
            logger.error(f"Erro ao limpar histórico: {str(e)}")
            return False
    
    def get_conversation_summary(self, user_id: str) -> Dict:
        """Gera resumo da conversa de um usuário"""
        if user_id not in self.conversation_history:
            return {"summary": "Nenhuma conversa encontrada."}
        
        try:
            # Cria prompt para resumo
            conversation_text = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in self.conversation_history[user_id]
            ])
            
            summary_prompt = f"Faça um resumo conciso desta conversa em português brasileiro, destacando os principais pontos e intenções do usuário:\n\n{conversation_text}"
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": summary_prompt}],
                max_tokens=200,
                temperature=0.5
            )
            
            return {
                "summary": response.choices[0].message.content,
                "message_count": len(self.conversation_history[user_id]),
                "user_id": user_id
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar resumo: {str(e)}")
            return {"summary": "Erro ao gerar resumo da conversa."}
