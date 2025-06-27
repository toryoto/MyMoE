from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import EmployeeProfile
from .forms import EmployeeProfileForm,SignUpForm

class EmployeeProfileCreateView(LoginRequiredMixin, CreateView):
    model = EmployeeProfile
    form_class = EmployeeProfileForm
    template_name = 'profiles/employee_profile_form.html'
    success_url = reverse_lazy('profile_detail')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class EmployeeProfileDetailView(LoginRequiredMixin, DetailView):
    model = EmployeeProfile
    template_name = 'profiles/employee_profile_detail.html'
    context_object_name = 'profile'

    def dispatch(self, request, *args, **kwargs):
        if not EmployeeProfile.objects.filter(user=request.user).exists():
            return redirect('profile_create')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(EmployeeProfile, user=self.request.user)

class EmployeeProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = EmployeeProfile
    form_class = EmployeeProfileForm
    template_name = 'profiles/employee_profile_form.html'
    success_url = reverse_lazy('profile_detail')

    def dispatch(self, request, *args, **kwargs):
        if not EmployeeProfile.objects.filter(user=request.user).exists():
            return redirect('profile_create')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(EmployeeProfile, user=self.request.user)

    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user
    
# 新規登録（Sign Up）画面のビュー関数を追加
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # フォームのデータを処理します
            pass
    else:
        form = SignUpForm()
    
    return render(request, 'profiles/sign_up.html', {'form': form})