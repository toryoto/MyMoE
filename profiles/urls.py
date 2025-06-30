from django.urls import path
from django.conf import settings

from .views import (
    EmployeeProfileCreateView, MyProfileDetailView, EmployeeProfileUpdateView, EmployeeProfileDetailView, 
    SkillSearchView,
)

app_name = 'profiles'

urlpatterns = [
    path('my-profile/', MyProfileDetailView.as_view(), name='my_profile_detail'),
    path('my-profile/update/', EmployeeProfileUpdateView.as_view(), name='my_profile_update'),
    path('create/', EmployeeProfileCreateView.as_view(), name='profile_create'),
    path('<int:pk>/', EmployeeProfileDetailView.as_view(), name='employee_profile_detail'),
    path('api/skills/search/', SkillSearchView.as_view(), name='skill_search'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.conf import settings
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
