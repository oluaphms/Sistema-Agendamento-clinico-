"""
Testes do Módulo Analytics
Verifica se todas as funcionalidades estão funcionando
"""

import sys
import os
import unittest
from datetime import datetime, date, timedelta

# Adicionar o diretório pai ao path para importar o módulo
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestAnalyticsModule(unittest.TestCase):
    """Testes para o módulo de analytics"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        try:
            from analytics.models import db
            from analytics.services import analytics_service
            
            # Configurar banco de teste
            self.db = db
            self.analytics_service = analytics_service
            
            print("✅ Módulo de analytics carregado com sucesso!")
            
        except ImportError as e:
            print(f"❌ Erro ao importar módulo: {e}")
            self.fail("Módulo de analytics não pôde ser importado")
    
    def test_models_import(self):
        """Testa se os modelos podem ser importados"""
        try:
            from analytics.models import (
                AnalyticsConfig, AnalyticsHistorico, RelatorioAgendado,
                PrevisaoFalta, InsightAutomatico, MetricaTempoReal
            )
            print("✅ Todos os modelos importados com sucesso")
        except ImportError as e:
            self.fail(f"Erro ao importar modelos: {e}")
    
    def test_services_import(self):
        """Testa se os serviços podem ser importados"""
        try:
            from analytics.services import AnalyticsService
            print("✅ Serviços importados com sucesso")
        except ImportError as e:
            self.fail(f"Erro ao importar serviços: {e}")
    
    def test_routes_import(self):
        """Testa se as rotas podem ser importadas"""
        try:
            from analytics.routes import analytics_bp
            print("✅ Rotas importadas com sucesso")
        except ImportError as e:
            self.fail(f"Erro ao importar rotas: {e}")
    
    def test_integration_import(self):
        """Testa se o módulo de integração pode ser importado"""
        try:
            from analytics.integration import (
                init_analytics, get_analytics_summary, 
                get_analytics_alerts, health_check
            )
            print("✅ Módulo de integração importado com sucesso")
        except ImportError as e:
            self.fail(f"Erro ao importar módulo de integração: {e}")
    
    def test_health_check(self):
        """Testa a verificação de saúde do módulo"""
        try:
            from analytics.integration import health_check
            status = health_check()
            
            self.assertIn('status', status)
            self.assertIn('module', status)
            self.assertIn('version', status)
            
            print(f"✅ Health check: {status['status']}")
            
        except Exception as e:
            self.fail(f"Erro no health check: {e}")
    
    def test_config_functions(self):
        """Testa as funções de configuração"""
        try:
            from analytics.models import get_config, set_config
            
            # Testar definição de configuração
            set_config('test_key', 'test_value', 'string', 'Teste')
            
            # Testar obtenção de configuração
            value = get_config('test_key', 'default')
            self.assertEqual(value, 'test_value')
            
            # Testar valor padrão
            default_value = get_config('non_existent_key', 'default_value')
            self.assertEqual(default_value, 'default_value')
            
            print("✅ Funções de configuração funcionando")
            
        except Exception as e:
            self.fail(f"Erro nas funções de configuração: {e}")
    
    def test_metric_registration(self):
        """Testa o registro de métricas"""
        try:
            from analytics.models import registrar_metrica
            
            # Registrar uma métrica de teste
            metrica = registrar_metrica(
                date.today(),
                'test_metric',
                42.5,
                {'test': True, 'value': 42}
            )
            
            self.assertIsNotNone(metrica)
            self.assertEqual(metrica.tipo_metrica, 'test_metric')
            self.assertEqual(metrica.valor, 42.5)
            
            print("✅ Registro de métricas funcionando")
            
        except Exception as e:
            self.fail(f"Erro no registro de métricas: {e}")
    
    def test_insight_registration(self):
        """Testa o registro de insights"""
        try:
            from analytics.models import registrar_insight
            
            # Registrar um insight de teste
            insight = registrar_insight(
                'test_type',
                'Teste de Insight',
                'Este é um insight de teste',
                {'test': True},
                'normal'
            )
            
            self.assertIsNotNone(insight)
            self.assertEqual(insight.tipo, 'test_type')
            self.assertEqual(insight.titulo, 'Teste de Insight')
            
            print("✅ Registro de insights funcionando")
            
        except Exception as e:
            self.fail(f"Erro no registro de insights: {e}")
    
    def test_analytics_service_methods(self):
        """Testa os métodos do serviço de analytics"""
        try:
            from analytics.services import AnalyticsService
            
            service = AnalyticsService()
            
            # Verificar se os métodos existem
            methods = [
                'calcular_metricas_gerais',
                'calcular_taxa_presenca_detalhada',
                'calcular_consultas_por_especialidade',
                'calcular_receita_mensal_profissional',
                'calcular_crescimento_pacientes',
                'treinar_modelo_falta',
                'prever_falta',
                'gerar_insights_automaticos'
            ]
            
            for method in methods:
                self.assertTrue(hasattr(service, method))
                self.assertTrue(callable(getattr(service, method)))
            
            print("✅ Todos os métodos do serviço estão disponíveis")
            
        except Exception as e:
            self.fail(f"Erro no teste dos métodos do serviço: {e}")
    
    def test_blueprint_registration(self):
        """Testa se o blueprint pode ser registrado"""
        try:
            from flask import Flask
            from analytics.routes import analytics_bp
            
            # Criar app de teste
            app = Flask(__name__)
            app.config['TESTING'] = True
            
            # Registrar blueprint
            app.register_blueprint(analytics_bp)
            
            # Verificar se as rotas foram registradas
            routes = [str(rule) for rule in app.url_map.iter_rules()]
            
            # Verificar se algumas rotas principais estão presentes
            expected_routes = [
                '/analytics/',
                '/analytics/relatorios',
                '/analytics/configuracoes'
            ]
            
            for route in expected_routes:
                self.assertIn(route, routes)
            
            print("✅ Blueprint registrado com sucesso")
            
        except Exception as e:
            self.fail(f"Erro no registro do blueprint: {e}")

def run_tests():
    """Executa todos os testes"""
    print("🧪 Iniciando testes do módulo Analytics...")
    print("=" * 50)
    
    # Criar suite de testes
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAnalyticsModule)
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 50)
    
    if result.wasSuccessful():
        print("🎉 Todos os testes passaram!")
        print(f"✅ Executados: {result.testsRun}")
        print(f"✅ Sucessos: {result.testsRun}")
        print(f"❌ Falhas: {len(result.failures)}")
        print(f"❌ Erros: {len(result.errors)}")
    else:
        print("❌ Alguns testes falharam!")
        print(f"✅ Executados: {result.testsRun}")
        print(f"❌ Falhas: {len(result.failures)}")
        print(f"❌ Erros: {len(result.errors)}")
        
        if result.failures:
            print("\nFalhas:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback}")
        
        if result.errors:
            print("\nErros:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback}")
    
    return result.wasSuccessful()

def test_quick():
    """Teste rápido sem unittest"""
    print("🚀 Teste rápido do módulo Analytics...")
    
    try:
        # Testar imports básicos
        from analytics.models import get_config, set_config
        from analytics.services import AnalyticsService
        from analytics.routes import analytics_bp
        from analytics.integration import health_check
        
        print("✅ Imports básicos funcionando")
        
        # Testar configuração
        set_config('quick_test', 'success', 'string', 'Teste rápido')
        value = get_config('quick_test', 'fail')
        
        if value == 'success':
            print("✅ Sistema de configuração funcionando")
        else:
            print("❌ Sistema de configuração com problema")
        
        # Testar health check
        status = health_check()
        print(f"✅ Health check: {status['status']}")
        
        print("🎉 Teste rápido concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste rápido: {e}")
        return False

if __name__ == '__main__':
    # Executar teste rápido primeiro
    if test_quick():
        print("\n" + "="*50)
        # Se o teste rápido passar, executar testes completos
        run_tests()
    else:
        print("❌ Teste rápido falhou. Verifique a instalação do módulo.")
        sys.exit(1)







