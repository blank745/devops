"""
Integration тесты для views приложения racing
"""
import pytest
from datetime import date, time, timedelta
from django.contrib.auth.models import User
from django.urls import reverse
from racing.models import (
    UserProfile, Hippodrome, Owner, Jockey, Horse, Competition, Result
)


@pytest.mark.integration
class TestIndexView:
    """Интеграционные тесты для главной страницы"""
    
    def test_index_view_anonymous(self, client):
        """Тест главной страницы для анонимного пользователя"""
        response = client.get(reverse('index'))
        assert response.status_code == 200
        assert 'recent_competitions' in response.context
    
    def test_index_view_authenticated(self, client, db):
        """Тест главной страницы для авторизованного пользователя"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        client.force_login(user)
        
        response = client.get(reverse('index'))
        assert response.status_code == 200


@pytest.mark.integration
class TestCompetitionViews:
    """Интеграционные тесты для views состязаний"""
    
    def test_competition_list_requires_login(self, client, db):
        """Тест что список состязаний требует авторизации"""
        response = client.get(reverse('competition_list'))
        assert response.status_code == 302  # Редирект на логин
    
    def test_competition_list_authenticated(self, client, db):
        """Тест списка состязаний для авторизованного пользователя"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        client.force_login(user)
        
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        Competition.objects.create(
            hippodrome=hippodrome,
            date=date.today(),
            time=time(14, 0)
        )
        
        response = client.get(reverse('competition_list'))
        assert response.status_code == 200
        assert len(response.context['competitions']) == 1
    
    def test_competition_detail(self, client, db):
        """Тест детальной страницы состязания"""
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        competition = Competition.objects.create(
            hippodrome=hippodrome,
            date=date.today(),
            time=time(14, 0)
        )
        
        response = client.get(reverse('competition_detail', args=[competition.id]))
        assert response.status_code == 200
        assert response.context['competition'] == competition
    
    def test_add_competition_requires_jockey_or_admin(self, client, db):
        """Тест что добавление состязания требует прав жокея или админа"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        client.force_login(user)
        
        response = client.get(reverse('add_competition'))
        assert response.status_code == 302  # Редирект из-за недостатка прав
    
    def test_add_competition_as_admin(self, client, db):
        """Тест добавления состязания администратором"""
        user = User.objects.create_user(username='admin', password='test123')
        UserProfile.objects.create(user=user, role='admin')
        client.force_login(user)
        
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        
        response = client.get(reverse('add_competition'))
        assert response.status_code == 200
        
        # POST запрос
        past_date = date.today() - timedelta(days=1)
        response = client.post(reverse('add_competition'), {
            'date': past_date,
            'time': '14:00',
            'hippodrome': hippodrome.id,
            'name': 'Новое состязание'
        })
        assert response.status_code == 302  # Редирект после успешного создания
        assert Competition.objects.filter(name='Новое состязание').exists()


@pytest.mark.integration
class TestJockeyViews:
    """Интеграционные тесты для views жокеев"""
    
    def test_jockey_list_requires_login(self, client, db):
        """Тест что список жокеев требует авторизации"""
        response = client.get(reverse('jockey_list'))
        assert response.status_code == 302
    
    def test_jockey_list_authenticated(self, client, db):
        """Тест списка жокеев для авторизованного пользователя"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        client.force_login(user)
        
        Jockey.objects.create(name='Jockey1', address='Test', age=30, rating=5)
        Jockey.objects.create(name='Jockey2', address='Test', age=35, rating=7)
        
        response = client.get(reverse('jockey_list'))
        assert response.status_code == 200
        assert len(response.context['all_jockeys']) == 2
    
    def test_add_jockey_requires_admin(self, client, db):
        """Тест что добавление жокея требует прав администратора"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        client.force_login(user)
        
        response = client.get(reverse('add_jockey'))
        assert response.status_code == 302
    
    def test_add_jockey_as_admin(self, client, db):
        """Тест добавления жокея администратором"""
        user = User.objects.create_user(username='admin', password='test123')
        UserProfile.objects.create(user=user, role='admin')
        client.force_login(user)
        
        response = client.get(reverse('add_jockey'))
        assert response.status_code == 200
        
        response = client.post(reverse('add_jockey'), {
            'name': 'Новый жокей',
            'address': 'Москва',
            'age': 30,
            'rating': 8
        })
        assert response.status_code == 302
        assert Jockey.objects.filter(name='Новый жокей').exists()
    
    def test_jockey_competitions(self, client, db):
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
        
        response = client.get(reverse('jockey_competitions', args=[jockey.id]))
        assert response.status_code == 200
        assert len(response.context['results']) == 1


@pytest.mark.integration
class TestHorseViews:
    """Интеграционные тесты для views лошадей"""
    
    def test_horse_list_requires_login(self, client, db):
        """Тест что список лошадей требует авторизации"""
        response = client.get(reverse('horse_list'))
        assert response.status_code == 302
    
    def test_horse_list_authenticated(self, client, db):
        """Тест списка лошадей для авторизованного пользователя"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        client.force_login(user)
        
        owner = Owner.objects.create(name='Owner', address='Test', phone='+79991234567')
        Horse.objects.create(name='Horse1', gender='M', age=5, owner=owner)
        Horse.objects.create(name='Horse2', gender='F', age=6, owner=owner)
        
        response = client.get(reverse('horse_list'))
        assert response.status_code == 200
        assert len(response.context['horses']) == 2
    
    def test_add_horse_requires_jockey_or_admin(self, client, db):
        """Тест что добавление лошади требует прав жокея или админа"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        client.force_login(user)
        
        response = client.get(reverse('add_horse'))
        assert response.status_code == 302
    
    def test_add_horse_as_jockey(self, client, db):
        """Тест добавления лошади жокеем"""
        user = User.objects.create_user(username='jockey', password='test123')
        jockey = Jockey.objects.create(name='Jockey', address='Test', age=30, rating=5)
        UserProfile.objects.create(user=user, role='jockey', jockey=jockey)
        client.force_login(user)
        
        owner = Owner.objects.create(name='Owner', address='Test', phone='+79991234567')
        
        response = client.get(reverse('add_horse'))
        assert response.status_code == 200
        
        response = client.post(reverse('add_horse'), {
            'name': 'Новая лошадь',
            'gender': 'M',
            'age': 5,
            'owner': owner.id
        })
        assert response.status_code == 302
        assert Horse.objects.filter(name='Новая лошадь').exists()
    
    def test_horse_competitions(self, client, db):
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
        
        response = client.get(reverse('horse_competitions', args=[horse.id]))
        assert response.status_code == 200
        assert len(response.context['results']) == 1


@pytest.mark.integration
class TestResultViews:
    """Интеграционные тесты для views результатов"""
    
    def test_add_result_requires_jockey_or_admin(self, client, db):
        """Тест что добавление результата требует прав жокея или админа"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        client.force_login(user)
        
        response = client.get(reverse('add_result'))
        assert response.status_code == 302
    
    def test_add_result_as_admin(self, client, db):
        """Тест добавления результата администратором"""
        user = User.objects.create_user(username='admin', password='test123')
        UserProfile.objects.create(user=user, role='admin')
        client.force_login(user)
        
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        competition = Competition.objects.create(
            hippodrome=hippodrome,
            date=date.today() - timedelta(days=1),
            time=time(14, 0)
        )
        owner = Owner.objects.create(name='Owner', address='Test', phone='+79991234567')
        horse = Horse.objects.create(name='Horse', gender='M', age=5, owner=owner)
        jockey = Jockey.objects.create(name='Jockey', address='Test', age=30, rating=5)
        
        response = client.get(reverse('add_result'))
        assert response.status_code == 200
        
        response = client.post(reverse('add_result'), {
            'competition': competition.id,
            'horse': horse.id,
            'jockey': jockey.id,
            'position': 1,
            'time_result': '02:30.500'
        })
        assert response.status_code == 302
        assert Result.objects.filter(competition=competition, position=1).exists()


@pytest.mark.integration
class TestHippodromeViews:
    """Интеграционные тесты для views ипподромов"""
    
    def test_hippodrome_list_requires_login(self, client, db):
        """Тест что список ипподромов требует авторизации"""
        response = client.get(reverse('hippodrome_list'))
        assert response.status_code == 302
    
    def test_hippodrome_list_authenticated(self, client, db):
        """Тест списка ипподромов для авторизованного пользователя"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        client.force_login(user)
        
        Hippodrome.objects.create(name='Hippodrome1', address='Test')
        Hippodrome.objects.create(name='Hippodrome2', address='Test')
        
        response = client.get(reverse('hippodrome_list'))
        assert response.status_code == 200
        assert len(response.context['hippodromes']) == 2
    
    def test_add_hippodrome_requires_admin(self, client, db):
        """Тест что добавление ипподрома требует прав администратора"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        client.force_login(user)
        
        response = client.get(reverse('add_hippodrome'))
        assert response.status_code == 302
    
    def test_add_hippodrome_as_admin(self, client, db):
        """Тест добавления ипподрома администратором"""
        user = User.objects.create_user(username='admin', password='test123')
        UserProfile.objects.create(user=user, role='admin')
        client.force_login(user)
        
        response = client.get(reverse('add_hippodrome'))
        assert response.status_code == 200
        
        response = client.post(reverse('add_hippodrome'), {
            'name': 'Новый ипподром',
            'address': 'Москва',
            'capacity': 15000,
            'is_active': True
        })
        assert response.status_code == 302
        assert Hippodrome.objects.filter(name='Новый ипподром').exists()
    
    def test_edit_hippodrome_requires_admin(self, client, db):
        """Тест что редактирование ипподрома требует прав администратора"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        client.force_login(user)
        
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        response = client.get(reverse('edit_hippodrome', args=[hippodrome.id]))
        assert response.status_code == 302
    
    def test_edit_hippodrome_as_admin(self, client, db):
        """Тест редактирования ипподрома администратором"""
        user = User.objects.create_user(username='admin', password='test123')
        UserProfile.objects.create(user=user, role='admin')
        client.force_login(user)
        
        hippodrome = Hippodrome.objects.create(name='Test', address='Test')
        
        response = client.get(reverse('edit_hippodrome', args=[hippodrome.id]))
        assert response.status_code == 200
        
        response = client.post(reverse('edit_hippodrome', args=[hippodrome.id]), {
            'name': 'Обновленный ипподром',
            'address': 'Новый адрес',
            'capacity': 20000,
            'is_active': True
        })
        assert response.status_code == 302
        hippodrome.refresh_from_db()
        assert hippodrome.name == 'Обновленный ипподром'


@pytest.mark.integration
class TestAuthenticationViews:
    """Интеграционные тесты для views аутентификации"""
    
    def test_register_view_get(self, client):
        """Тест GET запроса страницы регистрации"""
        response = client.get(reverse('register'))
        assert response.status_code == 200
    
    def test_register_view_post(self, client, db):
        """Тест POST запроса регистрации"""
        response = client.post(reverse('register'), {
            'username': 'newuser',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'email': 'ivan@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'phone': '+79991234567',
            'address': 'Москва'
        })
        assert response.status_code == 302  # Редирект после успешной регистрации
        assert User.objects.filter(username='newuser').exists()
        user = User.objects.get(username='newuser')
        assert UserProfile.objects.filter(user=user, role='user').exists()
    
    def test_login_view_get(self, client):
        """Тест GET запроса страницы входа"""
        response = client.get(reverse('login'))
        assert response.status_code == 200
    
    def test_login_view_post_success(self, client, db):
        """Тест успешного входа"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        
        response = client.post(reverse('login'), {
            'username': 'user',
            'password': 'test123'
        })
        assert response.status_code == 302  # Редирект после успешного входа
    
    def test_login_view_post_failure(self, client, db):
        """Тест неуспешного входа"""
        User.objects.create_user(username='user', password='test123')
        
        response = client.post(reverse('login'), {
            'username': 'user',
            'password': 'wrongpassword'
        })
        assert response.status_code == 200  # Остается на странице входа
    
    def test_logout_view(self, client, db):
        """Тест выхода"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        client.force_login(user)
        
        response = client.get(reverse('logout'))
        assert response.status_code == 302  # Редирект после выхода
    
    def test_profile_view_requires_login(self, client):
        """Тест что профиль требует авторизации"""
        response = client.get(reverse('profile'))
        assert response.status_code == 302
    
    def test_profile_view_authenticated(self, client, db):
        """Тест профиля для авторизованного пользователя"""
        user = User.objects.create_user(username='user', password='test123')
        UserProfile.objects.create(user=user, role='user')
        client.force_login(user)
        
        response = client.get(reverse('profile'))
        assert response.status_code == 200
        assert response.context['user_profile'].user == user
    
    def test_profile_view_creates_profile(self, client, db):
        """Тест создания профиля при просмотре"""
        user = User.objects.create_user(username='user', password='test123')
        # Профиль не создан
        client.force_login(user)
        
        response = client.get(reverse('profile'))
        assert response.status_code == 200
        assert UserProfile.objects.filter(user=user).exists()

