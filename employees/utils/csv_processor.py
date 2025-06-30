import csv
from io import StringIO
from django.contrib.auth import get_user_model
from departments.models import Department, DTE
from django.core.exceptions import ValidationError
from django.db import transaction

User = get_user_model()

class CSVProcessor:
    def __init__(self):
        self.results = {
            'success': [],
            'errors': [],
            'warnings': []
        }
        self.required_fields = ['username', 'email', 'first_name', 'last_name', 'department_code', 'dte_code']
        
    def validate_csv(self, csv_file):
        """CSVファイルのバリデーション"""
        try:
            # ファイル内容を読み取り
            content = csv_file.read().decode('utf-8')
            csv_file.seek(0)  # ファイルポインタをリセット
            
            # CSV解析
            csv_data = list(csv.DictReader(StringIO(content)))
            
            if not csv_data:
                return {'valid': False, 'error': 'CSVファイルが空です'}
            
            # ヘッダーチェック
            headers = csv_data[0].keys()
            missing_headers = [field for field in self.required_fields if field not in headers]
            
            if missing_headers:
                return {
                    'valid': False, 
                    'error': f'必須列が不足しています: {", ".join(missing_headers)}'
                }
            
            # 各行をバリデーション
            validated_data = []
            for i, row in enumerate(csv_data, start=2):  # 2行目から開始
                result = self._validate_row(row, i)
                validated_data.append(result)
            
            return {
                'valid': True,
                'data': validated_data,
                'total_rows': len(csv_data)
            }
            
        except UnicodeDecodeError:
            return {'valid': False, 'error': 'ファイルエンコーディングが正しくありません（UTF-8を使用してください）'}
        except Exception as e:
            return {'valid': False, 'error': f'ファイル処理エラー: {str(e)}'}
    
    def _validate_row(self, row, row_number):
        """各行のデータバリデーション"""
        errors = []
        warnings = []
        
        # 必須フィールドチェック
        for field in self.required_fields:
            if not row.get(field, '').strip():
                errors.append(f'{field}が空です')
        
        # ユーザー名重複チェック
        if row.get('username') and User.objects.filter(username=row['username']).exists():
            errors.append(f'ユーザー名 "{row["username"]}" は既に存在します')
        
        # メール重複チェック
        if row.get('email') and User.objects.filter(email=row['email']).exists():
            errors.append(f'メールアドレス "{row["email"]}" は既に存在します')
        
        # 部署コードチェック
        department = None
        department_data = None
        if row.get('department_code'):
            try:
                department = Department.objects.get(code=row['department_code'], is_active=True)
                # セッション保存用に辞書形式に変換
                department_data = {
                    'id': department.id,
                    'name': department.name,
                    'code': department.code
                }
            except Department.DoesNotExist:
                errors.append(f'部署コード "{row["department_code"]}" が存在しません')
        
        # DTEコードチェック
        dte = None
        dte_data = None
        if row.get('dte_code'):
            if department:
                try:
                    dte = DTE.objects.get(code=row['dte_code'], department=department, is_active=True)
                    # セッション保存用に辞書形式に変換
                    dte_data = {
                        'id': dte.id,
                        'name': dte.name,
                        'code': dte.code,
                        'department_id': dte.department.id
                    }
                except DTE.DoesNotExist:
                    errors.append(f'DTE "{row["dte_code"]}" が部署 "{department.name}" に存在しません')
            else:
                warnings.append('部署が指定されていないため、DTEは設定されません')
        
        return {
            'row_number': row_number,
            'data': row,
            'department_data': department_data,  # 辞書形式
            'dte_data': dte_data,               # 辞書形式
            'errors': errors,
            'warnings': warnings,
            'is_valid': len(errors) == 0
        }
    
    @transaction.atomic
    def process_csv(self, validated_data, initial_password="TempPass2025"):
        """検証済みデータの一括登録処理"""
        success_count = 0
        failed_rows = []
                
        for row_data in validated_data:
            if not row_data['is_valid']:
                failed_rows.append(row_data)
                continue
            
            try:
                User.objects.create_user(
                    username=row_data['data']['username'],
                    email=row_data['data']['email'],
                    first_name=row_data['data']['first_name'],
                    last_name=row_data['data']['last_name'],
                    password=initial_password,
                    force_password_change=True,
                    department = Department.objects.get(id=row_data['department_data']['id']),
                    dte = DTE.objects.get(id=row_data['dte_data']['id'])
                )

                success_count += 1

            except Exception as e:
                row_data['errors'].append(f'登録エラー: {str(e)}')
                failed_rows.append(row_data)

        return {
            'success_count': success_count,
            'failed_count': len(failed_rows),
            'failed_rows': failed_rows,
            'initial_password': initial_password
        }