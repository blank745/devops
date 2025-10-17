from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models
from .models import Hippodrome, Owner, Jockey, Horse, Competition, Result, UserProfile


class HippodromeForm(forms.ModelForm):
    class Meta:
        model = Hippodrome
        fields = ['name', 'address', 'capacity', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class OwnerForm(forms.ModelForm):
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            import re
            # Паттерн для российского номера телефона
            # Поддерживает форматы: +7XXXXXXXXXX, 8XXXXXXXXXX, +7 (XXX) XXX-XX-XX, 8 (XXX) XXX-XX-XX
            russian_phone_pattern = r'^(\+7|8)[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
            
            # Убираем все пробелы, дефисы и скобки для проверки
            clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
            
            # Проверяем, что номер начинается с +7 или 8 и имеет правильную длину
            if not re.match(r'^(\+7|8)[0-9]{10}$', clean_phone):
                raise forms.ValidationError(
                    'Введите корректный российский номер телефона. '
                    'Форматы: +7XXXXXXXXXX, 8XXXXXXXXXX, +7 (XXX) XXX-XX-XX, 8 (XXX) XXX-XX-XX'
                )
            
            # Нормализуем номер к формату +7XXXXXXXXXX
            if clean_phone.startswith('8'):
                clean_phone = '+7' + clean_phone[1:]
            elif not clean_phone.startswith('+7'):
                clean_phone = '+7' + clean_phone
            
            return clean_phone
        return phone
    
    class Meta:
        model = Owner
        fields = ['name', 'address', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (XXX) XXX-XX-XX'}),
        }


class JockeyForm(forms.ModelForm):
    class Meta:
        model = Jockey
        fields = ['name', 'address', 'age', 'rating']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
        }


class HorseForm(forms.ModelForm):
    class Meta:
        model = Horse
        fields = ['name', 'gender', 'age', 'owner']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'owner': forms.Select(attrs={'class': 'form-control'}),
        }


class CompetitionForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        
        if date and time:
            from datetime import datetime, date as date_class
            from django.utils import timezone
            
            # Создаем datetime объект из даты и времени
            competition_datetime = datetime.combine(date, time)
            
            # Проверяем, что состязание не в будущем (не позже сегодняшней даты)
            if competition_datetime > timezone.now().replace(tzinfo=None):
                raise forms.ValidationError(
                    'Состязание не может быть запланировано в будущем. '
                    'Пожалуйста, выберите дату и время не позже сегодняшней.'
                )
            
            # Проверяем, что состязание не слишком далеко в прошлом (не более 10 лет)
            from datetime import timedelta
            min_past_date = timezone.now().replace(tzinfo=None) - timedelta(days=3650)  # 10 лет
            if competition_datetime < min_past_date:
                raise forms.ValidationError(
                    'Состязание не может быть запланировано более чем 10 лет назад.'
                )
        
        return cleaned_data
    
    class Meta:
        model = Competition
        fields = ['date', 'time', 'hippodrome', 'name']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hippodrome': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ResultForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Показываем только жокеев, которые не связаны с удаленными пользователями
        # или связаны с активными пользователями-жокеями
        self.fields['jockey'].queryset = Jockey.objects.filter(
            models.Q(userprofile__isnull=True) | 
            models.Q(userprofile__isnull=False, userprofile__role='jockey')
        )
    
    def clean(self):
        cleaned_data = super().clean()
        competition = cleaned_data.get('competition')
        horse = cleaned_data.get('horse')
        position = cleaned_data.get('position')
        
        if competition:
            from datetime import datetime
            from django.utils import timezone
            
            # Создаем datetime объект из даты и времени соревнования
            competition_datetime = datetime.combine(competition.date, competition.time)
            
            # Проверяем, что соревнование не в будущем (более чем на 1 год)
            from datetime import timedelta
            max_future_date = timezone.now().replace(tzinfo=None) + timedelta(days=365)
            if competition_datetime > max_future_date:
                raise forms.ValidationError(
                    'Нельзя добавлять результаты для соревнований, запланированных более чем на год вперед.'
                )
            
            # Проверяем, что соревнование не слишком далеко в прошлом (более 10 лет)
            min_past_date = timezone.now().replace(tzinfo=None) - timedelta(days=3650)
            if competition_datetime < min_past_date:
                raise forms.ValidationError(
                    'Нельзя добавлять результаты для соревнований, которые прошли более 10 лет назад.'
                )
        
        # Проверяем дублирование лошади в соревновании
        if competition and horse:
            existing_horse_result = Result.objects.filter(
                competition=competition, 
                horse=horse
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing_horse_result.exists():
                raise forms.ValidationError(
                    f'Лошадь "{horse.name}" уже участвует в этом соревновании.'
                )
        
        # Проверяем дублирование места в соревновании
        if competition and position:
            existing_position_result = Result.objects.filter(
                competition=competition, 
                position=position
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing_position_result.exists():
                raise forms.ValidationError(
                    f'Место {position} уже занято в этом соревновании.'
                )
        
        # Общая логическая проверка: время для позиции должно согласовываться с соседями
        time_result = cleaned_data.get('time_result')
        if competition and position and time_result is not None:
            # Есть ли вообще другие результаты? Если нет — проверку не выполняем
            any_other = Result.objects.filter(competition=competition).exclude(
                pk=self.instance.pk if self.instance else None
            ).exists()
            if any_other:
                # Унифицированно преобразуем введённое значение к timedelta
                from datetime import timedelta
                from django.utils.dateparse import parse_duration
                import re

                def to_timedelta(value):
                    if isinstance(value, timedelta):
                        return value
                    if isinstance(value, str):
                        std = parse_duration(value)
                        if std is not None:
                            return std
                        m = re.match(r'^(?:(?P<h>\d{1,2}):)?(?P<m>\d{1,2}):(?P<s>\d{1,2})(?:[\.,](?P<ms>\d{1,6}))?$', value.strip())
                        if not m:
                            return None
                        hours = int(m.group('h') or 0)
                        minutes = int(m.group('m'))
                        seconds = int(m.group('s'))
                        frac = m.group('ms') or '0'
                        if len(frac) > 6:
                            frac = frac[:6]
                        microseconds = int(frac.ljust(6, '0'))
                        return timedelta(hours=hours, minutes=minutes, seconds=seconds, microseconds=microseconds)
                    return None

                parsed_time = to_timedelta(time_result)
                if parsed_time is None:
                    raise forms.ValidationError('Некорректный формат времени. Используйте MM:SS.mmm')
                cleaned_data['time_result'] = parsed_time

                # Ищем ближайшего соседа с меньшей позицией
                lower_neighbor = Result.objects.filter(
                    competition=competition,
                    position__lt=position
                ).order_by('-position').first()

                # Ищем ближайшего соседа с большей позицией
                upper_neighbor = Result.objects.filter(
                    competition=competition,
                    position__gt=position
                ).order_by('position').first()

                # Проверяем нижнюю границу (не лучше чем сосед с лучшей позицией)
                if lower_neighbor and parsed_time < lower_neighbor.time_result:
                    raise forms.ValidationError(
                        f'Время для места {position} не может быть меньше времени для места {lower_neighbor.position}.'
                    )

                # Проверяем верхнюю границу (не хуже чем сосед с худшей позицией)
                if upper_neighbor and parsed_time > upper_neighbor.time_result:
                    raise forms.ValidationError(
                        f'Время для места {position} не может быть больше времени для места {upper_neighbor.position}.'
                    )
        
        return cleaned_data
    
    class Meta:
        model = Result
        fields = ['competition', 'horse', 'jockey', 'position', 'time_result']
        widgets = {
            'competition': forms.Select(attrs={'class': 'form-control'}),
            'horse': forms.Select(attrs={'class': 'form-control'}),
            'jockey': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'time_result': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM:SS.mmm'}),
        }


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (XXX) XXX-XX-XX'}))
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            import re
            # Убираем все пробелы, дефисы и скобки для проверки
            clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
            
            # Проверяем, что номер начинается с +7 или 8 и имеет правильную длину
            if not re.match(r'^(\+7|8)[0-9]{10}$', clean_phone):
                raise forms.ValidationError(
                    'Введите корректный российский номер телефона. '
                    'Форматы: +7XXXXXXXXXX, 8XXXXXXXXXX, +7 (XXX) XXX-XX-XX, 8 (XXX) XXX-XX-XX'
                )
            
            # Нормализуем номер к формату +7XXXXXXXXXX
            if clean_phone.startswith('8'):
                clean_phone = '+7' + clean_phone[1:]
            elif not clean_phone.startswith('+7'):
                clean_phone = '+7' + clean_phone
            
            return clean_phone
        return phone

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'phone', 'address')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Все новые пользователи автоматически получают роль "Пользователь"
            user_profile = UserProfile.objects.create(
                user=user,
                role='user',  # Фиксированная роль "Пользователь"
                phone=self.cleaned_data['phone'],
                address=self.cleaned_data['address']
            )
        return user
