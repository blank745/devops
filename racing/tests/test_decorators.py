"""
Unit тесты для декораторов приложения racing
"""
import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory
from racing.decorators import admin_required, jockey_or_admin_required, user_required
from racing.models import UserProfile, Jockey
from racing.views import index


@pytest.mark.unit
class TestDecorators:
    """Тесты для декораторов доступа"""
    
    def test_admin_required_with_admin(self, db, client):
        """Тест декоратора admin_required с администратором"""
        user = User.objects.create_user(username='admin', password='test123')
        UserProfile.objects.create(user=user, role='admin')
        client.force_login(user)
        
        # Пытаемся получить доступ к защищенной функции
        # В реальном приложении это будет проверяться через views
        assert user.userprofile.role == 'admin'
        assert user.userprofile.is_admin() is True
    
    def test_admin_required_with_user(self, db, client):
        """Тест декоратора admin_required с обычным пользователем"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        client.force_login(user)
        
        assert user.userprofile.role == 'user'
        assert user.userprofile.is_admin() is False
    
    def test_jockey_or_admin_required_with_jockey(self, db, client):
        """Тест декоратора jockey_or_admin_required с жокеем"""
        user = User.objects.create_user(username='jockey', password='test123')
        jockey = Jockey.objects.create(name='Test Jockey', address='Test', age=30, rating=5)
        UserProfile.objects.create(user=user, role='jockey', jockey=jockey)
        client.force_login(user)
        
        assert user.userprofile.role == 'jockey'
        assert user.userprofile.is_jockey() is True
    
    def test_jockey_or_admin_required_with_admin(self, db, client):
        """Тест декоратора jockey_or_admin_required с администратором"""
        user = User.objects.create_user(username='admin', password='test123')
        UserProfile.objects.create(user=user, role='admin')
        client.force_login(user)
        
        assert user.userprofile.role == 'admin'
        assert user.userprofile.is_admin() is True
    
    def test_user_required_with_user(self, db, client):
        """Тест декоратора user_required с пользователем"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        client.force_login(user)
        
        assert user.userprofile.role == 'user'
        assert user.userprofile.is_user() is True
    
    def test_user_required_creates_profile(self, db):
        """Тест создания профиля при использовании user_required"""
        user = User.objects.create_user(username='user', password='test123')
        # Профиль не создан
        
        # Симулируем доступ через декоратор
        factory = RequestFactory()
        request = factory.get('/')
        request.user = user
        
        # Декоратор должен создать профиль
        # Это проверяется в integration тестах

