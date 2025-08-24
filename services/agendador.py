"""
Agendador de Tarefas - Sistema Clínica
Gerencia notificações automáticas e lembretes
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import schedule

# Configuração de logging
logger = logging.getLogger(__name__)

class TipoTarefa(Enum):
    """Tipos de tarefas agendadas"""
    LEMBRETE_24H = "lembrete_24h"
    LEMBRETE_1H = "lembrete_1h"
    LEMBRETE_ADICIONAL = "lembrete_adicional"
    RESUMO_DIARIO = "resumo_diario"
    LIMPEZA_HISTORICO = "limpeza_historico"
    TESTE_CONECTIVIDADE = "teste_conectividade"

class StatusTarefa(Enum):
    """Status das tarefas"""
    AGENDADA = "agendada"
    EXECUTANDO = "executando"
    CONCLUIDA = "concluida"
    FALHOU = "falhou"
    CANCELADA = "cancelada"

@dataclass
class Tarefa:
    """Estrutura de dados para tarefas agendadas"""
    id: str
    tipo: TipoTarefa
    nome: str
    funcao: Callable
    parametros: Dict
    proxima_execucao: datetime
    intervalo: str  # cron expression ou intervalo
    status: StatusTarefa
    ultima_execucao: Optional[datetime] = None
    proxima_execucao_prevista: Optional[datetime] = None
    tentativas: int = 0
    max_tentativas: int = 3
    ativa: bool = True

class AgendadorTarefas:
    """Agendador principal de tarefas do sistema"""
    
    def __init__(self):
        self.tarefas: List[Tarefa] = []
        self.thread_execucao = None
        self.executando = False
        self.gerenciador_notificacoes = None
        
        # Configurar tarefas padrão
        self._configurar_tarefas_padrao()
    
    def _configurar_tarefas_padrao(self):
        """Configura tarefas padrão do sistema"""
        try:
            # Tarefa de limpeza de histórico (diária às 02:00)
            self.agendar_tarefa_cron(
                tipo=TipoTarefa.LIMPEZA_HISTORICO,
                nome="Limpeza de Histórico",
                funcao=self._limpar_historico,
                cron_expression="0 2 * * *"  # Diariamente às 02:00
            )
            
            # Tarefa de teste de conectividade (a cada 6 horas)
            self.agendar_tarefa_cron(
                tipo=TipoTarefa.TESTE_CONECTIVIDADE,
                nome="Teste de Conectividade",
                funcao=self._testar_conectividade,
                cron_expression="0 */6 * * *"  # A cada 6 horas
            )
            
            logger.info("Tarefas padrão configuradas com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao configurar tarefas padrão: {str(e)}")
    
    def definir_gerenciador_notificacoes(self, gerenciador):
        """Define o gerenciador de notificações"""
        self.gerenciador_notificacoes = gerenciador
        logger.info("Gerenciador de notificações definido")
    
    def agendar_tarefa_cron(self, tipo: TipoTarefa, nome: str, funcao: Callable, 
                           cron_expression: str, parametros: Dict = None) -> str:
        """
        Agenda uma tarefa usando expressão cron
        
        Args:
            tipo: Tipo da tarefa
            nome: Nome descritivo da tarefa
            funcao: Função a ser executada
            cron_expression: Expressão cron (ex: "0 2 * * *" para diário às 02:00)
            parametros: Parâmetros para a função
        
        Returns:
            str: ID da tarefa agendada
        """
        try:
            tarefa_id = f"tarefa_{tipo.value}_{int(time.time())}"
            
            # Calcular próxima execução baseada na expressão cron
            proxima_execucao = self._calcular_proxima_execucao_cron(cron_expression)
            
            tarefa = Tarefa(
                id=tarefa_id,
                tipo=tipo,
                nome=nome,
                funcao=funcao,
                parametros=parametros or {},
                proxima_execucao=proxima_execucao,
                intervalo=cron_expression,
                status=StatusTarefa.AGENDADA
            )
            
            self.tarefas.append(tarefa)
            
            # Agendar no schedule
            schedule.every().day.at(proxima_execucao.strftime("%H:%M")).do(
                self._executar_tarefa, tarefa
            )
            
            logger.info(f"Tarefa agendada: {nome} (ID: {tarefa_id}) para {proxima_execucao}")
            return tarefa_id
            
        except Exception as e:
            logger.error(f"Erro ao agendar tarefa: {str(e)}")
            return None
    
    def agendar_tarefa_intervalo(self, tipo: TipoTarefa, nome: str, funcao: Callable,
                                intervalo_minutos: int, parametros: Dict = None) -> str:
        """
        Agenda uma tarefa para execução em intervalos regulares
        
        Args:
            tipo: Tipo da tarefa
            nome: Nome descritivo da tarefa
            funcao: Função a ser executada
            intervalo_minutos: Intervalo em minutos
            parametros: Parâmetros para a função
        
        Returns:
            str: ID da tarefa agendada
        """
        try:
            tarefa_id = f"tarefa_{tipo.value}_{int(time.time())}"
            
            proxima_execucao = datetime.now() + timedelta(minutes=intervalo_minutos)
            
            tarefa = Tarefa(
                id=tarefa_id,
                tipo=tipo,
                nome=nome,
                funcao=funcao,
                parametros=parametros or {},
                proxima_execucao=proxima_execucao,
                intervalo=f"{intervalo_minutos}min",
                status=StatusTarefa.AGENDADA
            )
            
            self.tarefas.append(tarefa)
            
            # Agendar no schedule
            schedule.every(intervalo_minutos).minutes.do(
                self._executar_tarefa, tarefa
            )
            
            logger.info(f"Tarefa agendada: {nome} (ID: {tarefa_id}) a cada {intervalo_minutos} minutos")
            return tarefa_id
            
        except Exception as e:
            logger.error(f"Erro ao agendar tarefa: {str(e)}")
            return None
    
    def agendar_tarefa_data_hora(self, tipo: TipoTarefa, nome: str, funcao: Callable,
                                data_hora: datetime, parametros: Dict = None) -> str:
        """
        Agenda uma tarefa para execução em data/hora específica
        
        Args:
            tipo: Tipo da tarefa
            nome: Nome descritivo da tarefa
            funcao: Função a ser executada
            data_hora: Data e hora para execução
            parametros: Parâmetros para a função
        
        Returns:
            str: ID da tarefa agendada
        """
        try:
            tarefa_id = f"tarefa_{tipo.value}_{int(time.time())}"
            
            tarefa = Tarefa(
                id=tarefa_id,
                tipo=tipo,
                nome=nome,
                funcao=funcao,
                parametros=parametros or {},
                proxima_execucao=data_hora,
                intervalo="unica",
                status=StatusTarefa.AGENDADA
            )
            
            self.tarefas.append(tarefa)
            
            # Agendar no schedule
            schedule.every().day.at(data_hora.strftime("%H:%M")).do(
                self._executar_tarefa, tarefa
            )
            
            logger.info(f"Tarefa agendada: {nome} (ID: {tarefa_id}) para {data_hora}")
            return tarefa_id
            
        except Exception as e:
            logger.error(f"Erro ao agendar tarefa: {str(e)}")
            return None
    
    def agendar_lembrete_agendamento(self, agendamento: Dict) -> bool:
        """
        Agenda lembretes automáticos para um agendamento
        
        Args:
            agendamento: Dados do agendamento
        
        Returns:
            bool: True se agendado com sucesso
        """
        try:
            if not self.gerenciador_notificacoes:
                logger.error("Gerenciador de notificações não definido")
                return False
            
            data_consulta = datetime.strptime(agendamento['data'], '%Y-%m-%d')
            horario_consulta = datetime.strptime(agendamento['horario'], '%H:%M')
            
            # Lembrete 24h antes
            data_lembrete_24h = data_consulta - timedelta(days=1)
            self.agendar_tarefa_data_hora(
                tipo=TipoTarefa.LEMBRETE_24H,
                nome=f"Lembrete 24h - Agendamento {agendamento['id']}",
                funcao=self._enviar_lembrete_24h,
                data_hora=data_lembrete_24h.replace(hour=18, minute=0),  # 18:00
                parametros={"agendamento_id": agendamento['id']}
            )
            
            # Lembrete 1h antes
            data_lembrete_1h = data_consulta.replace(
                hour=horario_consulta.hour,
                minute=horario_consulta.minute
            ) - timedelta(hours=1)
            
            self.agendar_tarefa_data_hora(
                tipo=TipoTarefa.LEMBRETE_1H,
                nome=f"Lembrete 1h - Agendamento {agendamento['id']}",
                funcao=self._enviar_lembrete_1h,
                data_hora=data_lembrete_1h,
                parametros={"agendamento_id": agendamento['id']}
            )
            
            # Lembrete adicional se não confirmar (6h antes)
            data_lembrete_adicional = data_consulta - timedelta(hours=6)
            self.agendar_tarefa_data_hora(
                tipo=TipoTarefa.LEMBRETE_ADICIONAL,
                nome=f"Lembrete Adicional - Agendamento {agendamento['id']}",
                funcao=self._enviar_lembrete_adicional,
                data_hora=data_lembrete_adicional,
                parametros={"agendamento_id": agendamento['id']}
            )
            
            logger.info(f"Lembretes agendados para agendamento {agendamento['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao agendar lembretes: {str(e)}")
            return False
    
    def agendar_resumo_diario_profissional(self, profissional_id: int, data: str) -> bool:
        """
        Agenda envio de resumo diário para profissional
        
        Args:
            profissional_id: ID do profissional
            data: Data do resumo (formato: YYYY-MM-DD)
        
        Returns:
            bool: True se agendado com sucesso
        """
        try:
            # Enviar resumo às 07:00 do dia
            data_resumo = datetime.strptime(data, '%Y-%m-%d').replace(hour=7, minute=0)
            
            self.agendar_tarefa_data_hora(
                tipo=TipoTarefa.RESUMO_DIARIO,
                nome=f"Resumo Diário - Profissional {profissional_id} - {data}",
                funcao=self._enviar_resumo_diario,
                data_hora=data_resumo,
                parametros={"profissional_id": profissional_id, "data": data}
            )
            
            logger.info(f"Resumo diário agendado para profissional {profissional_id} em {data}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao agendar resumo diário: {str(e)}")
            return False
    
    def iniciar(self):
        """Inicia o agendador de tarefas"""
        try:
            if self.executando:
                logger.warning("Agendador já está executando")
                return
            
            self.executando = True
            self.thread_execucao = threading.Thread(target=self._loop_execucao, daemon=True)
            self.thread_execucao.start()
            
            logger.info("Agendador de tarefas iniciado")
            
        except Exception as e:
            logger.error(f"Erro ao iniciar agendador: {str(e)}")
    
    def parar(self):
        """Para o agendador de tarefas"""
        try:
            self.executando = False
            if self.thread_execucao:
                self.thread_execucao.join(timeout=5)
            
            logger.info("Agendador de tarefas parado")
            
        except Exception as e:
            logger.error(f"Erro ao parar agendador: {str(e)}")
    
    def _loop_execucao(self):
        """Loop principal de execução das tarefas"""
        try:
            while self.executando:
                schedule.run_pending()
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Erro no loop de execução: {str(e)}")
            self.executando = False
    
    def _executar_tarefa(self, tarefa: Tarefa):
        """Executa uma tarefa agendada"""
        try:
            if not tarefa.ativa:
                return
            
            tarefa.status = StatusTarefa.EXECUTANDO
            tarefa.ultima_execucao = datetime.now()
            tarefa.tentativas += 1
            
            logger.info(f"Executando tarefa: {tarefa.nome}")
            
            # Executar função da tarefa
            resultado = tarefa.funcao(**tarefa.parametros)
            
            if resultado:
                tarefa.status = StatusTarefa.CONCLUIDA
                logger.info(f"Tarefa concluída com sucesso: {tarefa.nome}")
            else:
                tarefa.status = StatusTarefa.FALHOU
                logger.error(f"Tarefa falhou: {tarefa.nome}")
            
            # Reagendar se necessário
            if tarefa.intervalo != "unica":
                self._reagendar_tarefa(tarefa)
            
        except Exception as e:
            tarefa.status = StatusTarefa.FALHOU
            logger.error(f"Erro ao executar tarefa {tarefa.nome}: {str(e)}")
            
            # Tentar novamente se não excedeu limite
            if tarefa.tentativas < tarefa.max_tentativas:
                self._reagendar_tarefa(tarefa, delay_minutos=5)
    
    def _reagendar_tarefa(self, tarefa: Tarefa, delay_minutos: int = 0):
        """Reagenda uma tarefa para próxima execução"""
        try:
            if tarefa.intervalo == "unica":
                return
            
            # Calcular próxima execução
            if delay_minutos > 0:
                proxima_execucao = datetime.now() + timedelta(minutes=delay_minutos)
            else:
                proxima_execucao = self._calcular_proxima_execucao_cron(tarefa.intervalo)
            
            tarefa.proxima_execucao = proxima_execucao
            tarefa.proxima_execucao_prevista = proxima_execucao
            tarefa.status = StatusTarefa.AGENDADA
            
            logger.info(f"Tarefa reagendada: {tarefa.nome} para {proxima_execucao}")
            
        except Exception as e:
            logger.error(f"Erro ao reagendar tarefa: {str(e)}")
    
    def _calcular_proxima_execucao_cron(self, cron_expression: str) -> datetime:
        """Calcula próxima execução baseada em expressão cron"""
        try:
            # Implementação simplificada para expressões cron básicas
            # Formato esperado: "minuto hora * * *"
            partes = cron_expression.split()
            if len(partes) != 5:
                raise ValueError("Expressão cron inválida")
            
            minuto, hora = int(partes[0]), int(partes[1])
            
            agora = datetime.now()
            proxima_execucao = agora.replace(hour=hora, minute=minuto, second=0, microsecond=0)
            
            # Se já passou do horário hoje, agendar para amanhã
            if proxima_execucao <= agora:
                proxima_execucao += timedelta(days=1)
            
            return proxima_execucao
            
        except Exception as e:
            logger.error(f"Erro ao calcular próxima execução cron: {str(e)}")
            return datetime.now() + timedelta(hours=1)
    
    def _enviar_lembrete_24h(self, agendamento_id: int):
        """Envia lembrete 24h antes da consulta"""
        try:
            if not self.gerenciador_notificacoes:
                return False
            
            # TODO: Buscar dados do agendamento no banco
            # Por enquanto, simulação
            agendamento = {
                "id": agendamento_id,
                "paciente_id": 1,
                "telefone_paciente": "+5511999999999",
                "data": "2025-01-20",
                "horario": "14:00",
                "profissional": "Dr. João Silva",
                "especialidade": "Clínico Geral"
            }
            
            return self.gerenciador_notificacoes.notificar_lembrete_24h(agendamento)
            
        except Exception as e:
            logger.error(f"Erro ao enviar lembrete 24h: {str(e)}")
            return False
    
    def _enviar_lembrete_1h(self, agendamento_id: int):
        """Envia lembrete 1h antes da consulta"""
        try:
            if not self.gerenciador_notificacoes:
                return False
            
            # TODO: Buscar dados do agendamento no banco
            agendamento = {
                "id": agendamento_id,
                "paciente_id": 1,
                "telefone_paciente": "+5511999999999",
                "data": "2025-01-20",
                "horario": "14:00",
                "profissional": "Dr. João Silva"
            }
            
            return self.gerenciador_notificacoes.notificar_lembrete_1h(agendamento)
            
        except Exception as e:
            logger.error(f"Erro ao enviar lembrete 1h: {str(e)}")
            return False
    
    def _enviar_lembrete_adicional(self, agendamento_id: int):
        """Envia lembrete adicional se não confirmar"""
        try:
            if not self.gerenciador_notificacoes:
                return False
            
            # TODO: Buscar dados do agendamento no banco
            agendamento = {
                "id": agendamento_id,
                "paciente_id": 1,
                "telefone_paciente": "+5511999999999",
                "data": "2025-01-20",
                "horario": "14:00",
                "profissional": "Dr. João Silva"
            }
            
            return self.gerenciador_notificacoes.notificar_lembrete_adicional(agendamento)
            
        except Exception as e:
            logger.error(f"Erro ao enviar lembrete adicional: {str(e)}")
            return False
    
    def _enviar_resumo_diario(self, profissional_id: int, data: str):
        """Envia resumo diário para profissional"""
        try:
            if not self.gerenciador_notificacoes:
                return False
            
            return self.gerenciador_notificacoes.enviar_resumo_diario_profissional(profissional_id, data)
            
        except Exception as e:
            logger.error(f"Erro ao enviar resumo diário: {str(e)}")
            return False
    
    def _limpar_historico(self):
        """Limpa histórico antigo de notificações"""
        try:
            if self.gerenciador_notificacoes:
                # TODO: Implementar limpeza de histórico
                logger.info("Limpeza de histórico executada")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao limpar histórico: {str(e)}")
            return False
    
    def _testar_conectividade(self):
        """Testa conectividade dos serviços"""
        try:
            if self.gerenciador_notificacoes and hasattr(self.gerenciador_notificacoes, 'whatsapp_service'):
                resultado = self.gerenciador_notificacoes.whatsapp_service.testar_conectividade()
                logger.info(f"Teste de conectividade: {resultado}")
            return True
            
        except Exception as e:
            logger.error(f"Erro no teste de conectividade: {str(e)}")
            return False
    
    def obter_tarefas(self) -> List[Dict]:
        """Obtém lista de todas as tarefas"""
        try:
            return [
                {
                    "id": t.id,
                    "tipo": t.tipo.value,
                    "nome": t.nome,
                    "status": t.status.value,
                    "proxima_execucao": t.proxima_execucao.isoformat(),
                    "ultima_execucao": t.ultima_execucao.isoformat() if t.ultima_execucao else None,
                    "tentativas": t.tentativas,
                    "ativa": t.ativa
                }
                for t in self.tarefas
            ]
            
        except Exception as e:
            logger.error(f"Erro ao obter tarefas: {str(e)}")
            return []
    
    def cancelar_tarefa(self, tarefa_id: str) -> bool:
        """Cancela uma tarefa específica"""
        try:
            for tarefa in self.tarefas:
                if tarefa.id == tarefa_id:
                    tarefa.ativa = False
                    tarefa.status = StatusTarefa.CANCELADA
                    logger.info(f"Tarefa cancelada: {tarefa.nome}")
                    return True
            
            logger.warning(f"Tarefa não encontrada: {tarefa_id}")
            return False
            
        except Exception as e:
            logger.error(f"Erro ao cancelar tarefa: {str(e)}")
            return False
    
    def reativar_tarefa(self, tarefa_id: str) -> bool:
        """Reativa uma tarefa cancelada"""
        try:
            for tarefa in self.tarefas:
                if tarefa.id == tarefa_id:
                    tarefa.ativa = True
                    tarefa.status = StatusTarefa.AGENDADA
                    logger.info(f"Tarefa reativada: {tarefa.nome}")
                    return True
            
            logger.warning(f"Tarefa não encontrada: {tarefa_id}")
            return False
            
        except Exception as e:
            logger.error(f"Erro ao reativar tarefa: {str(e)}")
            return False
    
    def obter_estatisticas(self) -> Dict:
        """Obtém estatísticas do agendador"""
        try:
            total_tarefas = len(self.tarefas)
            tarefas_ativas = len([t for t in self.tarefas if t.ativa])
            tarefas_executando = len([t for t in self.tarefas if t.status == StatusTarefa.EXECUTANDO])
            tarefas_concluidas = len([t for t in self.tarefas if t.status == StatusTarefa.CONCLUIDA])
            tarefas_falharam = len([t for t in self.tarefas if t.status == StatusTarefa.FALHOU])
            
            return {
                "total_tarefas": total_tarefas,
                "tarefas_ativas": tarefas_ativas,
                "tarefas_executando": tarefas_executando,
                "tarefas_concluidas": tarefas_concluidas,
                "tarefas_falharam": tarefas_falharam,
                "agendador_executando": self.executando,
                "ultima_execucao": datetime.now().isoformat() if self.executando else None
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {}
