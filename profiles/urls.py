from django.urls import path
from .views import EmployeeProfileCreateView, EmployeeProfileDetailView, EmployeeProfileUpdateView

urlpatterns = [
    path('create/', EmployeeProfileCreateView.as_view(), name='profile_create'),
    path('detail/', EmployeeProfileDetailView.as_view(), name='profile_detail'),
    path('edit/', EmployeeProfileUpdateView.as_view(), name='profile_edit'),
]
