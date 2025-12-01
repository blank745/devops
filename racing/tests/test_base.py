"""
Базовый класс для всех тестов с преднастройкой базы данных
"""
from django.test import TestCase
from django.core.management import call_command


class BaseTestCase(TestCase):
    """
    Базовый класс для тестов с применением миграций
    
    Автоматически применяет все миграции перед запуском тестов,
    чтобы гарантировать, что схема БД соответствует текущему состоянию моделей.
    """
    
    @classmethod
    def setUpClass(cls):
        """Применяет миграции перед запуском тестов класса"""
        super().setUpClass()
        
        # Применяем все миграции для обеспечения актуальной схемы БД
        # Это гарантирует, что тесты работают с правильной структурой таблиц
        call_command('migrate', verbosity=0, interactive=False)
    
    @classmethod
    def tearDownClass(cls):
        """Очистка после тестов класса"""
        super().tearDownClass()

