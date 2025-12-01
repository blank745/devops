"""
Unit тесты для форм приложения racing
Использует unittest
"""
import unittest
from datetime import date, time, timedelta
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from django.core.management import call_command
from racing.forms import (
    HippodromeForm, OwnerForm, JockeyForm, HorseForm,
    CompetitionForm, ResultForm, UserRegistrationForm
)
from racing.models import (
    Hippodrome, Owner, Jockey, Horse, Competition, Result, UserProfile
)


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


class TestHippodromeForm(BaseTestCase):
    """Тесты для формы HippodromeForm"""
    
    def test_valid_hippodrome_form(self):
        """Тест валидной формы ипподрома"""
        form_data = {
            'name': 'Центральный ипподром',
            'address': 'Москва, ул. Ленина, 1',
            'capacity': 10000,
            'description': 'Крупнейший ипподром',
            'is_active': True
        }
        form = HippodromeForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_hippodrome_form_save(self):
        """Тест сохранения формы ипподрома"""
        form_data = {
            'name': 'Центральный ипподром',
            'address': 'Москва',
            'capacity': 10000,
            'is_active': True
        }
        form = HippodromeForm(data=form_data)
        self.assertTrue(form.is_valid())
        hippodrome = form.save()
        self.assertEqual(hippodrome.name, 'Центральный ипподром')
        self.assertTrue(Hippodrome.objects.filter(name='Центральный ипподром').exists())


class TestOwnerForm(BaseTestCase):
    """Тесты для формы OwnerForm"""
    
    def test_valid_owner_form(self):
        """Тест валидной формы владельца"""
        form_data = {
            'name': 'Иван Петров',
            'address': 'Москва',
            'phone': '+79991234567'
        }
        form = OwnerForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_owner_form_phone_normalization(self):
        """Тест нормализации номера телефона"""
        form_data = {
            'name': 'Иван Петров',
            'address': 'Москва',
            'phone': '8 (999) 123-45-67'
        }
        form = OwnerForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['phone'], '+79991234567')
    
    def test_owner_form_invalid_phone(self):
        """Тест невалидного номера телефона"""
        form_data = {
            'name': 'Иван Петров',
            'address': 'Москва',
            'phone': '12345'
        }
        form = OwnerForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)
    
    def test_owner_form_phone_with_8(self):
        """Тест номера телефона начинающегося с 8"""
        form_data = {
            'name': 'Иван Петров',
            'address': 'Москва',
            'phone': '89991234567'
        }
        form = OwnerForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.cleaned_data['phone'].startswith('+7'))


class TestJockeyForm(BaseTestCase):
    """Тесты для формы JockeyForm"""
    
    def test_valid_jockey_form(self):
        """Тест валидной формы жокея"""
        form_data = {
            'name': 'Алексей Смирнов',
            'address': 'Москва',
            'age': 30,
            'rating': 5
        }
        form = JockeyForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_jockey_form_save(self):
        """Тест сохранения формы жокея"""
        form_data = {
            'name': 'Алексей Смирнов',
            'address': 'Москва',
            'age': 30,
            'rating': 8
        }
        form = JockeyForm(data=form_data)
        self.assertTrue(form.is_valid())
        jockey = form.save()
        self.assertEqual(jockey.name, 'Алексей Смирнов')
        self.assertEqual(jockey.rating, 8)


class TestHorseForm(BaseTestCase):
    """Тесты для формы HorseForm"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.owner = Owner.objects.create(
            name='Owner',
            address='Test',
            phone='+79991234567'
        )
    
    def test_valid_horse_form(self):
        """Тест валидной формы лошади"""
        form_data = {
            'name': 'Быстрый',
            'gender': 'M',
            'age': 5,
            'owner': self.owner.id
        }
        form = HorseForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_horse_form_save(self):
        """Тест сохранения формы лошади"""
        form_data = {
            'name': 'Быстрый',
            'gender': 'F',
            'age': 5,
            'owner': self.owner.id
        }
        form = HorseForm(data=form_data)
        self.assertTrue(form.is_valid())
        horse = form.save()
        self.assertEqual(horse.name, 'Быстрый')
        self.assertEqual(horse.gender, 'F')


class TestCompetitionForm(BaseTestCase):
    """Тесты для формы CompetitionForm"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.hippodrome = Hippodrome.objects.create(
            name='Test',
            address='Test'
        )
    
    def test_valid_competition_form(self):
        """Тест валидной формы состязания"""
        past_date = date.today() - timedelta(days=1)
        form_data = {
            'date': past_date,
            'time': time(14, 0),
            'hippodrome': self.hippodrome.id,
            'name': 'Кубок чемпионов'
        }
        form = CompetitionForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_competition_form_future_date(self):
        """Тест формы состязания с датой в будущем"""
        future_date = date.today() + timedelta(days=1)
        form_data = {
            'date': future_date,
            'time': time(14, 0),
            'hippodrome': self.hippodrome.id,
            'name': 'Кубок'
        }
        form = CompetitionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    def test_competition_form_too_old_date(self):
        """Тест формы состязания с датой более 10 лет назад"""
        old_date = date.today() - timedelta(days=3651)  # Более 10 лет
        form_data = {
            'date': old_date,
            'time': time(14, 0),
            'hippodrome': self.hippodrome.id,
            'name': 'Кубок'
        }
        form = CompetitionForm(data=form_data)
        self.assertFalse(form.is_valid())


class TestResultForm(BaseTestCase):
    """Тесты для формы ResultForm"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        self.competition = Competition.objects.create(
            hippodrome=self.hippodrome,
            date=date.today() - timedelta(days=1),
            time=time(14, 0)
        )
        self.owner = Owner.objects.create(
            name='Owner',
            address='Test',
            phone='+79991234567'
        )
        self.horse = Horse.objects.create(
            name='Horse',
            gender='M',
            age=5,
            owner=self.owner
        )
        self.jockey = Jockey.objects.create(
            name='Jockey',
            address='Test',
            age=30,
            rating=5
        )
    
    def test_valid_result_form(self):
        """Тест валидной формы результата"""
        form_data = {
            'competition': self.competition.id,
            'horse': self.horse.id,
            'jockey': self.jockey.id,
            'position': 1,
            'time_result': '02:30.500'
        }
        form = ResultForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_result_form_duplicate_horse(self):
        """Тест формы результата с дублирующейся лошадью"""
        # Создаем первый результат
        jockey1 = Jockey.objects.create(
            name='Jockey1',
            address='Test',
            age=30,
            rating=5
        )
        Result.objects.create(
            competition=self.competition,
            horse=self.horse,
            jockey=jockey1,
            position=1,
            time_result=timedelta(minutes=2, seconds=30)
        )
        
        # Пытаемся создать второй результат с той же лошадью
        jockey2 = Jockey.objects.create(
            name='Jockey2',
            address='Test',
            age=30,
            rating=5
        )
        form_data = {
            'competition': self.competition.id,
            'horse': self.horse.id,
            'jockey': jockey2.id,
            'position': 2,
            'time_result': '02:35.000'
        }
        form = ResultForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    def test_result_form_duplicate_position(self):
        """Тест формы результата с дублирующимся местом"""
        # Создаем первый результат
        horse1 = Horse.objects.create(
            name='Horse1',
            gender='M',
            age=5,
            owner=self.owner
        )
        jockey1 = Jockey.objects.create(
            name='Jockey1',
            address='Test',
            age=30,
            rating=5
        )
        Result.objects.create(
            competition=self.competition,
            horse=horse1,
            jockey=jockey1,
            position=1,
            time_result=timedelta(minutes=2, seconds=30)
        )
        
        # Пытаемся создать второй результат с тем же местом
        horse2 = Horse.objects.create(
            name='Horse2',
            gender='M',
            age=5,
            owner=self.owner
        )
        jockey2 = Jockey.objects.create(
            name='Jockey2',
            address='Test',
            age=30,
            rating=5
        )
        form_data = {
            'competition': self.competition.id,
            'horse': horse2.id,
            'jockey': jockey2.id,
            'position': 1,
            'time_result': '02:35.000'
        }
        form = ResultForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
    
    def test_result_form_time_validation(self):
        """Тест валидации времени результата"""
        # Создаем первый результат с временем 02:30
        horse1 = Horse.objects.create(
            name='Horse1',
            gender='M',
            age=5,
            owner=self.owner
        )
        jockey1 = Jockey.objects.create(
            name='Jockey1',
            address='Test',
            age=30,
            rating=5
        )
        Result.objects.create(
            competition=self.competition,
            horse=horse1,
            jockey=jockey1,
            position=1,
            time_result=timedelta(minutes=2, seconds=30)
        )
        
        # Пытаемся создать результат на 2-е место с лучшим временем
        horse2 = Horse.objects.create(
            name='Horse2',
            gender='M',
            age=5,
            owner=self.owner
        )
        jockey2 = Jockey.objects.create(
            name='Jockey2',
            address='Test',
            age=30,
            rating=5
        )
        form_data = {
            'competition': self.competition.id,
            'horse': horse2.id,
            'jockey': jockey2.id,
            'position': 2,
            'time_result': '02:25.000'  # Лучше чем у первого места
        }
        form = ResultForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)


class TestUserRegistrationForm(BaseTestCase):
    """Тесты для формы регистрации пользователя"""
    
    def test_valid_registration_form(self):
        """Тест валидной формы регистрации"""
        form_data = {
            'username': 'newuser',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'email': 'ivan@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'phone': '+79991234567',
            'address': 'Москва'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_registration_form_save(self):
        """Тест сохранения формы регистрации"""
        form_data = {
            'username': 'newuser',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'email': 'ivan@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'phone': '+79991234567',
            'address': 'Москва'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, 'newuser')
        self.assertTrue(UserProfile.objects.filter(user=user, role='user').exists())
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.phone, '+79991234567')
    
    def test_registration_form_phone_normalization(self):
        """Тест нормализации номера телефона при регистрации"""
        form_data = {
            'username': 'newuser',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'email': 'ivan@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'phone': '8 (999) 123-45-67',
            'address': 'Москва'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['phone'], '+79991234567')
    
    def test_registration_form_password_mismatch(self):
        """Тест несовпадения паролей"""
        form_data = {
            'username': 'newuser',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'email': 'ivan@example.com',
            'password1': 'testpass123',
            'password2': 'differentpass',
            'phone': '+79991234567'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
