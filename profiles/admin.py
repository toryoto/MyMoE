from django.contrib import admin
from .models import EmployeeProfile, Skill

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    """
    EmployeeProfile model の管理画面設定（拡張版）
    """
    list_display = (
        'enterprise_id', 'name', 'department', 'dte', 'mail_address',
        'ml', 'birth_day', 'is_manager', 'is_hr'
    )
    list_filter = ('department', 'is_manager', 'is_hr', 'ml')
    search_fields = (
        'enterprise_id', 'name', 'department', 'dte',
        'mail_address', 'statement_id'
    )
    ordering = ('enterprise_id',)
    filter_horizontal = ('skills',)

    fieldsets = (
        ('基本情報', {
            'fields': ('user', 'enterprise_id', 'name', 'department', 'dte', 'statement_id')
        }),
        ('連絡・日付情報', {
            'fields': ('mail_address', 'phone_number', 'birth_day', 'ml', 'date_of_birth')
        }),
        ('権限', {
            'fields': ('is_manager', 'is_hr')
        }),
        ('プロフィール詳細', {
            'fields': ('bio',)
        }),
        ('スキル', {
            'fields': ('skills',)
        }),
    )

    readonly_fields = ('user',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # 編集時はuserのみ読み取り専用
            return self.readonly_fields + ('enterprise_id',)
        return self.readonly_fields
