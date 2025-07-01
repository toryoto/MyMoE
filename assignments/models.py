from django.db import models
from employees.models import Employee

class Client(models.Model):
    """クライアント"""
    INDUSTRY_CHOICES = [
        ('finance', '金融'),
        ('retail', '小売'),
        ('telecommunications', '通信'),
        ('automotive', '自動車'),
        ('other', 'その他'),
    ]

    name = models.CharField(max_length=100, unique=True)
    industry = models.CharField(max_length=20, choices=INDUSTRY_CHOICES, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "クライアント"
        verbose_name_plural = "クライアント"

    def __str__(self):
        return self.name


class Project(models.Model):
    """プロジェクト"""
    STATUS_CHOICES = [
        ('active', '進行中'),
        ('completed', '完了'),
    ]

    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='projects')
    name = models.CharField(max_length=100)
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, null=True, related_name='managed_projects', verbose_name='プロジェクト責任者')
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    class Meta:
        verbose_name = "プロジェクト"
        verbose_name_plural = "プロジェクト"

    def __str__(self):
        return f"{self.client.name} - {self.name}"


class Assignment(models.Model):
    """アサイン"""
    ROLE_CHOICES = [
        ('pm', 'プロジェクトマネージャー'),
        ('leader', 'リーダー'),
        ('member', 'メンバー'),
        ('support', 'サポート'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='assignments')
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='assignments')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = "アサイン"
        verbose_name_plural = "アサイン"

    def __str__(self):
        return f"{self.employee.username} → {self.project.name} ({self.get_role_display()})"