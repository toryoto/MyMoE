from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import EmployeeProfile, Skill, PreEmploymentHistory
from .forms import EmployeeProfileForm, PreEmploymentHistoryFormSet, PreEmploymentHistoryForm
from django.http import JsonResponse,HttpResponseForbidden, HttpResponse
from django.views import View
from employees.models import Employee
from departments.models import Department, DTE
import json
from django.template.loader import render_to_string
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
        return context

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
    
class UpdateEmployeeOrgInfoView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_hr
    
    def post(self, request, employee_id):
        try:
            data = json.loads(request.body)
            employee = get_object_or_404(Employee, id=employee_id)
            
            department_id = data.get('department_id')
            dte_id = data.get('dte_id')
            
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
                    return JsonResponse({
                        'status': 'error',
                        'message': '選択したDTEは選択した部署に属していません'
                    }, status=400)
                employee.dte = dte
            else:
                employee.dte = None
            
            employee.save()
            
            # 更新された組織情報のHTMLを生成
            html = render_to_string('components/user_org_info.html', {
                'employee': employee
            })
            
            return JsonResponse({
                'status': 'success',
                'message': '組織情報が更新されました',
                'html': html
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': '無効なリクエストデータです'
            }, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

class GetDTEsForDepartmentView(LoginRequiredMixin, View):
    def get(self, request, department_id):
        dtes = DTE.objects.filter(department_id=department_id, is_active=True).values('id', 'name')
        return JsonResponse(list(dtes), safe=False)

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
        return context

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
    
class UpdateEmployeeOrgInfoView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_hr
    
    def post(self, request, employee_id):
        try:
            data = json.loads(request.body)
            employee = get_object_or_404(Employee, id=employee_id)
            
            department_id = data.get('department_id')
            dte_id = data.get('dte_id')
            
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
                    return JsonResponse({
                        'status': 'error',
                        'message': '選択したDTEは選択した部署に属していません'
                    }, status=400)
                employee.dte = dte
            else:
                employee.dte = None
            
            employee.save()
            
            # 更新された組織情報のHTMLを生成
            html = render_to_string('components/user_org_info.html', {
                'employee': employee
            })
            
            return JsonResponse({
                'status': 'success',
                'message': '組織情報が更新されました',
                'html': html
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': '無効なリクエストデータです'
            }, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

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