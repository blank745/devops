"""
Integration тесты для views приложения racing
"""
import unittest
from datetime import date, time, timedelta
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from racing.models import (
    UserProfile, Hippodrome, Owner, Jockey, Horse, Competition, Result
)


class TestIndexView(TestCase):
    """Интеграционные тесты для главной страницы"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
    
    def test_index_view_anonymous(self):
        """Тест главной страницы для анонимного пользователя"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('recent_competitions', response.context)
    
    def test_index_view_authenticated(self):
        """Тест главной страницы для авторизованного пользователя"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        self.client.force_login(user)
        
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)


class TestCompetitionViews(TestCase):
    """Интеграционные тесты для views состязаний"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
    
    def test_competition_list_requires_login(self):
        """Тест что список состязаний требует авторизации"""
        response = self.client.get(reverse('competition_list'))
        self.assertEqual(response.status_code, 302)  # Редирект на логин
    
    def test_competition_list_authenticated(self):
        """Тест списка состязаний для авторизованного пользователя"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        self.client.force_login(user)
        
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        Competition.objects.create(
            hippodrome=hippodrome,
            date=date.today(),
            time=time(14, 0)
        )
        
        response = self.client.get(reverse('competition_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['competitions']), 1)
    
    def test_competition_detail(self):
        """Тест детальной страницы состязания"""
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        competition = Competition.objects.create(
            hippodrome=hippodrome,
            date=date.today(),
            time=time(14, 0)
        )
        
        response = self.client.get(reverse('competition_detail', args=[competition.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['competition'], competition)
    
    def test_add_competition_requires_jockey_or_admin(self):
        """Тест что добавление состязания требует прав жокея или админа"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        self.client.force_login(user)
        
        response = self.client.get(reverse('add_competition'))
        self.assertEqual(response.status_code, 302)  # Редирект из-за недостатка прав
    
    def test_add_competition_as_admin(self):
        """Тест добавления состязания администратором"""
        user = User.objects.create_user(username='admin', password='test123')
        UserProfile.objects.create(user=user, role='admin')
        self.client.force_login(user)
        
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        
        response = self.client.get(reverse('add_competition'))
        self.assertEqual(response.status_code, 200)
        
        # POST запрос
        past_date = date.today() - timedelta(days=1)
        response = self.client.post(reverse('add_competition'), {
            'date': past_date,
            'time': '14:00',
            'hippodrome': hippodrome.id,
            'name': 'Новое состязание'
        })
        self.assertEqual(response.status_code, 302)  # Редирект после успешного создания
        self.assertTrue(Competition.objects.filter(name='Новое состязание').exists())


class TestJockeyViews(TestCase):
    """Интеграционные тесты для views жокеев"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
    
    def test_jockey_list_requires_login(self):
        """Тест что список жокеев требует авторизации"""
        response = self.client.get(reverse('jockey_list'))
        self.assertEqual(response.status_code, 302)
    
    def test_jockey_list_authenticated(self):
        """Тест списка жокеев для авторизованного пользователя"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        self.client.force_login(user)
        
        Jockey.objects.create(name='Jockey1', address='Test', age=30, rating=5)
        Jockey.objects.create(name='Jockey2', address='Test', age=35, rating=7)
        
        response = self.client.get(reverse('jockey_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['all_jockeys']), 2)
    
    def test_add_jockey_requires_admin(self):
        """Тест что добавление жокея требует прав администратора"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        self.client.force_login(user)
        
        response = self.client.get(reverse('add_jockey'))
        self.assertEqual(response.status_code, 302)
    
    def test_add_jockey_as_admin(self):
        """Тест добавления жокея администратором"""
        user = User.objects.create_user(username='admin', password='test123')
        UserProfile.objects.create(user=user, role='admin')
        self.client.force_login(user)
        
        response = self.client.get(reverse('add_jockey'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(reverse('add_jockey'), {
            'name': 'Новый жокей',
            'address': 'Москва',
            'age': 30,
            'rating': 8
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Jockey.objects.filter(name='Новый жокей').exists())
    
    def test_jockey_competitions(self):
        """Тест списка состязаний жокея"""
        jockey = Jockey.objects.create(name='Jockey', address='Test', age=30, rating=5)
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        competition = Competition.objects.create(
            hippodrome=hippodrome,
            date=date.today(),
            time=time(14, 0)
        )
        owner = Owner.objects.create(name='Owner', address='Test', phone='+79991234567')
        horse = Horse.objects.create(name='Horse', gender='M', age=5, owner=owner)
        Result.objects.create(
            competition=competition,
            horse=horse,
            jockey=jockey,
            position=1,
            time_result=timedelta(minutes=2, seconds=30)
        )
        
        response = self.client.get(reverse('jockey_competitions', args=[jockey.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['results']), 1)


class TestHorseViews(TestCase):
    """Интеграционные тесты для views лошадей"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
    
    def test_horse_list_requires_login(self):
        """Тест что список лошадей требует авторизации"""
        response = self.client.get(reverse('horse_list'))
        self.assertEqual(response.status_code, 302)
    
    def test_horse_list_authenticated(self):
        """Тест списка лошадей для авторизованного пользователя"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        self.client.force_login(user)
        
        owner = Owner.objects.create(name='Owner', address='Test', phone='+79991234567')
        Horse.objects.create(name='Horse1', gender='M', age=5, owner=owner)
        Horse.objects.create(name='Horse2', gender='F', age=6, owner=owner)
        
        response = self.client.get(reverse('horse_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['horses']), 2)
    
    def test_add_horse_requires_jockey_or_admin(self):
        """Тест что добавление лошади требует прав жокея или админа"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        self.client.force_login(user)
        
        response = self.client.get(reverse('add_horse'))
        self.assertEqual(response.status_code, 302)
    
    def test_add_horse_as_jockey(self):
        """Тест добавления лошади жокеем"""
        user = User.objects.create_user(username='jockey', password='test123')
        jockey = Jockey.objects.create(name='Jockey', address='Test', age=30, rating=5)
        UserProfile.objects.create(user=user, role='jockey', jockey=jockey)
        self.client.force_login(user)
        
        owner = Owner.objects.create(name='Owner', address='Test', phone='+79991234567')
        
        response = self.client.get(reverse('add_horse'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(reverse('add_horse'), {
            'name': 'Новая лошадь',
            'gender': 'M',
            'age': 5,
            'owner': owner.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Horse.objects.filter(name='Новая лошадь').exists())
    
    def test_horse_competitions(self):
        """Тест списка состязаний лошади"""
        owner = Owner.objects.create(name='Owner', address='Test', phone='+79991234567')
        horse = Horse.objects.create(name='Horse', gender='M', age=5, owner=owner)
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        competition = Competition.objects.create(
            hippodrome=hippodrome,
            date=date.today(),
            time=time(14, 0)
        )
        jockey = Jockey.objects.create(name='Jockey', address='Test', age=30, rating=5)
        Result.objects.create(
            competition=competition,
            horse=horse,
            jockey=jockey,
            position=1,
            time_result=timedelta(minutes=2, seconds=30)
        )
        
        response = self.client.get(reverse('horse_competitions', args=[horse.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['results']), 1)


class TestResultViews(TestCase):
    """Интеграционные тесты для views результатов"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
    
    def test_add_result_requires_jockey_or_admin(self):
        """Тест что добавление результата требует прав жокея или админа"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        self.client.force_login(user)
        
        response = self.client.get(reverse('add_result'))
        self.assertEqual(response.status_code, 302)
    
    def test_add_result_as_admin(self):
        """Тест добавления результата администратором"""
        user = User.objects.create_user(username='admin', password='test123')
        UserProfile.objects.create(user=user, role='admin')
        self.client.force_login(user)
        
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        competition = Competition.objects.create(
            hippodrome=hippodrome,
            date=date.today() - timedelta(days=1),
            time=time(14, 0)
        )
        owner = Owner.objects.create(name='Owner', address='Test', phone='+79991234567')
        horse = Horse.objects.create(name='Horse', gender='M', age=5, owner=owner)
        jockey = Jockey.objects.create(name='Jockey', address='Test', age=30, rating=5)
        
        response = self.client.get(reverse('add_result'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(reverse('add_result'), {
            'competition': competition.id,
            'horse': horse.id,
            'jockey': jockey.id,
            'position': 1,
            'time_result': '02:30.500'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Result.objects.filter(competition=competition, position=1).exists())


class TestHippodromeViews(TestCase):
    """Интеграционные тесты для views ипподромов"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
    
    def test_hippodrome_list_requires_login(self):
        """Тест что список ипподромов требует авторизации"""
        response = self.client.get(reverse('hippodrome_list'))
        self.assertEqual(response.status_code, 302)
    
    def test_hippodrome_list_authenticated(self):
        """Тест списка ипподромов для авторизованного пользователя"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        self.client.force_login(user)
        
        Hippodrome.objects.create(name='Hippodrome1', address='Test')
        Hippodrome.objects.create(name='Hippodrome2', address='Test')
        
        response = self.client.get(reverse('hippodrome_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['hippodromes']), 2)
    
    def test_add_hippodrome_requires_admin(self):
        """Тест что добавление ипподрома требует прав администратора"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        self.client.force_login(user)
        
        response = self.client.get(reverse('add_hippodrome'))
        self.assertEqual(response.status_code, 302)
    
    def test_add_hippodrome_as_admin(self):
        """Тест добавления ипподрома администратором"""
        user = User.objects.create_user(username='admin', password='test123')
        UserProfile.objects.create(user=user, role='admin')
        self.client.force_login(user)
        
        response = self.client.get(reverse('add_hippodrome'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(reverse('add_hippodrome'), {
            'name': 'Новый ипподром',
            'address': 'Москва',
            'capacity': 15000,
            'is_active': True
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Hippodrome.objects.filter(name='Новый ипподром').exists())
    
    def test_edit_hippodrome_requires_admin(self):
        """Тест что редактирование ипподрома требует прав администратора"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        self.client.force_login(user)
        
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        response = self.client.get(reverse('edit_hippodrome', args=[hippodrome.id]))
        self.assertEqual(response.status_code, 302)
    
    def test_edit_hippodrome_as_admin(self):
        """Тест редактирования ипподрома администратором"""
        user = User.objects.create_user(username='admin', password='test123')
        UserProfile.objects.create(user=user, role='admin')
        self.client.force_login(user)
        
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        
        response = self.client.get(reverse('edit_hippodrome', args=[hippodrome.id]))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(reverse('edit_hippodrome', args=[hippodrome.id]), {
            'name': 'Обновленный ипподром',
            'address': 'Новый адрес',
            'capacity': 20000,
            'is_active': True
        })
        self.assertEqual(response.status_code, 302)
        hippodrome.refresh_from_db()
        self.assertEqual(hippodrome.name, 'Обновленный ипподром')


class TestAuthenticationViews(TestCase):
    """Интеграционные тесты для views аутентификации"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
    
    def test_register_view_get(self):
        """Тест GET запроса страницы регистрации"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
    
    def test_register_view_post(self):
        """Тест POST запроса регистрации"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'email': 'ivan@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'phone': '+79991234567',
            'address': 'Москва'
        })
        self.assertEqual(response.status_code, 302)  # Редирект после успешной регистрации
        self.assertTrue(User.objects.filter(username='newuser').exists())
        user = User.objects.get(username='newuser')
        self.assertTrue(UserProfile.objects.filter(user=user, role='user').exists())
    
    def test_login_view_get(self):
        """Тест GET запроса страницы входа"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_view_post_success(self):
        """Тест успешного входа"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        
        response = self.client.post(reverse('login'), {
            'username': 'user',
            'password': 'test123'
        })
        self.assertEqual(response.status_code, 302)  # Редирект после успешного входа
    
    def test_login_view_post_failure(self):
        """Тест неуспешного входа"""
        User.objects.create_user(username='user', password='test123')
        
        response = self.client.post(reverse('login'), {
            'username': 'user',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Остается на странице входа
    
    def test_logout_view(self):
        """Тест выхода"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        self.client.force_login(user)
        
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Редирект после выхода
    
    def test_profile_view_requires_login(self):
        """Тест что профиль требует авторизации"""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
    
    def test_profile_view_authenticated(self):
        """Тест профиля для авторизованного пользователя"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        self.client.force_login(user)
        
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user_profile'].user, user)
    
    def test_profile_view_creates_profile(self):
        """Тест создания профиля при просмотре"""
        user = User.objects.create_user(username='user', password='test123')
        # Профиль не создан
        self.client.force_login(user)
        
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
