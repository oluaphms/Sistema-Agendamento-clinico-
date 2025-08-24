"""
Modelos do banco de dados - Sistema Clínica
Versão Modernizada - Fase 1
"""

from .user import User
from .patient import Patient
from .professional import Professional
from .service import Service
from .appointment import Appointment
from .medical_record import MedicalRecord

__all__ = [
    'User',
    'Patient', 
    'Professional',
    'Service',
    'Appointment',
    'MedicalRecord'
]
