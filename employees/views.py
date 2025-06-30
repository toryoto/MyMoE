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
from .forms import EmployeeCreationForm
from .models import Employee
from .forms import CSVUploadForm
from .utils.csv_processor import CSVProcessor

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
            return redirect('force_password_change')
        
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
            messages.success(request, 'パスワードが正常に変更されました。MyMoEへようこそ！')
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
            return redirect('csv_preview')
        
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
        
        return redirect('csv_result')

# Step 3: 実際のインポート実行
class CSVResultView(HRRequiredMixin, View):
    template_name = 'employees/csv_result.html'
    
    def get(self, request):
        result = request.session.get('import_result')
        
        if not result:
            messages.error(request, '結果データが見つかりません。')
            return redirect('csv_bulk_import')
        
        return render(request, self.template_name, {'result': result})