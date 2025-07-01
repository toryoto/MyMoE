from django.urls import path
from .views import department_pie_chart

app_name = 'stats'

urlpatterns = [
    path('department/', department_pie_chart, name='department_pie'),
]