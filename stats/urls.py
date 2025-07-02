from django.urls import path
from . import views

app_name = 'stats'

urlpatterns = [
    path('data/', views.department_pie_chart, name='department_pie_chart'),
]