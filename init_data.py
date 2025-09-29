#!/usr/bin/env python
"""
Скрипт для инициализации базы данных с тестовыми данными
"""

import os
import sys
import django
from datetime import datetime, date, time, timedelta

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'racing_club.settings')
django.setup()

from racing.models import Hippodrome, Owner, Jockey, Horse, Competition, Result


def create_test_data():
    """Создание тестовых данных"""
    
    # Создание ипподромов
    hippodromes_data = [
        {
            'name': 'Центральный ипподром Москвы',
            'address': 'Москва, ул. Беговая, 22',
            'capacity': 15000,
            'description': 'Главный ипподром столицы России',
            'is_active': True
        },
        {
            'name': 'Ипподром Санкт-Петербурга',
            'address': 'Санкт-Петербург, ул. Конюшенная, 1',
            'capacity': 12000,
            'description': 'Исторический ипподром Северной столицы',
            'is_active': True
        },
        {
            'name': 'Казанский ипподром',
            'address': 'Казань, ул. Ипподромная, 5',
            'capacity': 8000,
            'description': 'Современный ипподром в столице Татарстана',
            'is_active': True
        },
    ]
    
    hippodromes = []
    for hippodrome_data in hippodromes_data:
        hippodrome, created = Hippodrome.objects.get_or_create(
            name=hippodrome_data['name'],
            defaults=hippodrome_data
        )
        hippodromes.append(hippodrome)
        if created:
            print(f"Создан ипподром: {hippodrome.name}")
    
    # Создание владельцев
    owners_data = [
        {'name': 'Иван Петров', 'address': 'Москва, ул. Ленина, 1', 'phone': '+74951234567'},
        {'name': 'Мария Сидорова', 'address': 'Санкт-Петербург, Невский пр., 10', 'phone': '+78122345678'},
        {'name': 'Алексей Козлов', 'address': 'Казань, ул. Баумана, 5', 'phone': '+78433456789'},
    ]
    
    owners = []
    for owner_data in owners_data:
        owner, created = Owner.objects.get_or_create(
            name=owner_data['name'],
            defaults=owner_data
        )
        owners.append(owner)
        if created:
            print(f"Создан владелец: {owner.name}")
    
    # Создание жокеев
    jockeys_data = [
        {'name': 'Дмитрий Волков', 'address': 'Москва, ул. Тверская, 15', 'age': 28, 'rating': 9},
        {'name': 'Анна Морозова', 'address': 'Санкт-Петербург, ул. Марата, 20', 'age': 25, 'rating': 8},
        {'name': 'Сергей Лебедев', 'address': 'Казань, ул. Кремлевская, 8', 'age': 32, 'rating': 7},
        {'name': 'Елена Соколова', 'address': 'Москва, ул. Арбат, 12', 'age': 29, 'rating': 9},
    ]
    
    jockeys = []
    for jockey_data in jockeys_data:
        jockey, created = Jockey.objects.get_or_create(
            name=jockey_data['name'],
            defaults=jockey_data
        )
        jockeys.append(jockey)
        if created:
            print(f"Создан жокей: {jockey.name}")
    
    # Создание лошадей
    horses_data = [
        {'name': 'Молния', 'gender': 'F', 'age': 5, 'owner': owners[0]},
        {'name': 'Гром', 'gender': 'M', 'age': 6, 'owner': owners[1]},
        {'name': 'Звезда', 'gender': 'F', 'age': 4, 'owner': owners[0]},
        {'name': 'Буран', 'gender': 'M', 'age': 7, 'owner': owners[2]},
        {'name': 'Ветер', 'gender': 'M', 'age': 5, 'owner': owners[1]},
        {'name': 'Роза', 'gender': 'F', 'age': 6, 'owner': owners[2]},
    ]
    
    horses = []
    for horse_data in horses_data:
        horse, created = Horse.objects.get_or_create(
            name=horse_data['name'],
            defaults=horse_data
        )
        horses.append(horse)
        if created:
            print(f"Создана лошадь: {horse.name}")
    
    # Создание состязаний
    competitions_data = [
        {
            'date': date(2024, 1, 15),
            'time': time(14, 0),
            'hippodrome': hippodromes[0],
            'name': 'Кубок Москвы'
        },
        {
            'date': date(2024, 1, 22),
            'time': time(15, 30),
            'hippodrome': hippodromes[1],
            'name': 'Зимние скачки'
        },
        {
            'date': date(2024, 2, 5),
            'time': time(13, 0),
            'hippodrome': hippodromes[2],
            'name': 'Состязание на приз Татарстана'
        },
    ]
    
    competitions = []
    for comp_data in competitions_data:
        competition, created = Competition.objects.get_or_create(
            date=comp_data['date'],
            time=comp_data['time'],
            defaults=comp_data
        )
        competitions.append(competition)
        if created:
            print(f"Создано состязание: {competition.name}")
    
    # Создание результатов
    results_data = [
        # Кубок Москвы
        {'competition': competitions[0], 'horse': horses[0], 'jockey': jockeys[0], 'position': 1, 'time_result': timedelta(minutes=1, seconds=23, milliseconds=456)},
        {'competition': competitions[0], 'horse': horses[1], 'jockey': jockeys[1], 'position': 2, 'time_result': timedelta(minutes=1, seconds=24, milliseconds=123)},
        {'competition': competitions[0], 'horse': horses[2], 'jockey': jockeys[2], 'position': 3, 'time_result': timedelta(minutes=1, seconds=25, milliseconds=789)},
        
        # Зимние скачки
        {'competition': competitions[1], 'horse': horses[3], 'jockey': jockeys[3], 'position': 1, 'time_result': timedelta(minutes=1, seconds=22, milliseconds=234)},
        {'competition': competitions[1], 'horse': horses[4], 'jockey': jockeys[0], 'position': 2, 'time_result': timedelta(minutes=1, seconds=23, milliseconds=567)},
        {'competition': competitions[1], 'horse': horses[5], 'jockey': jockeys[1], 'position': 3, 'time_result': timedelta(minutes=1, seconds=24, milliseconds=890)},
        
        # Состязание на приз Татарстана
        {'competition': competitions[2], 'horse': horses[0], 'jockey': jockeys[2], 'position': 1, 'time_result': timedelta(minutes=1, seconds=21, milliseconds=123)},
        {'competition': competitions[2], 'horse': horses[3], 'jockey': jockeys[3], 'position': 2, 'time_result': timedelta(minutes=1, seconds=22, milliseconds=456)},
        {'competition': competitions[2], 'horse': horses[1], 'jockey': jockeys[0], 'position': 3, 'time_result': timedelta(minutes=1, seconds=23, milliseconds=789)},
    ]
    
    for result_data in results_data:
        result, created = Result.objects.get_or_create(
            competition=result_data['competition'],
            position=result_data['position'],
            defaults=result_data
        )
        if created:
            print(f"Создан результат: {result.competition.name} - {result.horse.name} ({result.position} место)")
    
    print("\nТестовые данные успешно созданы!")
    print(f"Ипподромов: {Hippodrome.objects.count()}")
    print(f"Владельцев: {Owner.objects.count()}")
    print(f"Жокеев: {Jockey.objects.count()}")
    print(f"Лошадей: {Horse.objects.count()}")
    print(f"Состязаний: {Competition.objects.count()}")
    print(f"Результатов: {Result.objects.count()}")


if __name__ == '__main__':
    create_test_data()
