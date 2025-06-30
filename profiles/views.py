from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import EmployeeProfile, Skill, PreEmploymentHistory
from .forms import EmployeeProfileForm, PreEmploymentHistoryFormSet, PreEmploymentHistoryForm
from django.http import JsonResponse,HttpResponseForbidden
from django.views import View
from employees.models import Employee
from departments.models import Department, DTE
import json
from django.template.loader import render_to_string

class SkillSearchView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        skills = Skill.objects.filter(name__icontains=query)[:10] # 最大10件返す
        results = list(skills.values('id', 'name'))
        print(results)
        return JsonResponse(results, safe=False)

class EmployeeProfileCreateView(LoginRequiredMixin, CreateView):
    model = EmployeeProfile
    form_class = EmployeeProfileForm
    template_name = 'profiles/employee_profile_form.html'
    success_url = reverse_lazy('profiles:my_profile_detail')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['initial_skill_ids'] = []
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class MyProfileDetailView(LoginRequiredMixin, DetailView):
    model = EmployeeProfile
    template_name = 'profiles/employee_profile_detail.html'
    context_object_name = 'profile'

    def dispatch(self, request, *args, **kwargs):
        # プロフィールが存在しない場合は作成ページにリダイレクト
        profile, created = EmployeeProfile.objects.get_or_create(user=request.user)
        if created:
            return redirect('profiles:my_profile_update')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(EmployeeProfile, user=self.request.user)

class EmployeeProfileDetailView(LoginRequiredMixin, DetailView):
    model = EmployeeProfile
    template_name = 'profiles/employee_profile_detail.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return get_object_or_404(EmployeeProfile, pk=self.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_hr:
            context['departments'] = Department.objects.filter(is_active=True)
        return context

class EmployeeProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = EmployeeProfile
    form_class = EmployeeProfileForm
    template_name = 'profiles/employee_profile_form.html'
    success_url = reverse_lazy('profiles:my_profile_detail')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # テンプレートに渡すために、現在のスキルIDのリストを作成
        context['initial_skill_ids'] = list(self.object.skills.values_list('id', flat=True))
        context['history_formset'] = PreEmploymentHistoryFormSet(instance=self.object)

        return context

    def dispatch(self, request, *args, **kwargs):
        # プロフィールが存在しない場合は作成(employees/signals.pyで自動作成されているが、念の為)
        profile, created = EmployeeProfile.objects.get_or_create(user=request.user)
        if created:
            # 新規作成の場合は、オブジェクトをセットしてからUpdateViewの処理を継続
            self.kwargs['pk'] = profile.pk
        
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        # URLのpkではなく、常にログインユーザーのプロフィールを返す
        return get_object_or_404(EmployeeProfile, user=self.request.user)

    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user

class UpdateEmployeeOrgInfoView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not request.user.is_hr:
            return JsonResponse({'status': 'error', 'message': 'Permission denied.'}, status=403)

        try:
            employee = get_object_or_404(Employee, pk=pk)
            data = json.loads(request.body)
            department_id = data.get('department_id')
            dte_id = data.get('dte_id')

            department = get_object_or_404(Department, id=department_id) if department_id else None
            dte = get_object_or_404(DTE, id=dte_id) if dte_id else None

            employee.department = department
            employee.dte = dte
            employee.clean()
            employee.save()

            html = render_to_string('components/user_org_info.html', {'employee': employee})

            return JsonResponse({'status': 'success', 'message': 'Organization info updated.', 'html': html})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

class GetDTEsForDepartmentView(LoginRequiredMixin, View):
    def get(self, request, department_id):
        dtes = DTE.objects.filter(department_id=department_id, is_active=True).values('id', 'name')
        return JsonResponse(list(dtes), safe=False)


class PreEmploymentHistoryCreateView(LoginRequiredMixin, CreateView):
    model = PreEmploymentHistory
    form_class = PreEmploymentHistoryForm
    template_name = 'profiles/pre_employment_history_form.html'
    success_url = reverse_lazy('profiles:my_profile_detail')

    def form_valid(self, form):
        form.instance.employee = get_object_or_404(EmployeeProfile, user=self.request.user)
        return super().form_valid(form)
    
class PreEmploymentHistoryUpdateView(LoginRequiredMixin, UpdateView):
    model = PreEmploymentHistory
    form_class = PreEmploymentHistoryForm
    template_name = 'profiles/pre_employment_history_form.html'
    success_url = reverse_lazy('profiles:my_profile_detail')

    def get_queryset(self):
        # 自分の経歴のみ編集可能にする
        return PreEmploymentHistory.objects.filter(employee__user=self.request.user)

class EmployeeProfileDeleteView(LoginRequiredMixin, DetailView):
    model = EmployeeProfile
    template_name = 'profiles/employee_profile_detail.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        profile = super().get_object(queryset)

        if profile.user == self.request.user:
            return profile
        if self.request.user.is_hr:
            return profile

        raise HttpResponseForbidden("You do not have permission to delete this profile.")

from .forms import EmployeeProfileForm, PreEmploymentHistoryFormSet

class EmployeeProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = EmployeeProfile
    form_class = EmployeeProfileForm
    template_name = 'profiles/employee_profile_form.html'
    success_url = reverse_lazy('profiles:my_profile_detail')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['history_formset'] = PreEmploymentHistoryFormSet(self.request.POST, instance=self.object)
        else:
            context['history_formset'] = PreEmploymentHistoryFormSet(instance=self.object)

        context['initial_skill_ids'] = list(self.object.skills.values_list('id', flat=True))
        return context

    def form_valid(self, form):
        history_formset = PreEmploymentHistoryFormSet(self.request.POST, instance=self.object)
        if history_formset.is_valid():
            self.object = form.save()
            history_formset.instance = self.object
            history_formset.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form, history_formset=history_formset))


    def get_object(self, queryset=None):
        return get_object_or_404(EmployeeProfile, user=self.request.user)

    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user

