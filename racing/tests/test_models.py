"""
Unit тесты для моделей приложения racing
"""
import pytest
from datetime import date, time, timedelta
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from racing.models import (
    UserProfile, Hippodrome, Owner, Jockey, Horse, Competition, Result
)


@pytest.mark.unit
class TestUserProfile:
    """Тесты для модели UserProfile"""
    
    def test_user_profile_str(self, db):
        """Тест строкового представления профиля пользователя"""
        from django.contrib.auth.models import User
        user = User.objects.create_user(username='testuser', password='test123')
        profile = UserProfile.objects.create(user=user, role='user')
        assert str(profile) == "testuser (Пользователь)"
    
    def test_user_profile_is_admin(self, db):
        """Тест метода is_admin()"""
        from django.contrib.auth.models import User
        user = User.objects.create_user(username='admin', password='test123')
        profile = UserProfile.objects.create(user=user, role='admin')
        assert profile.is_admin() is True
        assert profile.is_jockey() is False
        assert profile.is_user() is False
    
    def test_user_profile_is_jockey(self, db):
        """Тест метода is_jockey()"""
        from django.contrib.auth.models import User
        user = User.objects.create_user(username='jockey', password='test123')
        jockey = Jockey.objects.create(name='Test Jockey', address='Test', age=30, rating=5)
        profile = UserProfile.objects.create(user=user, role='jockey', jockey=jockey)
        assert profile.is_jockey() is True
        assert profile.is_admin() is False
        assert profile.is_user() is False
    
    def test_user_profile_is_user(self, db):
        """Тест метода is_user()"""
        from django.contrib.auth.models import User
        user = User.objects.create_user(username='user', password='test123')
        profile = UserProfile.objects.create(user=user, role='user')
        assert profile.is_user() is True
        assert profile.is_admin() is False
        assert profile.is_jockey() is False
    
    def test_get_jockey_name(self, db):
        """Тест метода get_jockey_name() для жокея"""
        from django.contrib.auth.models import User
        user = User.objects.create_user(
            username='jockey', password='test123',
            first_name='Иван', last_name='Иванов'
        )
        jockey = Jockey.objects.create(name='Иван Иванов', address='Test', age=30, rating=5)
        profile = UserProfile.objects.create(user=user, role='jockey', jockey=jockey)
        assert profile.get_jockey_name() == 'Иван Иванов'
    
    def test_get_jockey_name_for_non_jockey(self, db):
        """Тест метода get_jockey_name() для не-жокея"""
        from django.contrib.auth.models import User
        user = User.objects.create_user(
            username='user', password='test123',
            first_name='Петр', last_name='Петров'
        )
        profile = UserProfile.objects.create(user=user, role='user')
        assert profile.get_jockey_name() == 'Петр Петров'
    
    def test_get_jockey_rating(self, db):
        """Тест метода get_jockey_rating()"""
        from django.contrib.auth.models import User
        user = User.objects.create_user(username='jockey', password='test123')
        jockey = Jockey.objects.create(name='Test', address='Test', age=30, rating=8)
        profile = UserProfile.objects.create(user=user, role='jockey', jockey=jockey)
        assert profile.get_jockey_rating() == 8
    
    def test_get_jockey_rating_for_non_jockey(self, db):
        """Тест метода get_jockey_rating() для не-жокея"""
        from django.contrib.auth.models import User
        user = User.objects.create_user(username='user', password='test123')
        profile = UserProfile.objects.create(user=user, role='user')
        assert profile.get_jockey_rating() is None
    
    def test_get_jockey_age(self, db):
        """Тест метода get_jockey_age()"""
        from django.contrib.auth.models import User
        user = User.objects.create_user(username='jockey', password='test123')
        jockey = Jockey.objects.create(name='Test', address='Test', age=35, rating=5)
        profile = UserProfile.objects.create(user=user, role='jockey', jockey=jockey)
        assert profile.get_jockey_age() == 35


@pytest.mark.unit
class TestHippodrome:
    """Тесты для модели Hippodrome"""
    
    def test_hippodrome_str(self, db):
        """Тест строкового представления ипподрома"""
        hippodrome = Hippodrome.objects.create(
            name='Центральный ипподром',
            address='Москва',
            capacity=10000
        )
        assert str(hippodrome) == 'Центральный ипподром'
    
    def test_hippodrome_ordering(self, db):
        """Тест упорядочивания ипподромов"""
        Hippodrome.objects.create(name='Б', address='Test')
        Hippodrome.objects.create(name='А', address='Test')
        hippodromes = list(Hippodrome.objects.all())
        assert hippodromes[0].name == 'А'
        assert hippodromes[1].name == 'Б'


@pytest.mark.unit
class TestOwner:
    """Тесты для модели Owner"""
    
    def test_owner_str(self, db):
        """Тест строкового представления владельца"""
        owner = Owner.objects.create(
            name='Иван Петров',
            address='Москва',
            phone='+79991234567'
        )
        assert str(owner) == 'Иван Петров'


@pytest.mark.unit
class TestJockey:
    """Тесты для модели Jockey"""
    
    def test_jockey_str(self, db):
        """Тест строкового представления жокея"""
        jockey = Jockey.objects.create(
            name='Алексей Смирнов',
            address='Москва',
            age=30,
            rating=5
        )
        assert str(jockey) == 'Алексей Смирнов'
    
    def test_jockey_rating_validation_min(self, db):
        """Тест валидации минимального рейтинга"""
        jockey = Jockey(name='Test', address='Test', age=30, rating=0)
        with pytest.raises(ValidationError):
            jockey.full_clean()
    
    def test_jockey_rating_validation_max(self, db):
        """Тест валидации максимального рейтинга"""
        jockey = Jockey(name='Test', address='Test', age=30, rating=11)
        with pytest.raises(ValidationError):
            jockey.full_clean()
    
    def test_jockey_rating_valid(self, db):
        """Тест валидного рейтинга"""
        jockey = Jockey.objects.create(
            name='Test',
            address='Test',
            age=30,
            rating=5
        )
        jockey.full_clean()  # Не должно вызывать исключение


@pytest.mark.unit
class TestHorse:
    """Тесты для модели Horse"""
    
    def test_horse_str(self, db):
        """Тест строкового представления лошади"""
        owner = Owner.objects.create(name='Owner', address='Test', phone='+79991234567')
        horse = Horse.objects.create(
            name='Быстрый',
            gender='M',
            age=5,
            owner=owner
        )
        assert str(horse) == 'Быстрый'
    
    def test_horse_gender_choices(self, db):
        """Тест выбора пола лошади"""
        owner = Owner.objects.create(name='Owner', address='Test', phone='+79991234567')
        horse_m = Horse.objects.create(name='M', gender='M', age=5, owner=owner)
        horse_f = Horse.objects.create(name='F', gender='F', age=5, owner=owner)
        assert horse_m.gender == 'M'
        assert horse_f.gender == 'F'


@pytest.mark.unit
class TestCompetition:
    """Тесты для модели Competition"""
    
    def test_competition_str_with_name(self, db):
        """Тест строкового представления состязания с названием"""
        hippodrome = Hippodrome.objects.create(name='Центральный', address='Test')
        competition = Competition.objects.create(
            name='Кубок чемпионов',
            hippodrome=hippodrome,
            date=date(2024, 1, 15),
            time=time(14, 0)
        )
        assert 'Кубок чемпионов' in str(competition)
        assert 'Центральный' in str(competition)
    
    def test_competition_str_without_name(self, db):
        """Тест строкового представления состязания без названия"""
        hippodrome = Hippodrome.objects.create(name='Центральный', address='Test')
        competition = Competition.objects.create(
            name=None,
            hippodrome=hippodrome,
            date=date(2024, 1, 15),
            time=time(14, 0)
        )
        assert 'Состязание' in str(competition)
        assert 'Центральный' in str(competition)
    
    def test_competition_ordering(self, db):
        """Тест упорядочивания состязаний"""
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        comp1 = Competition.objects.create(
            hippodrome=hippodrome,
            date=date(2024, 1, 15),
            time=time(14, 0)
        )
        comp2 = Competition.objects.create(
            hippodrome=hippodrome,
            date=date(2024, 1, 16),
            time=time(15, 0)
        )
        competitions = list(Competition.objects.all())
        # Более поздние даты должны быть первыми
        assert competitions[0].date >= competitions[1].date


@pytest.mark.unit
class TestResult:
    """Тесты для модели Result"""
    
    def test_result_str(self, db):
        """Тест строкового представления результата"""
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        competition = Competition.objects.create(
            name='Кубок',
            hippodrome=hippodrome,
            date=date(2024, 1, 15),
            time=time(14, 0)
        )
        owner = Owner.objects.create(name='Owner', address='Test', phone='+79991234567')
        horse = Horse.objects.create(name='Быстрый', gender='M', age=5, owner=owner)
        jockey = Jockey.objects.create(name='Jockey', address='Test', age=30, rating=5)
        result = Result.objects.create(
            competition=competition,
            horse=horse,
            jockey=jockey,
            position=1,
            time_result=timedelta(minutes=2, seconds=30, milliseconds=500)
        )
        assert 'Кубок' in str(result)
        assert 'Быстрый' in str(result)
        assert '1 место' in str(result)
    
    def test_result_unique_together(self, db):
        """Тест уникальности комбинации competition и position"""
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        competition = Competition.objects.create(
            hippodrome=hippodrome,
            date=date(2024, 1, 15),
            time=time(14, 0)
        )
        owner = Owner.objects.create(name='Owner', address='Test', phone='+79991234567')
        horse1 = Horse.objects.create(name='Horse1', gender='M', age=5, owner=owner)
        horse2 = Horse.objects.create(name='Horse2', gender='M', age=5, owner=owner)
        jockey1 = Jockey.objects.create(name='Jockey1', address='Test', age=30, rating=5)
        jockey2 = Jockey.objects.create(name='Jockey2', address='Test', age=30, rating=5)
        
        Result.objects.create(
            competition=competition,
            horse=horse1,
            jockey=jockey1,
            position=1,
            time_result=timedelta(minutes=2, seconds=30)
        )
        
        # Попытка создать второй результат с тем же местом должна вызвать ошибку
        with pytest.raises(IntegrityError):
            Result.objects.create(
                competition=competition,
                horse=horse2,
                jockey=jockey2,
                position=1,
                time_result=timedelta(minutes=2, seconds=35)
            )
    
    def test_get_formatted_time(self, db):
        """Тест форматирования времени результата"""
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        competition = Competition.objects.create(
            hippodrome=hippodrome,
            date=date(2024, 1, 15),
            time=time(14, 0)
        )
        owner = Owner.objects.create(name='Owner', address='Test', phone='+79991234567')
        horse = Horse.objects.create(name='Horse', gender='M', age=5, owner=owner)
        jockey = Jockey.objects.create(name='Jockey', address='Test', age=30, rating=5)
        result = Result.objects.create(
            competition=competition,
            horse=horse,
            jockey=jockey,
            position=1,
            time_result=timedelta(minutes=2, seconds=30, milliseconds=500)
        )
        formatted = result.get_formatted_time()
        assert formatted == "02:30.500"
    
    def test_get_formatted_time_zero(self, db):
        """Тест форматирования нулевого времени"""
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        competition = Competition.objects.create(
            hippodrome=hippodrome,
            date=date(2024, 1, 15),
            time=time(14, 0)
        )
        owner = Owner.objects.create(name='Owner', address='Test', phone='+79991234567')
        horse = Horse.objects.create(name='Horse', gender='M', age=5, owner=owner)
        jockey = Jockey.objects.create(name='Jockey', address='Test', age=30, rating=5)
        result = Result.objects.create(
            competition=competition,
            horse=horse,
            jockey=jockey,
            position=1,
            time_result=timedelta(0)
        )
        formatted = result.get_formatted_time()
        assert formatted == "00:00.000"
    
    def test_get_formatted_time_with_seconds_only(self, db):
        """Тест форматирования времени только с секундами"""
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        competition = Competition.objects.create(
            hippodrome=hippodrome,
            date=date(2024, 1, 15),
            time=time(14, 0)
        )
        owner = Owner.objects.create(name='Owner', address='Test', phone='+79991234567')
        horse = Horse.objects.create(name='Horse', gender='M', age=5, owner=owner)
        jockey = Jockey.objects.create(name='Jockey', address='Test', age=30, rating=5)
        result = Result.objects.create(
            competition=competition,
            horse=horse,
            jockey=jockey,
            position=1,
            time_result=timedelta(seconds=45, milliseconds=250)
        )
        formatted = result.get_formatted_time()
        assert formatted == "00:45.250"

