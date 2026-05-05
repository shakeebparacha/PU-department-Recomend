from django.urls import path
from . import views

app_name = 'merit'

urlpatterns = [
    path('', views.home, name='home'),
    path('calculator/', views.merit_calculator, name='calculator'),
    path('program-finder/', views.program_finder, name='program_finder'),
    path('recommendations/', views.recommendations, name='recommendations'),
    path('debug-csv/', views.debug_csv_status, name='debug_csv_status'),
]
