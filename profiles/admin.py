from django.contrib import admin
from .models import EmployeeProfile

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    """
    EmployeeProfile model の管理画面設定
    """
    list_display = ('user', 'phone_number', 'date_of_birth')
    list_filter = ('date_of_birth',)
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    ordering = ('user__username',)
    
    fieldsets = (
        ('基本情報', {
            'fields': ('user',)
        }),
        ('個人情報', {
            'fields': ('phone_number', 'date_of_birth', 'bio')
        }),
    )
    
    # 読み取り専用フィールド
    readonly_fields = ('user',)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # 編集時
            return self.readonly_fields + ('user',)
        return self.readonly_fields
