from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    """
    Employee model の管理画面設定
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    # UserAdmin のフィールドセットを継承
    fieldsets = UserAdmin.fieldsets
