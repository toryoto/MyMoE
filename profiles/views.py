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

    def get_object(self, queryset=None):
        return get_object_or_404(EmployeeProfile, user=self.request.user)

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

    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user

