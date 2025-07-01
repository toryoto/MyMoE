from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.generic import ListView
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import View
from django.contrib import messages
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db.models import Q
from django.http import JsonResponse

from .forms import EmployeeCreationForm
from .models import Employee
from .forms import CSVUploadForm
from .utils.csv_processor import CSVProcessor
from departments.models import Department, DTE
from profiles.models import Skill, EmployeeProfile
# CSV関連
from django.http import FileResponse, HttpResponse
import os
from django.conf import settings
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import ML_CHOICES

def mymoe_home(request):
    if not request.user.is_authenticated:
        return redirect('home')
    return render(request, 'mymoe/index.html')

class CustomLoginView(LoginView):
    """カスタムログインビュー（パスワード変更チェック付き）"""
    template_name = 'employees/login.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.get_user()
        
        # 初回ログインチェック
        if getattr(user, 'force_password_change', False):
            return redirect('employees:force_password_change')
        
        return response
    
class ForcePasswordChangeView(LoginRequiredMixin, View):
    """強制パスワード変更ビュー"""
    template_name = 'employees/force_password_change.html'
    
    def dispatch(self, request, *args, **kwargs):
        # 既にパスワード変更済みの場合はダッシュボードへ
        if not getattr(request.user, 'force_password_change', False):
            return redirect('mymoe_home')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        form = PasswordChangeForm(request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # フラグをクリア
            user.force_password_change = False
            user.save()
            
            # セッションを更新（再ログイン不要）
            update_session_auth_hash(request, user)
            messages.success(request, 'パスワードが正常に変更されました。MyMoEへようeso！')
            return redirect('mymoe_home')
        
        return render(request, self.template_name, {'form': form})

def signup(request):
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST) 
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('mymoe_home')
    else:
        form = EmployeeCreationForm()
    return render(request, 'employees/signup.html', {'form': form})

class EmployeeListView(ListView):
    model = Employee
    template_name = 'employees/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        
        search_query = self.request.GET.get('search_query')
        department_id = self.request.GET.get('department')
        dte_id = self.request.GET.get('dte')
        skill_names = self.request.GET.get('skills')

        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        if department_id:
            queryset = queryset.filter(department__id=department_id)
        if dte_id:
            queryset = queryset.filter(dte__id=dte_id)
        if skill_names:
            # スキル名でフィルタリング
            # EmployeeProfileを介してSkillを検索
            queryset = queryset.filter(employeeprofile__skills__name__icontains=skill_names)
            
        return queryset.distinct() # 重複を除去

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        context['dtes'] = DTE.objects.all()
        context['current_search_query'] = self.request.GET.get('search_query', '')
        context['current_department'] = self.request.GET.get('department', '')
        context['current_dte'] = self.request.GET.get('dte', '')
        context['current_skills'] = self.request.GET.get('skills', '')
        return context

class HRRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_hr

# Step 1: CSVアップロード・バリデーション
class CSVBulkImportView(HRRequiredMixin, View):
    template_name = 'employees/csv_bulk_import.html'
    
    def get(self, request):
        form = CSVUploadForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = CSVUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            processor = CSVProcessor()
            
            # CSVバリデーション
            validation_result = processor.validate_csv(csv_file)
            
            if not validation_result['valid']:
                messages.error(request, validation_result['error'])
                return render(request, self.template_name, {'form': form})
            
            # セッションに検証済みデータを保存
            request.session['csv_validation_data'] = validation_result['data']
            
            # プレビュー画面にリダイレクト
            return redirect('employees:csv_preview')
        
        return render(request, self.template_name, {'form': form})

# Step 2: プレビュー確認
class CSVPreviewView(HRRequiredMixin, View):
    template_name = 'employees/csv_preview.html'
    
    def get(self, request):
        validation_data = request.session.get('csv_validation_data')
        
        if not validation_data:
            messages.error(request, 'プレビューデータが見つかりません。CSVファイルを再度アップロードしてください。')
            return redirect('csv_bulk_import')
        
        total_rows = len(validation_data)
        valid_rows = sum(1 for row in validation_data if row['is_valid'])
        error_rows = total_rows - valid_rows
        
        context = {
            'validation_data': validation_data,
            'total_rows': total_rows,
            'valid_rows': valid_rows,
            'error_rows': error_rows,
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        validation_data = request.session.get('csv_validation_data')
        
        if not validation_data:
            messages.error(request, '処理データが見つかりません。')
            return redirect('csv_bulk_import')
        
        processor = CSVProcessor()
        
        # 一括登録実行
        result = processor.process_csv(validation_data)
        
        # セッションデータをクリア
        del request.session['csv_validation_data']
        
        # 結果をセッションに保存
        request.session['import_result'] = result
        
        return redirect('employees:csv_result')

# Step 3: 実際のインポート実行
class CSVResultView(HRRequiredMixin, View):
    template_name = 'employees/csv_result.html'
    
    def get(self, request):
        result = request.session.get('import_result')
        
        if not result:
            messages.error(request, '結果データが見つかりません。')
            return redirect('csv_bulk_import')
        
        return render(request, self.template_name, {'result': result})

def download_sample_csv(request):
    file_path = os.path.join(settings.BASE_DIR, 'docs', 'sample_employees_list.csv')
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='sample_employees_list.csv')
    else:
        messages.error(request, "サンプルCSVファイルが見つかりません。")
        return redirect('csv_bulk_import')

@login_required
@require_POST
def update_ml(request, pk):
    if not request.user.is_hr:
        return HttpResponse("権限がありません。", status=403)

    try:
        employee = Employee.objects.get(pk=pk)
    except Employee.DoesNotExist:
        return HttpResponse("社員が見つかりません。", status=404)

    ml_value = request.POST.get('ml')

    # ML_CHOICESから有効な選択肢のリストを作成
    valid_ml_choices = [choice[0] for choice in ML_CHOICES]

    if ml_value not in valid_ml_choices:
        return HttpResponse("無効なML値です。", status=400)

    employee.ml = ml_value
    employee.save()

    return HttpResponse("MLが正常に更新されました。", status=200)
