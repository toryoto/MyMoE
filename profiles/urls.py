from django.urls import path
from django.conf import settings

from profiles.views import (
    EmployeeProfileUpdateView, EmployeeProfileDetailView, 
    SkillSearchView, EmployeeProfilePDFView
)

app_name = 'profiles'

urlpatterns = [
    path('<int:pk>/', EmployeeProfileDetailView.as_view(), name='employee_profile_detail'),
    path('<int:pk>/edit/', EmployeeProfileUpdateView.as_view(), name='employee_profile_update'),
    
    # API エンドポイント
    path('api/skills/search/', SkillSearchView.as_view(), name='skill_search'),
    # path('update-org-info/<int:employee_id>/', UpdateEmployeeOrgInfoView.as_view(), name='update_employee_org_info'),
    
    # PDF Download
    path('<int:pk>/pdf/', EmployeeProfilePDFView.as_view(), name='profile_pdf'), 
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.conf import settings
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)