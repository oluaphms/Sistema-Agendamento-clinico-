#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste das estatísticas do dashboard
"""

from datetime import datetime, timedelta

def calcular_estatisticas():
    """Simula o cálculo das estatísticas do dashboard"""
    
    # Simular dados do banco
    total_agendamentos = 150
    confirmados = 127
    data_limite = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Taxa de confirmação
    taxa_confirmacao = (confirmados / total_agendamentos * 100) if total_agendamentos > 0 else 0
    
    # Pacientes ativos (últimos 30 dias)
    pacientes_ativos = 89  # Simulado
    
    # Consultas por mês (últimos 30 dias)
    consultas_mes = 234  # Simulado
    
    return {
        'taxa_confirmacao': round(taxa_confirmacao, 1),
        'pacientes_ativos': pacientes_ativos,
        'consultas_mes': consultas_mes
    }

if __name__ == "__main__":
    stats = calcular_estatisticas()
    print("=== Estatísticas do Dashboard ===")
    print(f"Taxa de Confirmação: {stats['taxa_confirmacao']}%")
    print(f"Pacientes Ativos: {stats['pacientes_ativos']}")
    print(f"Consultas/Mês: {stats['consultas_mes']}")
    print("✅ Estatísticas calculadas com sucesso!")
