from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee
from departments.models import DTE

@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    """
    Employee model の管理画面設定
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', 'department', 'dte', 'is_hr')
    list_filter = ('is_staff', 'is_active', 'date_joined', 'department', 'dte', 'is_hr')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Organization Info', {'fields': ('department', 'dte', 'is_hr')}),
    )

    class Media:
        js = (
            'admin/js/jquery.init.js',
            'admin/js/employee_dte_filter.js',
        )

    
