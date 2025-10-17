from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile


def role_required(allowed_roles):
    """
    Декоратор для проверки роли пользователя
    allowed_roles: список разрешенных ролей ['admin', 'jockey', 'user']
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            try:
                user_profile = request.user.userprofile
            except UserProfile.DoesNotExist:
                # Создаем профиль пользователя с ролью по умолчанию только для просмотра
                if allowed_roles == ['user', 'jockey', 'admin']:  # Только для @user_required
                    user_profile = UserProfile.objects.create(
                        user=request.user,
                        role='user'
                    )
                else:
                    # Для других ролей показываем ошибку
                    messages.error(request, 'Профиль пользователя не найден. Обратитесь к администратору.')
                    return redirect('index')
            
            if user_profile.role not in allowed_roles:
                messages.error(request, f'У вас нет прав для доступа к этой странице. Требуется роль: {", ".join(allowed_roles)}, у вас: {user_profile.get_role_display()}')
                return redirect('index')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """Декоратор для проверки прав администратора"""
    return role_required(['admin'])(view_func)


def jockey_or_admin_required(view_func):
    """Декоратор для проверки прав жокея или администратора"""
    return role_required(['jockey', 'admin'])(view_func)


def user_required(view_func):
    """Декоратор для проверки прав пользователя (все роли)"""
    return role_required(['user', 'jockey', 'admin'])(view_func)