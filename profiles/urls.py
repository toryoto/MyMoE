from django.urls import path
from .views import EmployeeProfileCreateView, EmployeeProfileDetailView, EmployeeProfileUpdateView
from django.conf import settings


urlpatterns = [
    path('create/', EmployeeProfileCreateView.as_view(), name='profile_create'),
    path('detail/', EmployeeProfileDetailView.as_view(), name='profile_detail'),
    path('edit/', EmployeeProfileUpdateView.as_view(), name='profile_edit'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.conf import settings
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
