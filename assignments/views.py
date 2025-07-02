from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from .models import Client, Project, Assignment
from django.db import models
from employees.models import Employee


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """管理者権限が必要なビューのMixin"""
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_hr


class ProjectManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """プロジェクトマネージャー権限が必要なビューのMixin"""
    def test_func(self):
        # 管理者または該当プロジェクトのマネージャーかチェック
        if self.request.user.is_staff or self.request.user.is_hr:
            return True
        
        project_pk = self.kwargs.get('pk')
        if hasattr(self, 'get_object'):
            # Assignment削除の場合はassignmentからprojectを取得
            obj = self.get_object()
            if hasattr(obj, 'project'):
                return obj.project.manager == self.request.user
            # Project関連の場合
            elif hasattr(obj, 'manager'):
                return obj.manager == self.request.user
        
        # URLからproject_pkを取得してチェック
        if project_pk:
            try:
                project = Project.objects.get(pk=project_pk)
                return project.manager == self.request.user
            except Project.DoesNotExist:
                return False
        
        return False


class EmployeeSearchAPIView(LoginRequiredMixin, View):
    """社員検索API"""
    def get(self, request):
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:
            return JsonResponse([])
        
        # プロジェクトIDがクエリパラメータにある場合は取得
        project_id = request.GET.get('project_id')
        assigned_employee_ids = []
        
        if project_id:
            try:
                project = Project.objects.get(pk=project_id)
                assigned_employee_ids = list(
                    project.assignments.values_list('employee_id', flat=True)
                )
            except Project.DoesNotExist:
                pass
        
        # 社員を検索（名前、ユーザー名、メールで検索）
        employees = Employee.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(username__icontains=query) |
            Q(email__icontains=query),
            is_active=True
        ).select_related('department')[:10]
        
        results = []
        for employee in employees:
            name = employee.get_full_name() or employee.username
            results.append({
                'id': employee.id,
                'name': name,
                'username': employee.username,
                'email': employee.email,
                'department': employee.department.name if employee.department else None,
                'already_assigned': employee.id in assigned_employee_ids
            })
        
        return JsonResponse(results, safe=False)


class ProjectListView(LoginRequiredMixin, ListView):
    """プロジェクト一覧ビュー"""
    model = Project
    template_name = 'assignments/project_list.html'
    context_object_name = 'projects'
    paginate_by = 10

    def get_queryset(self):
        queryset = Project.objects.select_related('client', 'manager').prefetch_related('assignments')
        
        # 検索機能
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(client__name__icontains=search_query)
            )
        
        # クライアントフィルター
        client_id = self.request.GET.get('client')
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        
        # ステータスフィルター
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clients'] = Client.objects.filter(is_active=True)
        context['status_choices'] = Project.STATUS_CHOICES
        context['current_search'] = self.request.GET.get('search', '')
        context['current_client'] = self.request.GET.get('client', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['active_projects_count'] = Project.objects.filter(status='active').count()
        context['total_projects_count'] = Project.objects.count()
        return context


class ProjectDetailView(LoginRequiredMixin, DetailView):
    """プロジェクト詳細ビュー"""
    model = Project
    template_name = 'assignments/project_detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignments'] = self.object.assignments.select_related('employee').order_by('-start_date')
        context['available_employees'] = Employee.objects.filter(is_active=True).order_by('username')
        context['role_choices'] = Assignment.ROLE_CHOICES
        context['today'] = timezone.now().date()
        
        # ユーザーがこのプロジェクトのマネージャーまたは管理者かチェック
        user = self.request.user
        can_manage = False
        
        if user.is_authenticated:
            if user.is_superuser:
                can_manage = True
            elif self.object.manager and self.object.manager.pk == user.pk:
                can_manage = True
        
        context['can_manage_assignments'] = can_manage
        
        return context


class ProjectCreateView(AdminRequiredMixin, CreateView):
    """プロジェクト作成ビュー"""
    model = Project
    template_name = 'assignments/project_form.html'
    fields = ['client', 'name', 'manager', 'start_date', 'end_date', 'status']

    def get_success_url(self):
        return reverse_lazy('assignments:project_detail', kwargs={'pk': self.object.pk})


class ProjectUpdateView(AdminRequiredMixin, UpdateView):
    """プロジェクト更新ビュー"""
    model = Project
    template_name = 'assignments/project_form.html'
    fields = ['client', 'name', 'manager', 'start_date', 'end_date', 'status']

    def get_success_url(self):
        return reverse_lazy('assignments:project_detail', kwargs={'pk': self.object.pk})


class AssignmentCreateView(ProjectManagerRequiredMixin, View):
    """アサイン作成ビュー（プロジェクトマネージャーのみ）"""
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        
        employee_id = request.POST.get('employee_id')
        role = request.POST.get('role', 'member')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date') or None
        
        try:
            employee = Employee.objects.get(pk=employee_id)
            
            # 既にアサインされているかチェック
            existing_assignment = Assignment.objects.filter(
                project=project,
                employee=employee
            ).first()
            
            if existing_assignment:
                return JsonResponse({'error': '既にアサインされています'}, status=400)
            
            # アサインを作成
            Assignment.objects.create(
                project=project,
                employee=employee,
                role=role,
                start_date=start_date,
                end_date=end_date
            )
            
            return JsonResponse({'success': True})
            
        except Employee.DoesNotExist:
            return JsonResponse({'error': '社員が見つかりません'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class AssignmentDeleteView(ProjectManagerRequiredMixin, View):
    """アサイン削除ビュー（プロジェクトマネージャーのみ）"""
    def post(self, request, pk):
        assignment = get_object_or_404(Assignment, pk=pk)
        assignment.delete()
        return JsonResponse({'success': True})

    def get_object(self):
        return get_object_or_404(Assignment, pk=self.kwargs['pk'])


class ClientListView(LoginRequiredMixin, ListView):
    """クライアント一覧ビュー（参照のみ）"""
    model = Client
    template_name = 'assignments/client_list.html'
    context_object_name = 'clients'
    paginate_by = 10

    def get_queryset(self):
        queryset = Client.objects.annotate(project_count=Count('projects'))
        
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        
        industry = self.request.GET.get('industry')
        if industry:
            queryset = queryset.filter(industry=industry)
        
        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['industry_choices'] = Client.INDUSTRY_CHOICES
        context['current_search'] = self.request.GET.get('search', '')
        context['current_industry'] = self.request.GET.get('industry', '')
        return context


class ClientDetailView(LoginRequiredMixin, DetailView):
    """クライアント詳細ビュー（参照のみ）"""
    model = Client
    template_name = 'assignments/client_detail.html'
    context_object_name = 'client'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = self.object.projects.select_related('manager').order_by('-start_date')
        return context


class MyAssignmentListView(LoginRequiredMixin, ListView):
    """自分のアサイン一覧ビュー"""
    model = Assignment
    template_name = 'assignments/my_assignment_list.html'
    context_object_name = 'assignments'
    paginate_by = 10

    def get_queryset(self):
        return Assignment.objects.filter(
            employee=self.request.user
        ).select_related('project__client', 'project__manager').order_by('-start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 全てのアサインメントを取得
        all_assignments = self.get_queryset()
        
        # 現在進行中のプロジェクト数（プロジェクトのステータスがactiveで、アサインが終了していない）
        context['active_assignments'] = all_assignments.filter(
            project__status='active'
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gt=timezone.now().date())
        ).count()
        
        # 完了済みプロジェクト数
        context['completed_assignments'] = all_assignments.filter(
            project__status='completed'
        ).count()
        
        # 総プロジェクト数
        context['total_assignments'] = all_assignments.count()
        
        return context