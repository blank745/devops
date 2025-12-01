"""
Unit тесты для декораторов приложения racing
Использует unittest
"""
import unittest
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.core.management import call_command
from racing.models import UserProfile, Jockey


# Базовый класс с применением миграций
try:
    from racing.tests.test_base import BaseTestCase
except ImportError:
    # Если test_base.py не найден, используем встроенный класс
    class BaseTestCase(TestCase):
        """Базовый класс для тестов с применением миграций"""
        @classmethod
        def setUpClass(cls):
            """Применяет миграции перед запуском тестов класса"""
            super().setUpClass()
            call_command('migrate', verbosity=0, interactive=False)


class TestDecorators(BaseTestCase):
    """Тесты для декораторов доступа"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
    
    def test_admin_required_with_admin(self):
        """Тест декоратора admin_required с администратором"""
        user = User.objects.create_user(username='admin', password='test123')
        UserProfile.objects.create(user=user, role='admin')
        self.client.force_login(user)
        
        # Проверяем, что пользователь имеет роль администратора
        self.assertEqual(user.userprofile.role, 'admin')
        self.assertTrue(user.userprofile.is_admin())
    
    def test_admin_required_with_user(self):
        """Тест декоратора admin_required с обычным пользователем"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        self.client.force_login(user)
        
        self.assertEqual(user.userprofile.role, 'user')
        self.assertFalse(user.userprofile.is_admin())
    
    def test_jockey_or_admin_required_with_jockey(self):
        """Тест декоратора jockey_or_admin_required с жокеем"""
        user = User.objects.create_user(username='jockey', password='test123')
        jockey = Jockey.objects.create(
            name='Test Jockey',
            address='Test',
            age=30,
            rating=5
        )
        UserProfile.objects.create(user=user, role='jockey', jockey=jockey)
        self.client.force_login(user)
        
        self.assertEqual(user.userprofile.role, 'jockey')
        self.assertTrue(user.userprofile.is_jockey())
    
    def test_jockey_or_admin_required_with_admin(self):
        """Тест декоратора jockey_or_admin_required с администратором"""
        user = User.objects.create_user(username='admin', password='test123')
        UserProfile.objects.create(user=user, role='admin')
        self.client.force_login(user)
        
        self.assertEqual(user.userprofile.role, 'admin')
        self.assertTrue(user.userprofile.is_admin())
    
    def test_user_required_with_user(self):
        """Тест декоратора user_required с пользователем"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        self.client.force_login(user)
        
        self.assertEqual(user.userprofile.role, 'user')
        self.assertTrue(user.userprofile.is_user())
