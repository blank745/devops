from .models import UserProfile, Jockey


def user_profile_context(request):
    """Контекстный процессор для добавления профиля пользователя в контекст"""
    context = {}
    if request.user.is_authenticated:
        try:
            context['user_profile'] = request.user.userprofile
        except UserProfile.DoesNotExist:
            # Создаем профиль пользователя с ролью по умолчанию для отображения в навигации
            context['user_profile'] = UserProfile.objects.create(
                user=request.user,
                role='user'
            )
        
        # Если пользователь имеет роль жокея, создаем профиль жокея если его нет
        if context['user_profile'].is_jockey() and not context['user_profile'].jockey:
            jockey = Jockey.objects.create(
                name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                address=context['user_profile'].address or "Не указан",
                age=25,  # Возраст по умолчанию
                rating=5  # Рейтинг по умолчанию
            )
            context['user_profile'].jockey = jockey
            context['user_profile'].save()
    
    return context
