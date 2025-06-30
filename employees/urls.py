from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('force-password-change/',views.ForcePasswordChangeView.as_view(), name='force_password_change'),
    # 社員一覧
    path('list/', views.EmployeeListView.as_view(), name='employee_list'),
    # CSV登録関連
    path('csv-import/', views.CSVBulkImportView.as_view(), name='csv_bulk_import'),
    path('csv-preview/', views.CSVPreviewView.as_view(), name='csv_preview'),
    path('csv-result/', views.CSVResultView.as_view(), name='csv_result'),
    path('download-sample-csv/', views.download_sample_csv, name='download_sample_csv'),
]
