from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import EmployeeProfile, Skill
from .forms import EmployeeProfileForm, PreEmploymentHistoryFormSet
from django.http import JsonResponse, HttpResponse
from django.views import View
from employees.models import Employee
from departments.models import Department, DTE
import json
from django.template.loader import render_to_string
from django.contrib import messages
# pdf
from .utils.pdf_generator import generate_employee_profile_pdf

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
        if self.request.POST:
            context['history_formset'] = PreEmploymentHistoryFormSet(self.request.POST, self.request.FILES, prefix='history')
        else:
            context['history_formset'] = PreEmploymentHistoryFormSet(prefix='history')
        context['initial_skill_ids'] = []
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        self.object = form.save()
        history_formset = PreEmploymentHistoryFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix='history')
        if history_formset.is_valid():
            history_formset.instance = self.object
            history_formset.save()
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

class EmployeeProfileDetailView(LoginRequiredMixin, DetailView):
    model = EmployeeProfile
    template_name = 'profiles/employee_profile_detail.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        # 自分のプロフィールの場合は自動作成
        if pk == self.request.user.pk:
            profile, created = EmployeeProfile.objects.get_or_create(user=self.request.user)
            return profile
        return get_object_or_404(EmployeeProfile, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_hr:
            context['departments'] = Department.objects.filter(is_active=True)
            context['ML_CHOICES'] = Employee.ML_CHOICES
            # 現在の部署に属するDTEを取得
            if self.object.user.department:
                context['dtes'] = DTE.objects.filter(department=self.object.user.department, is_active=True)
            else:
                context['dtes'] = DTE.objects.none()
        return context

    def post(self, request, *args, **kwargs):
        """HR権限でのPOST処理（組織情報・ML更新）"""
        if not request.user.is_hr:
            messages.error(request, '権限がありません。')
            return redirect('profiles:employee_profile_detail', pk=kwargs['pk'])
        
        profile = self.get_object()
        employee = profile.user
        
        # 組織情報の更新
        if 'update_org' in request.POST:
            department_id = request.POST.get('department')
            dte_id = request.POST.get('dte')
            
            try:
                # 部署を更新
                if department_id:
                    department = get_object_or_404(Department, id=department_id)
                    employee.department = department
                else:
                    employee.department = None
                
                # DTEを更新
                if dte_id:
                    dte = get_object_or_404(DTE, id=dte_id)
                    # DTEが選択した部署に属しているかチェック
                    if employee.department and dte.department != employee.department:
                        messages.error(request, '選択したDTEは選択した部署に属していません。')
                        return redirect('profiles:employee_profile_detail', pk=kwargs['pk'])
                    employee.dte = dte
                else:
                    employee.dte = None
                
                employee.save()
                messages.success(request, '組織情報が更新されました。')
                
            except Exception as e:
                messages.error(request, f'更新に失敗しました: {str(e)}')
        
        # MLレベルの更新
        elif 'update_ml' in request.POST:
            ml_value = request.POST.get('ml')
            
            try:
                # ML_CHOICESから有効な選択肢のリストを作成
                valid_ml_choices = [choice[0] for choice in Employee.ML_CHOICES]
                
                if ml_value in valid_ml_choices:
                    employee.ml = ml_value
                    employee.save()
                    messages.success(request, 'MLレベルが更新されました。')
                else:
                    messages.error(request, '無効なMLレベルです。')
                    
            except Exception as e:
                messages.error(request, f'ML更新に失敗しました: {str(e)}')
        
        return redirect('profiles:employee_profile_detail', pk=kwargs['pk'])

class EmployeeProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = EmployeeProfile
    form_class = EmployeeProfileForm
    template_name = 'profiles/employee_profile_form.html'
    
    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        return get_object_or_404(EmployeeProfile, user_id=pk)
    
    def get_success_url(self):
        return reverse_lazy('profiles:employee_profile_detail', kwargs={'pk': self.object.user.pk})

    def test_func(self):
        # 自分のプロフィールのみ編集可能
        profile = self.get_object()
        return self.request.user == profile.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['history_formset'] = PreEmploymentHistoryFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix='history')
        else:
            context['history_formset'] = PreEmploymentHistoryFormSet(instance=self.object, prefix='history')
        context['initial_skill_ids'] = list(self.object.skills.values_list('id', flat=True))
        return context

    def form_valid(self, form):
        history_formset = PreEmploymentHistoryFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix='history')
        if form.is_valid() and history_formset.is_valid():
            self.object = form.save()
            history_formset.instance = self.object
            history_formset.save()
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

class GetDTEsForDepartmentView(LoginRequiredMixin, View):
    def get(self, request, department_id):
        dtes = DTE.objects.filter(department_id=department_id, is_active=True).values('id', 'name')
        return JsonResponse(list(dtes), safe=False)

class EmployeeProfilePDFView(LoginRequiredMixin, View):
    def get(self, request, pk):
        profile = get_object_or_404(EmployeeProfile, pk=pk)
        pdf_data = generate_employee_profile_pdf(profile)
        employee_name = profile.user.username
        filename = f"{employee_name}_info.pdf"
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response