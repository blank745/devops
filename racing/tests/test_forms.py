"""
Unit тесты для форм приложения racing
"""
import pytest
from datetime import date, time, timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from racing.forms import (
    HippodromeForm, OwnerForm, JockeyForm, HorseForm,
    CompetitionForm, ResultForm, UserRegistrationForm
)
from racing.models import (
    Hippodrome, Owner, Jockey, Horse, Competition, Result, UserProfile
)


@pytest.mark.unit
class TestHippodromeForm:
    """Тесты для формы HippodromeForm"""
    
    def test_valid_hippodrome_form(self, db):
        """Тест валидной формы ипподрома"""
        form_data = {
            'name': 'Центральный ипподром',
            'address': 'Москва, ул. Ленина, 1',
            'capacity': 10000,
            'description': 'Крупнейший ипподром',
            'is_active': True
        }
        form = HippodromeForm(data=form_data)
        assert form.is_valid()
    
    def test_hippodrome_form_save(self, db):
        """Тест сохранения формы ипподрома"""
        form_data = {
            'name': 'Центральный ипподром',
            'address': 'Москва',
            'capacity': 10000,
            'is_active': True
        }
        form = HippodromeForm(data=form_data)
        assert form.is_valid()
        hippodrome = form.save()
        assert hippodrome.name == 'Центральный ипподром'
        assert Hippodrome.objects.filter(name='Центральный ипподром').exists()


@pytest.mark.unit
class TestOwnerForm:
    """Тесты для формы OwnerForm"""
    
    def test_valid_owner_form(self, db):
        """Тест валидной формы владельца"""
        form_data = {
            'name': 'Иван Петров',
            'address': 'Москва',
            'phone': '+79991234567'
        }
        form = OwnerForm(data=form_data)
        assert form.is_valid()
    
    def test_owner_form_phone_normalization(self, db):
        """Тест нормализации номера телефона"""
        form_data = {
            'name': 'Иван Петров',
            'address': 'Москва',
            'phone': '8 (999) 123-45-67'
        }
        form = OwnerForm(data=form_data)
        assert form.is_valid()
        assert form.cleaned_data['phone'] == '+79991234567'
    
    def test_owner_form_invalid_phone(self, db):
        """Тест невалидного номера телефона"""
        form_data = {
            'name': 'Иван Петров',
            'address': 'Москва',
            'phone': '12345'
        }
        form = OwnerForm(data=form_data)
        assert not form.is_valid()
        assert 'phone' in form.errors
    
    def test_owner_form_phone_with_8(self, db):
        """Тест номера телефона начинающегося с 8"""
        form_data = {
            'name': 'Иван Петров',
            'address': 'Москва',
            'phone': '89991234567'
        }
        form = OwnerForm(data=form_data)
        assert form.is_valid()
        assert form.cleaned_data['phone'].startswith('+7')


@pytest.mark.unit
class TestJockeyForm:
    """Тесты для формы JockeyForm"""
    
    def test_valid_jockey_form(self, db):
        """Тест валидной формы жокея"""
        form_data = {
            'name': 'Алексей Смирнов',
            'address': 'Москва',
            'age': 30,
            'rating': 5
        }
        form = JockeyForm(data=form_data)
        assert form.is_valid()
    
    def test_jockey_form_save(self, db):
        """Тест сохранения формы жокея"""
        form_data = {
            'name': 'Алексей Смирнов',
            'address': 'Москва',
            'age': 30,
            'rating': 8
        }
        form = JockeyForm(data=form_data)
        assert form.is_valid()
        jockey = form.save()
        assert jockey.name == 'Алексей Смирнов'
        assert jockey.rating == 8


@pytest.mark.unit
class TestHorseForm:
    """Тесты для формы HorseForm"""
    
    def test_valid_horse_form(self, db):
        """Тест валидной формы лошади"""
        owner = Owner.objects.create(name='Owner', address='Test', phone='+79991234567')
        form_data = {
            'name': 'Быстрый',
            'gender': 'M',
            'age': 5,
            'owner': owner.id
        }
        form = HorseForm(data=form_data)
        assert form.is_valid()
    
    def test_horse_form_save(self, db):
        """Тест сохранения формы лошади"""
        owner = Owner.objects.create(name='Owner', address='Test', phone='+79991234567')
        form_data = {
            'name': 'Быстрый',
            'gender': 'F',
            'age': 5,
            'owner': owner.id
        }
        form = HorseForm(data=form_data)
        assert form.is_valid()
        horse = form.save()
        assert horse.name == 'Быстрый'
        assert horse.gender == 'F'


@pytest.mark.unit
class TestCompetitionForm:
    """Тесты для формы CompetitionForm"""
    
    def test_valid_competition_form(self, db):
        """Тест валидной формы состязания"""
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        past_date = date.today() - timedelta(days=1)
        form_data = {
            'date': past_date,
            'time': time(14, 0),
            'hippodrome': hippodrome.id,
            'name': 'Кубок чемпионов'
        }
        form = CompetitionForm(data=form_data)
        assert form.is_valid()
    
    def test_competition_form_future_date(self, db):
        """Тест формы состязания с датой в будущем"""
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        future_date = date.today() + timedelta(days=1)
        form_data = {
            'date': future_date,
            'time': time(14, 0),
            'hippodrome': hippodrome.id,
            'name': 'Кубок'
        }
        form = CompetitionForm(data=form_data)
        assert not form.is_valid()
        assert '__all__' in form.errors
    
    def test_competition_form_too_old_date(self, db):
        """Тест формы состязания с датой более 10 лет назад"""
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        old_date = date.today() - timedelta(days=3651)  # Более 10 лет
        form_data = {
            'date': old_date,
            'time': time(14, 0),
            'hippodrome': hippodrome.id,
            'name': 'Кубок'
        }
        form = CompetitionForm(data=form_data)
        assert not form.is_valid()


@pytest.mark.unit
class TestResultForm:
    """Тесты для формы ResultForm"""
    
    def test_valid_result_form(self, db):
        """Тест валидной формы результата"""
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        competition = Competition.objects.create(
            hippodrome=hippodrome,
            date=date.today() - timedelta(days=1),
            time=time(14, 0)
        )
        owner = Owner.objects.create(name='Owner', address='Test', phone='+79991234567')
        horse = Horse.objects.create(name='Horse', gender='M', age=5, owner=owner)
        jockey = Jockey.objects.create(name='Jockey', address='Test', age=30, rating=5)
        
        form_data = {
            'competition': competition.id,
            'horse': horse.id,
            'jockey': jockey.id,
            'position': 1,
            'time_result': '02:30.500'
        }
        form = ResultForm(data=form_data)
        assert form.is_valid()
    
    def test_result_form_duplicate_horse(self, db):
        """Тест формы результата с дублирующейся лошадью"""
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        competition = Competition.objects.create(
            hippodrome=hippodrome,
            date=date.today() - timedelta(days=1),
            time=time(14, 0)
        )
        owner = Owner.objects.create(name='Owner', address='Test', phone='+79991234567')
        horse = Horse.objects.create(name='Horse', gender='M', age=5, owner=owner)
        jockey1 = Jockey.objects.create(name='Jockey1', address='Test', age=30, rating=5)
        jockey2 = Jockey.objects.create(name='Jockey2', address='Test', age=30, rating=5)
        
        # Создаем первый результат
        Result.objects.create(
            competition=competition,
            horse=horse,
            jockey=jockey1,
            position=1,
            time_result=timedelta(minutes=2, seconds=30)
        )
        
        # Пытаемся создать второй результат с той же лошадью
        form_data = {
            'competition': competition.id,
            'horse': horse.id,
            'jockey': jockey2.id,
            'position': 2,
            'time_result': '02:35.000'
        }
        form = ResultForm(data=form_data)
        assert not form.is_valid()
        assert '__all__' in form.errors
    
    def test_result_form_duplicate_position(self, db):
        """Тест формы результата с дублирующимся местом"""
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        competition = Competition.objects.create(
            hippodrome=hippodrome,
            date=date.today() - timedelta(days=1),
            time=time(14, 0)
        )
        owner = Owner.objects.create(name='Owner', address='Test', phone='+79991234567')
        horse1 = Horse.objects.create(name='Horse1', gender='M', age=5, owner=owner)
        horse2 = Horse.objects.create(name='Horse2', gender='M', age=5, owner=owner)
        jockey1 = Jockey.objects.create(name='Jockey1', address='Test', age=30, rating=5)
        jockey2 = Jockey.objects.create(name='Jockey2', address='Test', age=30, rating=5)
        
        # Создаем первый результат
        Result.objects.create(
            competition=competition,
            horse=horse1,
            jockey=jockey1,
            position=1,
            time_result=timedelta(minutes=2, seconds=30)
        )
        
        # Пытаемся создать второй результат с тем же местом
        form_data = {
            'competition': competition.id,
            'horse': horse2.id,
            'jockey': jockey2.id,
            'position': 1,
            'time_result': '02:35.000'
        }
        form = ResultForm(data=form_data)
        assert not form.is_valid()
        assert '__all__' in form.errors
    
    def test_result_form_time_validation(self, db):
        """Тест валидации времени результата"""
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        competition = Competition.objects.create(
            hippodrome=hippodrome,
            date=date.today() - timedelta(days=1),
            time=time(14, 0)
        )
        owner = Owner.objects.create(name='Owner', address='Test', phone='+79991234567')
        horse1 = Horse.objects.create(name='Horse1', gender='M', age=5, owner=owner)
        horse2 = Horse.objects.create(name='Horse2', gender='M', age=5, owner=owner)
        jockey1 = Jockey.objects.create(name='Jockey1', address='Test', age=30, rating=5)
        jockey2 = Jockey.objects.create(name='Jockey2', address='Test', age=30, rating=5)
        
        # Создаем первый результат с временем 02:30
        Result.objects.create(
            competition=competition,
            horse=horse1,
            jockey=jockey1,
            position=1,
            time_result=timedelta(minutes=2, seconds=30)
        )
        
        # Пытаемся создать результат на 2-е место с лучшим временем
        form_data = {
            'competition': competition.id,
            'horse': horse2.id,
            'jockey': jockey2.id,
            'position': 2,
            'time_result': '02:25.000'  # Лучше чем у первого места
        }
        form = ResultForm(data=form_data)
        assert not form.is_valid()
        assert '__all__' in form.errors


@pytest.mark.unit
class TestUserRegistrationForm:
    """Тесты для формы регистрации пользователя"""
    
    def test_valid_registration_form(self, db):
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
        assert form.is_valid()
    
    def test_registration_form_save(self, db):
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
        assert form.is_valid()
        user = form.save()
        assert user.username == 'newuser'
        assert UserProfile.objects.filter(user=user, role='user').exists()
        profile = UserProfile.objects.get(user=user)
        assert profile.phone == '+79991234567'
    
    def test_registration_form_phone_normalization(self, db):
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
        assert form.is_valid()
        assert form.cleaned_data['phone'] == '+79991234567'
    
    def test_registration_form_password_mismatch(self, db):
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
        assert not form.is_valid()

