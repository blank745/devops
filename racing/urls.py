from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('competitions/', views.competition_list, name='competition_list'),
    path('competitions/<int:competition_id>/', views.competition_detail, name='competition_detail'),
    path('competitions/add/', views.add_competition, name='add_competition'),
    path('jockeys/', views.jockey_list, name='jockey_list'),
    path('jockeys/add/', views.add_jockey, name='add_jockey'),
    path('jockeys/<int:jockey_id>/competitions/', views.jockey_competitions, name='jockey_competitions'),
    path('horses/', views.horse_list, name='horse_list'),
    path('horses/add/', views.add_horse, name='add_horse'),
    path('horses/<int:horse_id>/competitions/', views.horse_competitions, name='horse_competitions'),
    path('results/add/', views.add_result, name='add_result'),
    path('owners/add/', views.add_owner, name='add_owner'),
    path('hippodromes/', views.hippodrome_list, name='hippodrome_list'),
    path('hippodromes/add/', views.add_hippodrome, name='add_hippodrome'),
    path('hippodromes/<int:hippodrome_id>/edit/', views.edit_hippodrome, name='edit_hippodrome'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
]
