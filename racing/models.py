from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('jockey', 'Жокей'),
        ('admin', 'Администратор'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user', verbose_name="Роль")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")
    address = models.TextField(blank=True, null=True, verbose_name="Адрес")
    jockey = models.OneToOneField('Jockey', on_delete=models.CASCADE, blank=True, null=True, verbose_name="Профиль жокея")
    
    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
    
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
    """
    def is_admin(self):
        return self.role == 'admin'
    
    def is_jockey(self):
        return self.role == 'jockey'
    
    def is_user(self):
        return self.role == 'user'

    def get_jockey_name(self):
        if self.is_jockey() and self.jockey:
            return self.jockey.name
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
    
    def get_jockey_rating(self):
        if self.is_jockey() and self.jockey:
            return self.jockey.rating
        return None
    
    def get_jockey_age(self):
        if self.is_jockey() and self.jockey:
            return self.jockey.age
        return None
    """

class Hippodrome(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название ипподрома")
    address = models.TextField(verbose_name="Адрес")
    capacity = models.PositiveIntegerField(verbose_name="Вместимость", null=True, blank=True)
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Ипподром"
        verbose_name_plural = "Ипподромы"
        ordering = ['name']

    def __str__(self):
        return self.name


class Owner(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    address = models.TextField(verbose_name="Адрес")
    phone = models.CharField(max_length=20, verbose_name="Телефон")

    class Meta:
        verbose_name = "Владелец"
        verbose_name_plural = "Владельцы"

    def __str__(self):
        return self.name


class Jockey(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    address = models.TextField(verbose_name="Адрес")
    age = models.PositiveIntegerField(verbose_name="Возраст")
    rating = models.PositiveIntegerField(
        verbose_name="Рейтинг",
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    class Meta:
        verbose_name = "Жокей"
        verbose_name_plural = "Жокеи"

    def __str__(self):
        return self.name


class Horse(models.Model):
    GENDER_CHOICES = [
        ('M', 'Жеребец'),
        ('F', 'Кобыла'),
    ]

    name = models.CharField(max_length=100, verbose_name="Кличка")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Пол")
    age = models.PositiveIntegerField(verbose_name="Возраст")
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, verbose_name="Владелец")

    class Meta:
        verbose_name = "Лошадь"
        verbose_name_plural = "Лошади"

    def __str__(self):
        return self.name


class Competition(models.Model):
    date = models.DateField(verbose_name="Дата")
    time = models.TimeField(verbose_name="Время")
    hippodrome = models.ForeignKey(Hippodrome, on_delete=models.CASCADE, verbose_name="Ипподром")
    name = models.CharField(max_length=200, blank=True, null=True, verbose_name="Название состязания")

    class Meta:
        verbose_name = "Состязание"
        verbose_name_plural = "Состязания"
        ordering = ['-date', '-time']

    def __str__(self):
        if self.name:
            return f"{self.name} - {self.hippodrome.name} ({self.date})"
        return f"Состязание - {self.hippodrome.name} ({self.date})"


class Result(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, verbose_name="Состязание")
    horse = models.ForeignKey(Horse, on_delete=models.CASCADE, verbose_name="Лошадь")
    jockey = models.ForeignKey(Jockey, on_delete=models.CASCADE, verbose_name="Жокей")
    position = models.PositiveIntegerField(verbose_name="Занятое место")
    time_result = models.DurationField(verbose_name="Показанное время")

    class Meta:
        verbose_name = "Результат"
        verbose_name_plural = "Результаты"
        unique_together = ['competition', 'position']  # Одно место в состязании может занять только одна лошадь

    def __str__(self):
        return f"{self.competition} - {self.horse} ({self.position} место)"
    
    def get_formatted_time(self):
        """Возвращает время в формате MM:SS.mmm"""
        if not self.time_result:
            return "00:00.000"
        
        total_seconds = int(self.time_result.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        milliseconds = int(self.time_result.microseconds / 1000)
        
        return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


@receiver(post_delete, sender=UserProfile)
def delete_user_jockey(sender, instance, **kwargs):
    """
    Сигнал для удаления жокея при удалении профиля пользователя с ролью 'jockey'
    """
    if instance.role == 'jockey' and instance.jockey:
        # Удаляем связанного жокея
        jockey = instance.jockey
        jockey.delete()
