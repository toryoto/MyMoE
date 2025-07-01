from django.contrib import admin
from .models import EmployeeProfile, Skill, PreEmploymentHistory

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    """
    EmployeeProfile model の管理画面設定
    """
    list_display = ('user', 'phone_number', 'date_of_birth')
    list_filter = ('date_of_birth',)
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    ordering = ('user__username',)
    filter_horizontal = ('skills',)
    
    fieldsets = (
        ('基本情報', {
            'fields': ('user',)
        }),
        ('個人情報', {
            'fields': ('phone_number', 'date_of_birth', 'bio', 'photo')
        }),
        ('スキル', {
            'fields': ('skills',)
        }),
    )
    
    # 読み取り専用フィールド
    readonly_fields = ('user',)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # 編集時
            return self.readonly_fields + ('user',)
        return self.readonly_fields

@admin.register(PreEmploymentHistory)
class PreEmploymentHistoryAdmin(admin.ModelAdmin):
    """
    PreEmploymentHistory model の管理画面設定
    """
    list_display = ('employee_profile', 'company_name', 'job_title', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date', 'company_name')
    search_fields = ('employee_profile__user__username', 'company_name', 'job_title', 'job_role')
    ordering = ('-end_date', 'employee_profile__user__username')
    date_hierarchy = 'end_date'
    
    fieldsets = (
        ('従業員情報', {
            'fields': ('employee_profile',)
        }),
        ('会社情報', {
            'fields': ('company_name', 'job_title', 'job_role')
        }),
        ('期間', {
            'fields': ('start_date', 'end_date')
        }),
        ('詳細', {
            'fields': ('job_description',),
            'classes': ('collapse',)
        }),
    )
    
    # 従業員でグループ化して表示
    list_per_page = 25
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee_profile__user')
