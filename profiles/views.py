from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import EmployeeProfile
from .forms import EmployeeProfileForm
from django.http import JsonResponse
from django.views import View
from employees.models import Employee
from departments.models import Department, DTE
import json
from django.template.loader import render_to_string

class EmployeeProfileCreateView(LoginRequiredMixin, CreateView):
    model = EmployeeProfile
    form_class = EmployeeProfileForm
    template_name = 'profiles/employee_profile_form.html'
    success_url = reverse_lazy('profiles:my_profile_detail')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class MyProfileDetailView(LoginRequiredMixin, DetailView):
    model = EmployeeProfile
    template_name = 'profiles/employee_profile_detail.html'
    context_object_name = 'profile'

    def dispatch(self, request, *args, **kwargs):
        if not EmployeeProfile.objects.filter(user=request.user).exists():
            return redirect('profiles:profile_create')
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

    def dispatch(self, request, *args, **kwargs):
        if not EmployeeProfile.objects.filter(user=request.user).exists():
            return redirect('profiles:profile_create')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
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