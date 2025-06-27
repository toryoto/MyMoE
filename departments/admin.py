from django.contrib import admin
from .models import Department, DTE

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    search_fields = ('name', 'code')

@admin.register(DTE)
class DTEAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'department', 'is_active')
    list_filter = ('department', 'is_active')
    search_fields = ('name', 'code')