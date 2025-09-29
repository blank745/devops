from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Hippodrome, Owner, Jockey, Horse, Competition, Result, UserProfile
from .forms import HippodromeForm, OwnerForm, JockeyForm, HorseForm, CompetitionForm, ResultForm, UserRegistrationForm
from .decorators import admin_required, jockey_or_admin_required, user_required


def create_jockey_profile_for_user(user_profile):
    """Создает профиль жокея для пользователя-жокея"""
    if user_profile.is_jockey() and not user_profile.jockey:
        # Создаем профиль жокея с базовой информацией
        jockey = Jockey.objects.create(
            name=f"{user_profile.user.first_name} {user_profile.user.last_name}".strip() or user_profile.user.username,
            address=user_profile.address or "Не указан",
            age=25,  # Возраст по умолчанию
            rating=5  # Рейтинг по умолчанию
        )
        user_profile.jockey = jockey
        user_profile.save()
        return jockey
    return None


def index(request):
    """Главная страница"""
    recent_competitions = Competition.objects.all()[:5]
    total_horses = Horse.objects.count()
    total_jockeys = Jockey.objects.count()
    total_competitions = Competition.objects.count()
    
    context = {
        'recent_competitions': recent_competitions,
        'total_horses': total_horses,
        'total_jockeys': total_jockeys,
        'total_competitions': total_competitions,
    }
    return render(request, 'racing/index.html', context)


def competition_detail(request, competition_id):
    """Детали состязания с результатами"""
    competition = get_object_or_404(Competition, id=competition_id)
    results = Result.objects.filter(competition=competition).order_by('position')
    
    context = {
        'competition': competition,
        'results': results,
    }
    return render(request, 'racing/competition_detail.html', context)


@jockey_or_admin_required
def add_competition(request):
    """Добавление нового состязания"""
    if request.method == 'POST':
        form = CompetitionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Состязание успешно добавлено!')
            return redirect('competition_list')
    else:
        form = CompetitionForm()
    
    return render(request, 'racing/add_competition.html', {'form': form})


@admin_required
def add_jockey(request):
    """Добавление нового жокея"""
    if request.method == 'POST':
        form = JockeyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Жокей успешно добавлен!')
            return redirect('jockey_list')
    else:
        form = JockeyForm()
    
    return render(request, 'racing/add_jockey.html', {'form': form})


@jockey_or_admin_required
def add_horse(request):
    """Добавление новой лошади"""
    if request.method == 'POST':
        form = HorseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Лошадь успешно добавлена!')
            return redirect('horse_list')
    else:
        form = HorseForm()
    
    return render(request, 'racing/add_horse.html', {'form': form})


@jockey_or_admin_required
def add_result(request):
    """Добавление результата состязания"""
    if request.method == 'POST':
        form = ResultForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Результат успешно добавлен!')
            return redirect('competition_list')
    else:
        form = ResultForm()
    
    return render(request, 'racing/add_result.html', {'form': form})


def jockey_competitions(request, jockey_id):
    """Список состязаний жокея"""
    jockey = get_object_or_404(Jockey, id=jockey_id)
    results = Result.objects.filter(jockey=jockey).order_by('-competition__date', '-competition__time')
    
    context = {
        'jockey': jockey,
        'results': results,
    }
    return render(request, 'racing/jockey_competitions.html', context)


def horse_competitions(request, horse_id):
    """Список состязаний лошади"""
    horse = get_object_or_404(Horse, id=horse_id)
    results = Result.objects.filter(horse=horse).order_by('-competition__date', '-competition__time')
    
    context = {
        'horse': horse,
        'results': results,
    }
    return render(request, 'racing/horse_competitions.html', context)


@user_required
def competition_list(request):
    """Список всех состязаний"""
    competitions = Competition.objects.all()
    context = {'competitions': competitions}
    return render(request, 'racing/competition_list.html', context)


@user_required
def jockey_list(request):
    """Список всех жокеев"""
    # Получаем пользователей-жокеев (только с существующими жокеями)
    user_jockeys = UserProfile.objects.filter(role='jockey', jockey__isnull=False)
    
    # Получаем ID жокеев, которые уже связаны с пользователями
    user_jockey_ids = [up.jockey.id for up in user_jockeys]
    
    # Получаем обычных жокеев (исключая тех, что связаны с пользователями)
    regular_jockeys = Jockey.objects.exclude(id__in=user_jockey_ids)
    
    # Создаем список всех жокеев для отображения
    all_jockeys = []
    
    # Добавляем обычных жокеев
    for jockey in regular_jockeys:
        all_jockeys.append({
            'jockey': jockey,
            'is_user_jockey': False,
            'user_profile': None
        })
    
    # Добавляем пользователей-жокеев (только если жокей существует)
    for user_profile in user_jockeys:
        if user_profile.jockey:  # Проверяем, что жокей не был удален
            all_jockeys.append({
                'jockey': user_profile.jockey,
                'is_user_jockey': True,
                'user_profile': user_profile
            })
    
    context = {'all_jockeys': all_jockeys}
    return render(request, 'racing/jockey_list.html', context)


@user_required
def horse_list(request):
    """Список всех лошадей"""
    horses = Horse.objects.all()
    context = {'horses': horses}
    return render(request, 'racing/horse_list.html', context)


def add_owner(request):
    """Добавление нового владельца"""
    if request.method == 'POST':
        form = OwnerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Владелец успешно добавлен!')
            return redirect('add_horse')
    else:
        form = OwnerForm()
    
    return render(request, 'racing/add_owner.html', {'form': form})


@user_required
def hippodrome_list(request):
    """Список всех ипподромов"""
    hippodromes = Hippodrome.objects.all()
    context = {'hippodromes': hippodromes}
    return render(request, 'racing/hippodrome_list.html', context)


@admin_required
def add_hippodrome(request):
    """Добавление нового ипподрома"""
    if request.method == 'POST':
        form = HippodromeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ипподром успешно добавлен!')
            return redirect('hippodrome_list')
    else:
        form = HippodromeForm()
    
    return render(request, 'racing/add_hippodrome.html', {'form': form})


@admin_required
def edit_hippodrome(request, hippodrome_id):
    """Редактирование ипподрома"""
    hippodrome = get_object_or_404(Hippodrome, id=hippodrome_id)
    
    if request.method == 'POST':
        form = HippodromeForm(request.POST, instance=hippodrome)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ипподром успешно обновлен!')
            return redirect('hippodrome_list')
    else:
        form = HippodromeForm(instance=hippodrome)
    
    return render(request, 'racing/edit_hippodrome.html', {'form': form, 'hippodrome': hippodrome})


def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('index')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'racing/register.html', {'form': form})


def user_login(request):
    """Вход пользователя"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        from django.contrib.auth import authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.first_name}!')
            return redirect('index')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    
    return render(request, 'racing/login.html')


@login_required
def user_logout(request):
    """Выход пользователя"""
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы.')
    return redirect('index')


@login_required
def profile(request):
    """Профиль пользователя"""
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        # Создаем профиль пользователя с ролью по умолчанию
        user_profile = UserProfile.objects.create(
            user=request.user,
            role='user'
        )
        # Не показываем уведомление при просмотре профиля
    
    context = {'user_profile': user_profile}
    return render(request, 'racing/profile.html', context)
