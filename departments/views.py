from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Department, DTE


def dtes_by_department(request, department_id):
    dtes = DTE.objects.filter(department_id=department_id).values('id', 'name')
    return JsonResponse(list(dtes), safe=False)


class SuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    template_name = 'departments/department_list.html'
    context_object_name = 'departments'

class DepartmentDetailView(LoginRequiredMixin, DetailView):
    model = Department
    template_name = 'departments/department_detail.html'
    context_object_name = 'department'

class DepartmentCreateView(SuperuserRequiredMixin, CreateView):
    model = Department
    template_name = 'departments/department_form.html'
    fields = ['name', 'code', 'description', 'is_active']
    success_url = reverse_lazy('departments:department_list')

class DepartmentUpdateView(SuperuserRequiredMixin, UpdateView):
    model = Department
    template_name = 'departments/department_form.html'
    fields = ['name', 'code', 'description', 'is_active']
    success_url = reverse_lazy('departments:department_list')

class DepartmentDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Department
    template_name = 'departments/department_confirm_delete.html'
    success_url = reverse_lazy('departments:department_list')


class DTEListView(LoginRequiredMixin, ListView):
    model = DTE
    template_name = 'departments/dte_list.html'
    context_object_name = 'dtes'

class DTEDetailView(LoginRequiredMixin, DetailView):
    model = DTE
    template_name = 'departments/dte_detail.html'
    context_object_name = 'dte'

class DTECreateView(SuperuserRequiredMixin, CreateView):
    model = DTE
    template_name = 'departments/dte_form.html'
    fields = ['name', 'code', 'department', 'description', 'is_active']
    success_url = reverse_lazy('departments:dte_list')

class DTEUpdateView(SuperuserRequiredMixin, UpdateView):
    model = DTE
    template_name = 'departments/dte_form.html'
    fields = ['name', 'code', 'department', 'description', 'is_active']
    success_url = reverse_lazy('departments:dte_list')

class DTEDeleteView(SuperuserRequiredMixin, DeleteView):
    model = DTE
    template_name = 'departments/dte_confirm_delete.html'
    success_url = reverse_lazy('departments:dte_list')
