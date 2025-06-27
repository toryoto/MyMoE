from django.urls import path
from . import views

app_name = 'departments'

urlpatterns = [
    path('', views.DepartmentListView.as_view(), name='department_list'),
    path('<int:pk>/', views.DepartmentDetailView.as_view(), name='department_detail'),
    path('add/', views.DepartmentCreateView.as_view(), name='department_add'),
    path('<int:pk>/edit/', views.DepartmentUpdateView.as_view(), name='department_edit'),
    path('<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),
    path('dtes/', views.DTEListView.as_view(), name='dte_list'),
    path('dtes/<int:pk>/', views.DTEDetailView.as_view(), name='dte_detail'),
    path('dtes/add/', views.DTECreateView.as_view(), name='dte_add'),
    path('dtes/<int:pk>/edit/', views.DTEUpdateView.as_view(), name='dte_edit'),
    path('dtes/<int:pk>/delete/', views.DTEDeleteView.as_view(), name='dte_delete'),
]