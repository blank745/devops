"""
Конфигурация pytest для тестов Django приложения
"""
import pytest
from django.contrib.auth.models import User


# Фикстуры для тестов
@pytest.fixture
def user(db):
    """Создает обычного пользователя"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user(db):
    """Создает администратора"""
    from racing.models import UserProfile
    user = User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='testpass123'
    )
    UserProfile.objects.create(user=user, role='admin')
    return user


@pytest.fixture
def jockey_user(db):
    """Создает пользователя-жокея"""
    from racing.models import UserProfile, Jockey
    user = User.objects.create_user(
        username='jockey',
        email='jockey@example.com',
        password='testpass123'
    )
    jockey = Jockey.objects.create(
        name='Test Jockey',
        address='Test Address',
        age=30,
        rating=5
    )
    UserProfile.objects.create(user=user, role='jockey', jockey=jockey)
    return user


@pytest.fixture
def regular_user(db):
    """Создает обычного пользователя с профилем"""
    from racing.models import UserProfile
    user = User.objects.create_user(
        username='user',
        email='user@example.com',
        password='testpass123'
    )
    UserProfile.objects.create(user=user, role='user')
    return user


@pytest.fixture
def hippodrome(db):
    """Создает ипподром"""
    from racing.models import Hippodrome
    return Hippodrome.objects.create(
        name='Test Hippodrome',
        address='Test Address',
        capacity=10000,
        is_active=True
    )


@pytest.fixture
def owner(db):
    """Создает владельца"""
    from racing.models import Owner
    return Owner.objects.create(
        name='Test Owner',
        address='Test Address',
        phone='+79991234567'
    )


@pytest.fixture
def jockey(db):
    """Создает жокея"""
    from racing.models import Jockey
    return Jockey.objects.create(
        name='Test Jockey',
        address='Test Address',
        age=30,
        rating=5
    )


@pytest.fixture
def horse(db, owner):
    """Создает лошадь"""
    from racing.models import Horse
    return Horse.objects.create(
        name='Test Horse',
        gender='M',
        age=5,
        owner=owner
    )


@pytest.fixture
def competition(db, hippodrome):
    """Создает состязание"""
    from datetime import date, time
    from racing.models import Competition
    return Competition.objects.create(
        date=date.today(),
        time=time(14, 0),
        hippodrome=hippodrome,
        name='Test Competition'
    )


@pytest.fixture
def result(db, competition, horse, jockey):
    """Создает результат состязания"""
    from datetime import timedelta
    from racing.models import Result
    return Result.objects.create(
        competition=competition,
        horse=horse,
        jockey=jockey,
        position=1,
        time_result=timedelta(minutes=2, seconds=30, milliseconds=500)
    )


@pytest.fixture
def client():
    """Django test client"""
    from django.test import Client
    return Client()

