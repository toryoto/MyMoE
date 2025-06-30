from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import EmployeeProfile, Skill
from .forms import EmployeeProfileForm
from django.http import JsonResponse
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

from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import get_template
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from xhtml2pdf import pisa
from xhtml2pdf.default import DEFAULT_FONT
from profiles.models import EmployeeProfile
import os
import io
from django.conf import settings

class EmployeeProfilePDFView(LoginRequiredMixin, View):
    def get(self, request, pk):
        profile = get_object_or_404(EmployeeProfile, pk=pk)
        template_path = 'profile_pdf.html'
        context = {'profile': profile}

        # テンプレートをHTMLに変換
        template = get_template(template_path)
        html = template.render(context)

        # フォントファイルのパス（.ttf形式）
        font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'NotoSansJP-Regular.ttf')
        DEFAULT_FONT['Noto Sans JP'] = font_path

        # xhtml2pdfにフォントを直接登録するための埋め込みCSSを作成
        font_css = f"""
        <style>
        @font-face {{
            font-family: "Noto Sans JP";
            src: url("file://{font_path}");
        }}
        body {{
            font-family: "Noto Sans JP";
        }}
        </style>
        """

        # CSSをHTMLに埋め込む
        html_with_font = font_css + html

        # PDF生成
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.StringIO(html_with_font), dest=result)

        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="profile_{pk}.pdf"'
            return response
        else:
            return HttpResponse('PDF作成中にエラーが発生しました。', status=500)
