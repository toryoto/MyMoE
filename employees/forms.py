from django.contrib.auth.forms import UserCreationForm
from django import forms
import csv
from io import StringIO
from departments.models import Department, DTE
from .models import Employee
from django.core.validators import RegexValidator
from django import forms

class EmployeeCreationForm(UserCreationForm):
    username = forms.CharField(
        label='ユーザーID',
        max_length=50,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z]+\.[a-zA-Z]+$',
                message='EIDのみ入力可能です。'
            )
        ]
    )
    
    class Meta(UserCreationForm.Meta):
        model = Employee
        fields = ('username', 'email')


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='CSVファイル',
        help_text='UTF-8エンコーディングのCSVファイルをアップロードしてください',
        widget=forms.FileInput(attrs={'accept': '.csv', 'class': 'form-control'})
    )

    def clean_csv_file(self):
        file = self.cleaned_data['csv_file']
        
        if not file.name.endswith('.csv'):
            raise forms.ValidationError('CSVファイルをアップロードしてください')
        
        if file.size > 5 * 1024 * 1024:
            raise forms.ValidationError('ファイルサイズは5MB以下にしてください')
        
        return file
