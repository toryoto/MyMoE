from django.urls import path
from .views import EmployeeProfileCreateView, MyProfileDetailView, EmployeeProfileDetailView, EmployeeProfileUpdateView

urlpatterns = [
    path('create/', EmployeeProfileCreateView.as_view(), name='profile_create'),
    path('my_profile/', MyProfileDetailView.as_view(), name='my_profile_detail'), # ログインユーザーのプロフィール詳細
    path('detail/<int:pk>/', EmployeeProfileDetailView.as_view(), name='profile_detail'), # 他の社員のプロフィール詳細
    path('edit/', EmployeeProfileUpdateView.as_view(), name='profile_edit'),
]
