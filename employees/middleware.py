from django.shortcuts import redirect
from django.urls import reverse

# デフォルトパスワードから変更していないユーザのすべてのアクセスを拒否するミドルウェア
class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and getattr(request.user, 'force_password_change', False):
            allowed_paths = [
                reverse('employees:force_password_change'),
                reverse('employees:logout'),
            ]
            
            # 現在のパスが許可されたパスに含まれていない場合、パスワード変更ページへリダイレクト
            # Django Adminサイトへのアクセスも許可する
            if request.path not in allowed_paths and not request.path.startswith('/admin/'):
                return redirect('employees:force_password_change')
        
        response = self.get_response(request)
        return response
