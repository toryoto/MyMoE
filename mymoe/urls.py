from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect
from employees.views import mymoe_home
from departments.views import dtes_by_department
from django.conf import settings
from django.conf.urls.static import static

def index(request):
    if request.user.is_authenticated:
        return redirect('mymoe_home')
    return render(request, 'index.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('employees.urls')),
    path('profiles/', include('profiles.urls')),
    path('mymoe/', mymoe_home, name='mymoe_home'),
    path('departments/', include('departments.urls')),
    path('api/departments/<int:department_id>/dtes/', dtes_by_department, name='dtes_by_department'),
    path('', index, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
