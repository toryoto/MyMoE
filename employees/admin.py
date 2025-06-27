from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee
from departments.models import DTE

@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    """
    Employee model の管理画面設定
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', 'department', 'dte')
    list_filter = ('is_staff', 'is_active', 'date_joined', 'department', 'dte')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Organization Info', {'fields': ('department', 'dte')}),
    )

    class Media:
        js = (
            'admin/js/jquery.init.js',
            'admin/js/employee_dte_filter.js',
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "dte":
            # Initially, show no DTEs or only DTEs related to the currently selected department if editing an existing employee
            if request.resolver_match.kwargs.get('object_id'): # Editing existing object
                employee = Employee.objects.get(pk=request.resolver_match.kwargs['object_id'])
                if employee.department:
                    kwargs["queryset"] = DTE.objects.filter(department=employee.department)
                else:
                    kwargs["queryset"] = DTE.objects.none()
            else: # Adding new object
                kwargs["queryset"] = DTE.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
