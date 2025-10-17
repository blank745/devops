from django.contrib import admin
from .models import UserProfile, Hippodrome, Owner, Jockey, Horse, Competition, Result


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'has_jockey_profile')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'jockey__name')
    list_filter = ('role',)
    fields = ('user', 'role', 'phone', 'address', 'jockey')
    readonly_fields = ('jockey',)
    
    def has_jockey_profile(self, obj):
        """Показывает, есть ли у пользователя профиль жокея"""
        if obj.jockey:
            return f"Да ({obj.jockey.name})"
        return "Нет"
    has_jockey_profile.short_description = "Профиль жокея"
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.role != 'jockey':
            return self.readonly_fields + ('jockey',)
        return self.readonly_fields
    
    def save_model(self, request, obj, form, change):
        """Автоматически создает профиль жокея при смене роли на 'jockey'"""
        if obj.role == 'jockey' and not obj.jockey:
            # Создаем профиль жокея
            from .models import Jockey
            jockey = Jockey.objects.create(
                name=f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username,
                address=obj.address or "Не указан",
                age=25,  # Возраст по умолчанию
                rating=5  # Рейтинг по умолчанию
            )
            obj.jockey = jockey
        super().save_model(request, obj, form, change)


@admin.register(Hippodrome)
class HippodromeAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'capacity', 'is_active')
    search_fields = ('name', 'address')
    list_filter = ('is_active',)


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'address')
    search_fields = ('name', 'phone')


@admin.register(Jockey)
class JockeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'rating', 'address')
    search_fields = ('name',)
    list_filter = ('rating', 'age')


@admin.register(Horse)
class HorseAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'age', 'owner')
    search_fields = ('name', 'owner__name')
    list_filter = ('gender', 'age', 'owner')


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'time', 'hippodrome')
    search_fields = ('name', 'hippodrome__name')
    list_filter = ('date', 'hippodrome')
    date_hierarchy = 'date'


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('competition', 'horse', 'jockey', 'position', 'time_result')
    search_fields = ('horse__name', 'jockey__name', 'competition__name')
    list_filter = ('competition', 'position')
    raw_id_fields = ('competition', 'horse', 'jockey')


