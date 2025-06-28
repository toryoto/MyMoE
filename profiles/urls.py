from django.urls import path
from .views import (
    EmployeeProfileCreateView, MyProfileDetailView, EmployeeProfileUpdateView, EmployeeProfileDetailView, UpdateEmployeeOrgInfoView, GetDTEsForDepartmentView
)

app_name = 'profiles'

urlpatterns = [
    path('my-profile/', MyProfileDetailView.as_view(), name='my_profile_detail'),
    path('my-profile/update/', EmployeeProfileUpdateView.as_view(), name='my_profile_update'),
    path('create/', EmployeeProfileCreateView.as_view(), name='profile_create'),
    path('<int:pk>/', EmployeeProfileDetailView.as_view(), name='employee_profile_detail'),
    path('update-org-info/<int:pk>/', UpdateEmployeeOrgInfoView.as_view(), name='update_org_info'),
    path('get-dtes/<int:department_id>/', GetDTEsForDepartmentView.as_view(), name='get_dtes_for_department'),
]
