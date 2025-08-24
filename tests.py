import pytest
import tempfile
import os
from datetime import datetime, date
from app import app, db, Usuario, Paciente, Profissional, Servico, Agendamento
from security import security
from notifications import notifications
from reports import reports

@pytest.fixture
def client():
    """Cria um cliente de teste"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def sample_data():
    """Cria dados de exemplo para os testes"""
    with app.app_context():
        # Cria usuário admin
        admin = Usuario(
            usuario='admin_test',
            senha='admin123',
            role='admin'
        )
        db.session.add(admin)
        
        # Cria paciente
        paciente = Paciente(
            nome='João Silva',
            telefone='11999999999',
            email='joao@email.com',
            nascimento='1990-01-01'
        )
        db.session.add(paciente)
        
        # Cria profissional
        profissional = Profissional(
            nome='Dr. Carlos',
            especialidade='Cardiologia',
            telefone='11888888888',
            email='carlos@clinica.com'
        )
        db.session.add(profissional)
        
        # Cria serviço
        servico = Servico(
            nome='Consulta Cardiológica',
            duracao_min=60,
            preco=150.00
        )
        db.session.add(servico)
        
        db.session.commit()
        
        return {
            'admin': admin,
            'paciente': paciente,
            'profissional': profissional,
            'servico': servico
        }

class TestSecurity:
    """Testes para funcionalidades de segurança"""
    
    def test_password_validation(self):
        """Testa validação de senha"""
        # Senha válida
        is_valid, message = security.validate_password_strength("Senha123!")
        assert is_valid == True
        
        # Senha muito curta
        is_valid, message = security.validate_password_strength("abc")
        assert is_valid == False
        assert "8 caracteres" in message
        
        # Senha sem maiúscula
        is_valid, message = security.validate_password_strength("senha123!")
        assert is_valid == False
        assert "maiúscula" in message
    
    def test_input_sanitization(self):
        """Testa sanitização de entrada"""
        dangerous_input = "<script>alert('xss')</script>"
        sanitized = security.sanitize_input(dangerous_input)
        assert "<script>" not in sanitized
        assert "&lt;" in sanitized
    
    def test_email_validation(self):
        """Testa validação de email"""
        assert security.validate_email("teste@email.com") == True
        assert security.validate_email("email_invalido") == False
        assert security.validate_email("") == False
    
    def test_phone_validation(self):
        """Testa validação de telefone"""
        assert security.validate_phone("11999999999") == True
        assert security.validate_phone("(11) 99999-9999") == True
        assert security.validate_phone("123") == False

class TestNotifications:
    """Testes para funcionalidades de notificação"""
    
    def test_email_creation(self):
        """Testa criação de mensagem de email"""
        # Simula dados de agendamento
        class MockAgendamento:
            data = "2024-01-15"
            hora = "14:00"
            duracao = 60
        
        class MockPaciente:
            nome = "João Silva"
            email = "joao@email.com"
            telefone = "11999999999"
        
        class MockProfissional:
            nome = "Dr. Carlos"
        
        class MockServico:
            nome = "Consulta Cardiológica"
        
        ag = MockAgendamento()
        pac = MockPaciente()
        prof = MockProfissional()
        serv = MockServico()
        
        # Testa se não há erro na criação (sem enviar realmente)
        try:
            notifications.send_appointment_confirmation(ag, pac, prof, serv)
            assert True  # Se chegou aqui, não houve erro
        except Exception as e:
            pytest.fail(f"Erro inesperado: {e}")

class TestReports:
    """Testes para funcionalidades de relatórios"""
    
    def test_pdf_generation(self):
        """Testa geração de PDF"""
        # Dados de teste
        agendamentos = []
        pacientes = []
        profissionais = []
        servicos = []
        
        try:
            # Testa se não há erro na criação (sem gerar arquivo real)
            buffer = reports.generate_pdf_report(agendamentos, pacientes, profissionais, servicos)
            assert buffer is not None
        except Exception as e:
            pytest.fail(f"Erro na geração de PDF: {e}")
    
    def test_excel_generation(self):
        """Testa geração de Excel"""
        # Dados de teste
        agendamentos = []
        pacientes = []
        profissionais = []
        servicos = []
        
        try:
            # Testa se não há erro na criação (sem gerar arquivo real)
            buffer = reports.generate_excel_report(agendamentos, pacientes, profissionais, servicos)
            assert buffer is not None
        except Exception as e:
            pytest.fail(f"Erro na geração de Excel: {e}")

class TestDatabase:
    """Testes para o banco de dados"""
    
    def test_user_creation(self, client, sample_data):
        """Testa criação de usuário"""
        with app.app_context():
            # Verifica se o usuário foi criado
            user = Usuario.query.filter_by(usuario='admin_test').first()
            assert user is not None
            assert user.role == 'admin'
    
    def test_patient_creation(self, client, sample_data):
        """Testa criação de paciente"""
        with app.app_context():
            # Verifica se o paciente foi criado
            patient = Paciente.query.filter_by(nome='João Silva').first()
            assert patient is not None
            assert patient.email == 'joao@email.com'
    
    def test_appointment_creation(self, client, sample_data):
        """Testa criação de agendamento"""
        with app.app_context():
            # Cria agendamento
            agendamento = Agendamento(
                paciente_id=sample_data['paciente'].id,
                profissional_id=sample_data['profissional'].id,
                servico_id=sample_data['servico'].id,
                data='2024-01-15',
                hora='14:00',
                duracao=60,
                status='Agendado'
            )
            db.session.add(agendamento)
            db.session.commit()
            
            # Verifica se foi criado
            assert agendamento.id is not None
            assert agendamento.paciente_id == sample_data['paciente'].id

class TestRoutes:
    """Testes para as rotas da aplicação"""
    
    def test_login_page(self, client):
        """Testa se a página de login carrega"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'login' in response.data.lower()
    
    def test_dashboard_requires_login(self, client):
        """Testa se o dashboard requer login"""
        response = client.get('/dashboard', follow_redirects=True)
        assert response.status_code == 200
        # Deve redirecionar para login
        assert b'login' in response.data.lower()
    
    def test_protected_routes(self, client):
        """Testa se rotas protegidas redirecionam para login"""
        protected_routes = ['/pacientes', '/profissionais', '/agenda', '/relatorios']
        
        for route in protected_routes:
            response = client.get(route, follow_redirects=True)
            assert response.status_code == 200
            # Deve redirecionar para login
            assert b'login' in response.data.lower()

if __name__ == '__main__':
    # Executa os testes
    pytest.main([__file__, '-v'])
