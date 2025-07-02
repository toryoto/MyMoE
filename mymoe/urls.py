from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from employees.views import mymoe_home
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.forms import AuthenticationForm

def index(request):
    if request.user.is_authenticated:
        return redirect('mymoe_home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if getattr(user, 'force_password_change', False):
                return redirect('employees:force_password_change')
            return redirect('mymoe_home')
    else:
        form = AuthenticationForm()

    return render(request, 'index.html', {'form': form})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('employees/', include(('employees.urls', 'employees'), namespace='employees')),
    path('profiles/', include(('profiles.urls', 'profiles'), namespace='profiles')),
    path('departments/', include('departments.urls')),
    path('assignments/', include(('assignments.urls', 'assignments'), namespace='assignments')),
    path('mymoe/', mymoe_home, name='mymoe_home'),
    path('', index, name='home'),
    path('hr/', include(('employees.urls', 'employees'), namespace='hr')),
    path('stats/', include('stats.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)