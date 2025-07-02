from django.contrib import admin
from .models import Client, Project, Assignment

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'is_active')
    list_filter = ('industry', 'is_active')
    search_fields = ('name',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'manager', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'client', 'manager')
    search_fields = ('name', 'client__name', 'manager__username')
    raw_id_fields = ('manager',)

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'project', 'role', 'start_date', 'end_date')
    list_filter = ('role', 'project__client', 'start_date')
    search_fields = ('employee__username', 'project__name')
    raw_id_fields = ('employee', 'project')