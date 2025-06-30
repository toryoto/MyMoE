from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from employees.views import mymoe_home
from departments.views import dtes_by_department
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import messages

def index(request):
    if request.user.is_authenticated:
        return redirect('mymoe_home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # 初回ログインチェック
            if getattr(user, 'force_password_change', False):
                return redirect('employees:force_password_change')
            return redirect('mymoe_home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'index.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('employees/', include(('employees.urls', 'employees'), namespace='employees')),
    path('profiles/', include(('profiles.urls', 'profiles'), namespace='profiles')),
    path('mymoe/', mymoe_home, name='mymoe_home'),
    path('departments/', include('departments.urls')),
    path('api/departments/<int:department_id>/dtes/', dtes_by_department, name='dtes_by_department'),
    path('', index, name='home'),
    path('hr/', include(('employees.urls', 'employees'), namespace='hr')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)