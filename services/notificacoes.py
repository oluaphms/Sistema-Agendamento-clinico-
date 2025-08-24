"""
Sistema de Notificações - Sistema Clínica
Integração com WhatsApp e notificações automáticas
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TipoNotificacao(Enum):
    """Tipos de notificação disponíveis"""
    CONFIRMACAO_AGENDAMENTO = "confirmacao_agendamento"
    LEMBRETE_24H = "lembrete_24h"
    LEMBRETE_1H = "lembrete_1h"
    AGRADECIMENTO = "agradecimento"
    LEMBRETE_ADICIONAL = "lembrete_adicional"
    SUGESTAO_REAGENDAMENTO = "sugestao_reagendamento"
    RESUMO_DIARIO = "resumo_diario"
    CONFIRMACAO_PRESENCA = "confirmacao_presenca"

class StatusNotificacao(Enum):
    """Status das notificações"""
    PENDENTE = "pendente"
    ENVIADA = "enviada"
    ENTREGUE = "entregue"
    FALHOU = "falhou"
    CANCELADA = "cancelada"

@dataclass
class Notificacao:
    """Estrutura de dados para notificações"""
    id: str
    tipo: TipoNotificacao
    paciente_id: int
    agendamento_id: int
    telefone: str
    mensagem: str
    status: StatusNotificacao
    data_envio: datetime
    data_criacao: datetime
    tentativas: int = 0
    erro: Optional[str] = None
    resposta_paciente: Optional[str] = None

class GerenciadorNotificacoes:
    """Gerenciador principal de notificações"""
    
    def __init__(self):
        self.whatsapp_service = WhatsAppService()
        self.templates = self._carregar_templates()
        self.configuracoes = self._carregar_configuracoes()
    
    def _carregar_templates(self) -> Dict[str, str]:
        """Carrega templates de mensagens"""
        return {
            TipoNotificacao.CONFIRMACAO_AGENDAMENTO.value: """
🎉 *Agendamento Confirmado!*

Olá {nome_paciente}! 

Sua consulta foi agendada com sucesso:
📅 Data: {data}
🕐 Horário: {horario}
👨‍⚕️ Profissional: {profissional}
🏥 Especialidade: {especialidade}

📍 Local: {endereco_clinica}

Para confirmar sua presença, responda:
✅ SIM - Confirmo presença
🔄 REAGENDAR - Quero outro horário
❌ CANCELAR - Cancelar consulta

Qualquer dúvida, entre em contato: {telefone_clinica}

Agradecemos a confiança! 🙏
            """,
            
            TipoNotificacao.LEMBRETE_24H.value: """
⏰ *Lembrete de Consulta*

Olá {nome_paciente}!

Sua consulta é *AMANHÃ*:
📅 Data: {data}
🕐 Horário: {horario}
👨‍⚕️ Profissional: {profissional}

📍 Local: {endereco_clinica}

⚠️ *Importante:*
• Chegue 10 minutos antes
• Traga documentos necessários
• Use máscara (se necessário)

Para confirmar presença, responda:
✅ SIM - Estarei presente
🔄 REAGENDAR - Preciso de outro horário
❌ CANCELAR - Não poderei ir

Até amanhã! 👋
            """,
            
            TipoNotificacao.LEMBRETE_1H.value: """
🚨 *Consulta em 1 Hora!*

Olá {nome_paciente}!

Sua consulta é em *1 HORA*:
🕐 Horário: {horario}
👨‍⚕️ Profissional: {profissional}

📍 Local: {endereco_clinica}

🎯 *Checklist:*
• Documentos ✓
• Chegar 10 min antes ✓
• Máscara (se necessário) ✓

Estamos te aguardando! 👨‍⚕️

Precisa de ajuda? Ligue: {telefone_clinica}
            """,
            
            TipoNotificacao.AGRADECIMENTO.value: """
🙏 *Obrigado pela Consulta!*

Olá {nome_paciente}!

Agradecemos por escolher nossa clínica! 

⭐ *Como foi sua experiência?*
Responda de 1 a 5 estrelas:
1 ⭐ - Ruim
2 ⭐⭐ - Regular  
3 ⭐⭐⭐ - Boa
4 ⭐⭐⭐⭐ - Muito boa
5 ⭐⭐⭐⭐⭐ - Excelente

📋 *Próximos passos:*
• Retorno agendado para: {data_retorno}
• Exames solicitados: {exames}
• Prescrições: {prescricoes}

💡 *Dúvidas?* Entre em contato: {telefone_clinica}

Até a próxima! 👋
            """,
            
            TipoNotificacao.LEMBRETE_ADICIONAL.value: """
🔔 *Lembrete Importante*

Olá {nome_paciente}!

Ainda não recebemos sua confirmação para a consulta de amanhã:
📅 Data: {data}
🕐 Horário: {horario}
👨‍⚕️ Profissional: {profissional}

⚠️ *Confirme agora:*
✅ SIM - Estarei presente
🔄 REAGENDAR - Outro horário
❌ CANCELAR - Não poderei ir

*Sem confirmação, sua consulta pode ser cancelada.*

Precisa de ajuda? Ligue: {telefone_clinica}
            """,
            
            TipoNotificacao.SUGESTAO_REAGENDAMENTO.value: """
🔄 *Reagendar Consulta?*

Olá {nome_paciente}!

Notamos que você não compareceu à consulta de hoje:
📅 Data: {data}
🕐 Horário: {horario}

💡 *Sugestões de horários disponíveis:*
• {sugestao1}
• {sugestao2}
• {sugestao3}

Para reagendar, responda:
🔄 REAGENDAR - Quero novo horário
📞 LIGAR - Falar com atendente
❌ CANCELAR - Não quero reagendar

Estamos aqui para ajudar! 🤝
            """,
            
            TipoNotificacao.RESUMO_DIARIO.value: """
📊 *Resumo do Dia - {data}*

Olá Dr(a). {profissional}!

📋 *Agenda de Hoje:*
{agenda_dia}

📈 *Estatísticas:*
• Total de consultas: {total_consultas}
• Confirmadas: {confirmadas}
• Pendentes: {pendentes}
• Canceladas: {canceladas}

💡 *Lembretes:*
• Verificar prontuários antes das consultas
• Preparar materiais necessários
• Confirmar presença dos pacientes

Bom trabalho! 👨‍⚕️💪
            """,
            
            TipoNotificacao.CONFIRMACAO_PRESENCA.value: """
✅ *Confirmação de Presença*

Olá Dr(a). {profissional}!

O paciente {nome_paciente} confirmou presença para:
🕐 Horário: {horario}
📋 Tipo: {tipo_consulta}

📱 *Resposta do paciente:* "{resposta}"

Paciente está a caminho! 🚶‍♀️

Precisa de mais informações? Consulte o sistema.
            """
        }
    
    def _carregar_configuracoes(self) -> Dict[str, any]:
        """Carrega configurações do sistema"""
        return {
            "lembretes_ativos": True,
            "lembrete_24h": True,
            "lembrete_1h": True,
            "lembrete_adicional": True,
            "sugestao_reagendamento": True,
            "resumo_diario_profissionais": True,
            "horario_envio_lembrete_24h": "18:00",
            "horario_envio_lembrete_1h": "08:00",
            "tempo_espera_confirmacao": 6,  # horas
            "telefone_clinica": "+55 11 99999-9999",
            "endereco_clinica": "Rua das Clínicas, 123 - Centro",
            "nome_clinica": "Clínica Saúde Total"
        }
    
    def notificar_agendamento_criado(self, agendamento: Dict) -> bool:
        """Envia notificação de confirmação após agendamento"""
        try:
            mensagem = self._formatar_mensagem(
                TipoNotificacao.CONFIRMACAO_AGENDAMENTO.value,
                agendamento
            )
            
            notificacao = Notificacao(
                id=self._gerar_id(),
                tipo=TipoNotificacao.CONFIRMACAO_AGENDAMENTO,
                paciente_id=agendamento['paciente_id'],
                agendamento_id=agendamento['id'],
                telefone=agendamento['telefone_paciente'],
                mensagem=mensagem,
                status=StatusNotificacao.PENDENTE,
                data_envio=datetime.now(),
                data_criacao=datetime.now()
            )
            
            # Salvar no banco
            self._salvar_notificacao(notificacao)
            
            # Enviar via WhatsApp
            sucesso = self.whatsapp_service.enviar_mensagem(
                notificacao.telefone,
                notificacao.mensagem
            )
            
            if sucesso:
                notificacao.status = StatusNotificacao.ENVIADA
                self._atualizar_status_notificacao(notificacao.id, StatusNotificacao.ENVIADA)
                logger.info(f"Notificação de agendamento enviada para {agendamento['telefone_paciente']}")
                return True
            else:
                notificacao.status = StatusNotificacao.FALHOU
                self._atualizar_status_notificacao(notificacao.id, StatusNotificacao.FALHOU)
                logger.error(f"Falha ao enviar notificação para {agendamento['telefone_paciente']}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de agendamento: {str(e)}")
            return False
    
    def agendar_lembretes(self, agendamento: Dict) -> bool:
        """Agenda lembretes automáticos para um agendamento"""
        try:
            data_consulta = datetime.strptime(agendamento['data'], '%Y-%m-%d')
            horario_consulta = datetime.strptime(agendamento['horario'], '%H:%M')
            
            # Lembrete 24h antes
            if self.configuracoes["lembrete_24h"]:
                data_lembrete_24h = data_consulta - timedelta(days=1)
                horario_lembrete = datetime.strptime(
                    self.configuracoes["horario_envio_lembrete_24h"], 
                    '%H:%M'
                )
                
                self._agendar_notificacao(
                    agendamento,
                    TipoNotificacao.LEMBRETE_24H,
                    data_lembrete_24h.replace(
                        hour=horario_lembrete.hour,
                        minute=horario_lembrete.minute
                    )
                )
            
            # Lembrete 1h antes
            if self.configuracoes["lembrete_1h"]:
                data_lembrete_1h = data_consulta.replace(
                    hour=horario_consulta.hour,
                    minute=horario_consulta.minute
                ) - timedelta(hours=1)
                
                self._agendar_notificacao(
                    agendamento,
                    TipoNotificacao.LEMBRETE_1H,
                    data_lembrete_1h
                )
            
            # Lembrete adicional se não confirmar
            if self.configuracoes["lembrete_adicional"]:
                data_lembrete_adicional = data_consulta - timedelta(
                    hours=self.configuracoes["tempo_espera_confirmacao"]
                )
                
                self._agendar_notificacao(
                    agendamento,
                    TipoNotificacao.LEMBRETE_ADICIONAL,
                    data_lembrete_adicional
                )
            
            logger.info(f"Lembretes agendados para agendamento {agendamento['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao agendar lembretes: {str(e)}")
            return False
    
    def notificar_falta(self, agendamento: Dict) -> bool:
        """Envia sugestão de reagendamento após falta"""
        try:
            if not self.configuracoes["sugestao_reagendamento"]:
                return True
            
            mensagem = self._formatar_mensagem(
                TipoNotificacao.SUGESTAO_REAGENDAMENTO.value,
                agendamento
            )
            
            notificacao = Notificacao(
                id=self._gerar_id(),
                tipo=TipoNotificacao.SUGESTAO_REAGENDAMENTO,
                paciente_id=agendamento['paciente_id'],
                agendamento_id=agendamento['id'],
                telefone=agendamento['telefone_paciente'],
                mensagem=mensagem,
                status=StatusNotificacao.PENDENTE,
                data_envio=datetime.now(),
                data_criacao=datetime.now()
            )
            
            self._salvar_notificacao(notificacao)
            
            sucesso = self.whatsapp_service.enviar_mensagem(
                notificacao.telefone,
                notificacao.mensagem
            )
            
            if sucesso:
                notificacao.status = StatusNotificacao.ENVIADA
                self._atualizar_status_notificacao(notificacao.id, StatusNotificacao.ENVIADA)
                return True
            else:
                notificacao.status = StatusNotificacao.FALHOU
                self._atualizar_status_notificacao(notificacao.id, StatusNotificacao.FALHOU)
                return False
                
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de falta: {str(e)}")
            return False
    
    def notificar_agradecimento(self, agendamento: Dict) -> bool:
        """Envia agradecimento após consulta realizada"""
        try:
            mensagem = self._formatar_mensagem(
                TipoNotificacao.AGRADECIMENTO.value,
                agendamento
            )
            
            notificacao = Notificacao(
                id=self._gerar_id(),
                tipo=TipoNotificacao.AGRADECIMENTO,
                paciente_id=agendamento['paciente_id'],
                agendamento_id=agendamento['id'],
                telefone=agendamento['telefone_paciente'],
                mensagem=mensagem,
                status=StatusNotificacao.PENDENTE,
                data_envio=datetime.now(),
                data_criacao=datetime.now()
            )
            
            self._salvar_notificacao(notificacao)
            
            sucesso = self.whatsapp_service.enviar_mensagem(
                notificacao.telefone,
                notificacao.mensagem
            )
            
            if sucesso:
                notificacao.status = StatusNotificacao.ENVIADA
                self._atualizar_status_notificacao(notificacao.id, StatusNotificacao.ENVIADA)
                return True
            else:
                notificacao.status = StatusNotificacao.FALHOU
                self._atualizar_status_notificacao(notificacao.id, StatusNotificacao.FALHOU)
                return False
                
        except Exception as e:
            logger.error(f"Erro ao enviar agradecimento: {str(e)}")
            return False
    
    def enviar_resumo_diario_profissional(self, profissional_id: int, data: str) -> bool:
        """Envia resumo diário para o profissional"""
        try:
            if not self.configuracoes["resumo_diario_profissionais"]:
                return True
            
            # Buscar dados do profissional e agenda do dia
            dados_profissional = self._buscar_dados_profissional(profissional_id)
            agenda_dia = self._buscar_agenda_dia(profissional_id, data)
            
            if not dados_profissional or not agenda_dia:
                return False
            
            mensagem = self._formatar_mensagem(
                TipoNotificacao.RESUMO_DIARIO.value,
                {
                    "profissional": dados_profissional['nome'],
                    "data": data,
                    "agenda_dia": agenda_dia['resumo'],
                    "total_consultas": agenda_dia['total'],
                    "confirmadas": agenda_dia['confirmadas'],
                    "pendentes": agenda_dia['pendentes'],
                    "canceladas": agenda_dia['canceladas']
                }
            )
            
            notificacao = Notificacao(
                id=self._gerar_id(),
                tipo=TipoNotificacao.RESUMO_DIARIO,
                paciente_id=0,  # Não é paciente
                agendamento_id=0,  # Não é agendamento específico
                telefone=dados_profissional['telefone'],
                mensagem=mensagem,
                status=StatusNotificacao.PENDENTE,
                data_envio=datetime.now(),
                data_criacao=datetime.now()
            )
            
            self._salvar_notificacao(notificacao)
            
            sucesso = self.whatsapp_service.enviar_mensagem(
                notificacao.telefone,
                notificacao.mensagem
            )
            
            if sucesso:
                notificacao.status = StatusNotificacao.ENVIADA
                self._atualizar_status_notificacao(notificacao.id, StatusNotificacao.ENVIADA)
                return True
            else:
                notificacao.status = StatusNotificacao.FALHOU
                self._atualizar_status_notificacao(notificacao.id, StatusNotificacao.FALHOU)
                return False
                
        except Exception as e:
            logger.error(f"Erro ao enviar resumo diário: {str(e)}")
            return False
    
    def _formatar_mensagem(self, template: str, dados: Dict) -> str:
        """Formata mensagem usando template e dados"""
        try:
            mensagem = self.templates[template]
            
            # Substituir variáveis do template
            for chave, valor in dados.items():
                placeholder = f"{{{chave}}}"
                if placeholder in mensagem:
                    mensagem = mensagem.replace(placeholder, str(valor))
            
            # Adicionar informações da clínica
            mensagem = mensagem.replace("{telefone_clinica}", self.configuracoes["telefone_clinica"])
            mensagem = mensagem.replace("{endereco_clinica}", self.configuracoes["endereco_clinica"])
            mensagem = mensagem.replace("{nome_clinica}", self.configuracoes["nome_clinica"])
            
            return mensagem.strip()
            
        except Exception as e:
            logger.error(f"Erro ao formatar mensagem: {str(e)}")
            return "Erro ao formatar mensagem"
    
    def _agendar_notificacao(self, agendamento: Dict, tipo: TipoNotificacao, data_envio: datetime):
        """Agenda uma notificação para envio futuro"""
        try:
            mensagem = self._formatar_mensagem(tipo.value, agendamento)
            
            notificacao = Notificacao(
                id=self._gerar_id(),
                tipo=tipo,
                paciente_id=agendamento['paciente_id'],
                agendamento_id=agendamento['id'],
                telefone=agendamento['telefone_paciente'],
                mensagem=mensagem,
                status=StatusNotificacao.PENDENTE,
                data_envio=data_envio,
                data_criacao=datetime.now()
            )
            
            self._salvar_notificacao(notificacao)
            logger.info(f"Notificação {tipo.value} agendada para {data_envio}")
            
        except Exception as e:
            logger.error(f"Erro ao agendar notificação: {str(e)}")
    
    def _gerar_id(self) -> str:
        """Gera ID único para notificação"""
        return f"notif_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(datetime.now()))}"
    
    def _salvar_notificacao(self, notificacao: Notificacao):
        """Salva notificação no banco de dados"""
        # TODO: Implementar salvamento no banco
        # Por enquanto, apenas log
        logger.info(f"Notificação salva: {notificacao.id}")
    
    def _atualizar_status_notificacao(self, notificacao_id: str, status: StatusNotificacao):
        """Atualiza status da notificação no banco"""
        # TODO: Implementar atualização no banco
        logger.info(f"Status da notificação {notificacao_id} atualizado para {status.value}")
    
    def _buscar_dados_profissional(self, profissional_id: int) -> Optional[Dict]:
        """Busca dados do profissional"""
        # TODO: Implementar busca no banco
        # Por enquanto, dados mock
        return {
            "id": profissional_id,
            "nome": "Dr. João Silva",
            "telefone": "+55 11 99999-9999"
        }
    
    def _buscar_agenda_dia(self, profissional_id: int, data: str) -> Optional[Dict]:
        """Busca agenda do dia para o profissional"""
        # TODO: Implementar busca no banco
        # Por enquanto, dados mock
        return {
            "resumo": "09:00 - Consulta Dr. João\n10:00 - Exame Dra. Maria\n11:00 - Retorno Dr. Carlos",
            "total": 3,
            "confirmadas": 2,
            "pendentes": 1,
            "canceladas": 0
        }
    
    def processar_resposta_paciente(self, telefone: str, mensagem: str) -> Dict:
        """Processa resposta do paciente via WhatsApp"""
        try:
            mensagem_lower = mensagem.lower().strip()
            
            if mensagem_lower in ['sim', 'confirmo', 'ok', 'confirmado']:
                return {
                    "acao": "confirmar_presenca",
                    "mensagem": "Presença confirmada! Obrigado por confirmar. Até a consulta! 👋"
                }
            
            elif mensagem_lower in ['reagendar', 'remarcar', 'outro horário']:
                return {
                    "acao": "reagendar",
                    "mensagem": "Vamos reagendar sua consulta! Em breve um atendente entrará em contato para definir o novo horário. 📅"
                }
            
            elif mensagem_lower in ['cancelar', 'cancelado', 'não poderei']:
                return {
                    "acao": "cancelar",
                    "mensagem": "Consulta cancelada conforme solicitado. Para reagendar, entre em contato conosco. 📞"
                }
            
            elif mensagem_lower in ['1', '2', '3', '4', '5']:
                return {
                    "acao": "avaliacao",
                    "nota": int(mensagem_lower),
                    "mensagem": f"Obrigado pela avaliação de {mensagem_lower} estrelas! Sua opinião é muito importante para nós. ⭐"
                }
            
            else:
                return {
                    "acao": "nao_entendi",
                    "mensagem": "Desculpe, não entendi sua resposta. Para confirmar presença responda SIM, para reagendar responda REAGENDAR, ou para cancelar responda CANCELAR. 🤔"
                }
                
        except Exception as e:
            logger.error(f"Erro ao processar resposta do paciente: {str(e)}")
            return {
                "acao": "erro",
                "mensagem": "Desculpe, ocorreu um erro. Entre em contato conosco pelo telefone."
            }
    
    def obter_estatisticas(self) -> Dict:
        """Obtém estatísticas das notificações"""
        try:
            # TODO: Implementar busca no banco
            # Por enquanto, dados mock
            return {
                "total_enviadas": 150,
                "total_entregues": 142,
                "total_falharam": 8,
                "taxa_entrega": 94.7,
                "total_respostas": 89,
                "taxa_resposta": 62.7,
                "confirmacoes": 67,
                "reagendamentos": 15,
                "cancelamentos": 7
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {}
    
    def obter_historico(self, filtros: Dict = None) -> List[Dict]:
        """Obtém histórico de notificações"""
        try:
            # TODO: Implementar busca no banco
            # Por enquanto, dados mock
            return [
                {
                    "id": "notif_001",
                    "tipo": "confirmacao_agendamento",
                    "paciente": "João Silva",
                    "telefone": "+55 11 99999-9999",
                    "status": "enviada",
                    "data_envio": "2025-01-19 10:30:00",
                    "resposta": "SIM"
                }
            ]
        except Exception as e:
            logger.error(f"Erro ao obter histórico: {str(e)}")
            return []
