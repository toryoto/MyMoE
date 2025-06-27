from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect
from employees.views import mymoe_home

def index(request):
    if request.user.is_authenticated:
        return redirect('mymoe_home')
    return render(request, 'index.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('employees.urls')),
    path('profiles/', include('profiles.urls')),
    path('mymoe/', mymoe_home, name='mymoe_home'),
    path('', index, name='home'),
]
