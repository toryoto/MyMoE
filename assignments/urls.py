from django.urls import path
from . import views

app_name = 'assignments'

urlpatterns = [
    # プロジェクト管理のメイン画面
    path('', views.ProjectListView.as_view(), name='project_list'),
    
    # プロジェクト詳細とアサイン管理
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/assign/', views.AssignmentCreateView.as_view(), name='assignment_create'),
    path('assignments/<int:pk>/delete/', views.AssignmentDeleteView.as_view(), name='assignment_delete'),
    
    # 社員検索API
    path('api/employee-search/', views.EmployeeSearchAPIView.as_view(), name='employee_search'),
    
    # クライアント一覧（参照のみ）
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    
    # 自分のアサイン一覧
    path('my-assignments/', views.MyAssignmentListView.as_view(), name='my_assignment_list'),
    
    # プロジェクト作成・編集（管理者のみ）
    path('projects/create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_update'),
]