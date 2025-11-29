"""
Unit тесты для моделей приложения racing
"""
import unittest
from datetime import date, time, timedelta
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.contrib.auth.models import User
from racing.models import (
    UserProfile, Hippodrome, Owner, Jockey, Horse, Competition, Result
)


class TestUserProfile(TestCase):
    """Тесты для модели UserProfile"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create_user(
            username='testuser',
            password='test123',
            first_name='Иван',
            last_name='Иванов'
        )
    
    def test_user_profile_str(self):
        """Тест строкового представления профиля пользователя"""
        profile = UserProfile.objects.create(user=self.user, role='user')
        self.assertEqual(str(profile), "testuser (Пользователь)")
    
    def test_user_profile_is_admin(self):
        """Тест метода is_admin()"""
        profile = UserProfile.objects.create(user=self.user, role='admin')
        self.assertTrue(profile.is_admin())
        self.assertFalse(profile.is_jockey())
        self.assertFalse(profile.is_user())
    
    def test_user_profile_is_jockey(self):
        """Тест метода is_jockey()"""
        jockey = Jockey.objects.create(
            name='Test Jockey',
            address='Test',
            age=30,
            rating=5
        )
        profile = UserProfile.objects.create(
            user=self.user,
            role='jockey',
            jockey=jockey
        )
        self.assertTrue(profile.is_jockey())
        self.assertFalse(profile.is_admin())
        self.assertFalse(profile.is_user())
    
    def test_user_profile_is_user(self):
        """Тест метода is_user()"""
        profile = UserProfile.objects.create(user=self.user, role='user')
        self.assertTrue(profile.is_user())
        self.assertFalse(profile.is_admin())
        self.assertFalse(profile.is_jockey())
    
    def test_get_jockey_name(self):
        """Тест метода get_jockey_name() для жокея"""
        jockey = Jockey.objects.create(
            name='Иван Иванов',
            address='Test',
            age=30,
            rating=5
        )
        profile = UserProfile.objects.create(
            user=self.user,
            role='jockey',
            jockey=jockey
        )
        self.assertEqual(profile.get_jockey_name(), 'Иван Иванов')
    
    def test_get_jockey_name_for_non_jockey(self):
        """Тест метода get_jockey_name() для не-жокея"""
        profile = UserProfile.objects.create(user=self.user, role='user')
        self.assertEqual(profile.get_jockey_name(), 'Иван Иванов')
    
    def test_get_jockey_rating(self):
        """Тест метода get_jockey_rating()"""
        jockey = Jockey.objects.create(
            name='Test',
            address='Test',
            age=30,
            rating=8
        )
        profile = UserProfile.objects.create(
            user=self.user,
            role='jockey',
            jockey=jockey
        )
        self.assertEqual(profile.get_jockey_rating(), 8)
    
    def test_get_jockey_rating_for_non_jockey(self):
        """Тест метода get_jockey_rating() для не-жокея"""
        profile = UserProfile.objects.create(user=self.user, role='user')
        self.assertIsNone(profile.get_jockey_rating())
    
    def test_get_jockey_age(self):
        """Тест метода get_jockey_age()"""
        jockey = Jockey.objects.create(
            name='Test',
            address='Test',
            age=35,
            rating=5
        )
        profile = UserProfile.objects.create(
            user=self.user,
            role='jockey',
            jockey=jockey
        )
        self.assertEqual(profile.get_jockey_age(), 35)


class TestHippodrome(TestCase):
    """Тесты для модели Hippodrome"""
    
    def test_hippodrome_str(self):
        """Тест строкового представления ипподрома"""
        hippodrome = Hippodrome.objects.create(
            name='Центральный ипподром',
            address='Москва',
            capacity=10000
        )
        self.assertEqual(str(hippodrome), 'Центральный ипподром')
    
    def test_hippodrome_ordering(self):
        """Тест упорядочивания ипподромов"""
        Hippodrome.objects.create(name='Б', address='Test')
        Hippodrome.objects.create(name='А', address='Test')
        hippodromes = list(Hippodrome.objects.all())
        self.assertEqual(hippodromes[0].name, 'А')
        self.assertEqual(hippodromes[1].name, 'Б')


class TestOwner(TestCase):
    """Тесты для модели Owner"""
    
    def test_owner_str(self):
        """Тест строкового представления владельца"""
        owner = Owner.objects.create(
            name='Иван Петров',
            address='Москва',
            phone='+79991234567'
        )
        self.assertEqual(str(owner), 'Иван Петров')


class TestJockey(TestCase):
    """Тесты для модели Jockey"""
    
    def test_jockey_str(self):
        """Тест строкового представления жокея"""
        jockey = Jockey.objects.create(
            name='Алексей Смирнов',
            address='Москва',
            age=30,
            rating=5
        )
        self.assertEqual(str(jockey), 'Алексей Смирнов')
    
    def test_jockey_rating_validation_min(self):
        """Тест валидации минимального рейтинга"""
        jockey = Jockey(name='Test', address='Test', age=30, rating=0)
        with self.assertRaises(ValidationError):
            jockey.full_clean()
    
    def test_jockey_rating_validation_max(self):
        """Тест валидации максимального рейтинга"""
        jockey = Jockey(name='Test', address='Test', age=30, rating=11)
        with self.assertRaises(ValidationError):
            jockey.full_clean()
    
    def test_jockey_rating_valid(self):
        """Тест валидного рейтинга"""
        jockey = Jockey.objects.create(
            name='Test',
            address='Test',
            age=30,
            rating=5
        )
        jockey.full_clean()  # Не должно вызывать исключение


class TestHorse(TestCase):
    """Тесты для модели Horse"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.owner = Owner.objects.create(
            name='Owner',
            address='Test',
            phone='+79991234567'
        )
    
    def test_horse_str(self):
        """Тест строкового представления лошади"""
        horse = Horse.objects.create(
            name='Быстрый',
            gender='M',
            age=5,
            owner=self.owner
        )
        self.assertEqual(str(horse), 'Быстрый')
    
    def test_horse_gender_choices(self):
        """Тест выбора пола лошади"""
        horse_m = Horse.objects.create(
            name='M',
            gender='M',
            age=5,
            owner=self.owner
        )
        horse_f = Horse.objects.create(
            name='F',
            gender='F',
            age=5,
            owner=self.owner
        )
        self.assertEqual(horse_m.gender, 'M')
        self.assertEqual(horse_f.gender, 'F')


class TestCompetition(TestCase):
    """Тесты для модели Competition"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.hippodrome = Hippodrome.objects.create(
            name='Центральный',
            address='Test'
        )
    
    def test_competition_str_with_name(self):
        """Тест строкового представления состязания с названием"""
        competition = Competition.objects.create(
            name='Кубок чемпионов',
            hippodrome=self.hippodrome,
            date=date(2024, 1, 15),
            time=time(14, 0)
        )
        self.assertIn('Кубок чемпионов', str(competition))
        self.assertIn('Центральный', str(competition))
    
    def test_competition_str_without_name(self):
        """Тест строкового представления состязания без названия"""
        competition = Competition.objects.create(
            name=None,
            hippodrome=self.hippodrome,
            date=date(2024, 1, 15),
            time=time(14, 0)
        )
        self.assertIn('Состязание', str(competition))
        self.assertIn('Центральный', str(competition))
    
    def test_competition_ordering(self):
        """Тест упорядочивания состязаний"""
        comp1 = Competition.objects.create(
            hippodrome=self.hippodrome,
            date=date(2024, 1, 15),
            time=time(14, 0)
        )
        comp2 = Competition.objects.create(
            hippodrome=self.hippodrome,
            date=date(2024, 1, 16),
            time=time(15, 0)
        )
        competitions = list(Competition.objects.all())
        # Более поздние даты должны быть первыми
        self.assertGreaterEqual(competitions[0].date, competitions[1].date)


class TestResult(TestCase):
    """Тесты для модели Result"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        self.competition = Competition.objects.create(
            name='Кубок',
            hippodrome=self.hippodrome,
            date=date(2024, 1, 15),
            time=time(14, 0)
        )
        self.owner = Owner.objects.create(
            name='Owner',
            address='Test',
            phone='+79991234567'
        )
        self.horse = Horse.objects.create(
            name='Быстрый',
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
    
    def test_result_str(self):
        """Тест строкового представления результата"""
        result = Result.objects.create(
            competition=self.competition,
            horse=self.horse,
            jockey=self.jockey,
            position=1,
            time_result=timedelta(minutes=2, seconds=30, milliseconds=500)
        )
        self.assertIn('Кубок', str(result))
        self.assertIn('Быстрый', str(result))
        self.assertIn('1 место', str(result))
    
    def test_result_unique_together(self):
        """Тест уникальности комбинации competition и position"""
        Result.objects.create(
            competition=self.competition,
            horse=self.horse,
            jockey=self.jockey,
            position=1,
            time_result=timedelta(minutes=2, seconds=30)
        )
        
        # Создаем вторую лошадь и жокея
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
        
        # Попытка создать второй результат с тем же местом должна вызвать ошибку
        with self.assertRaises(IntegrityError):
            Result.objects.create(
                competition=self.competition,
                horse=horse2,
                jockey=jockey2,
                position=1,
                time_result=timedelta(minutes=2, seconds=35)
            )
    
    def test_get_formatted_time(self):
        """Тест форматирования времени результата"""
        result = Result.objects.create(
            competition=self.competition,
            horse=self.horse,
            jockey=self.jockey,
            position=1,
            time_result=timedelta(minutes=2, seconds=30, milliseconds=500)
        )
        formatted = result.get_formatted_time()
        self.assertEqual(formatted, "02:30.500")
    
    def test_get_formatted_time_zero(self):
        """Тест форматирования нулевого времени"""
        result = Result.objects.create(
            competition=self.competition,
            horse=self.horse,
            jockey=self.jockey,
            position=1,
            time_result=timedelta(0)
        )
        formatted = result.get_formatted_time()
        self.assertEqual(formatted, "00:00.000")
    
    def test_get_formatted_time_with_seconds_only(self):
        """Тест форматирования времени только с секундами"""
        result = Result.objects.create(
            competition=self.competition,
            horse=self.horse,
            jockey=self.jockey,
            position=1,
            time_result=timedelta(seconds=45, milliseconds=250)
        )
        formatted = result.get_formatted_time()
        self.assertEqual(formatted, "00:45.250")
