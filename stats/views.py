from django.shortcuts import render
from employees.models import Employee
from departments.models import Department
import json
from collections import Counter
from profiles.models import EmployeeProfile, PreEmploymentHistory
from django.contrib.auth import get_user_model
User = get_user_model()
from django.db.models import Count

def department_pie_chart(request):
    # NullでないDepartmentに属する社員を集計
    department_names = Employee.objects.filter(department__isnull=False).values_list('department__name', flat=True)
    department_counts = Counter(department_names)

    #department別の数を集計
    labels = list(department_counts.keys())
    data = list(department_counts.values())

    #dte別の数を集計
    dte_names = Employee.objects.filter(dte__isnull=False).values_list('dte__name', flat=True)
    dte_counts = Counter(dte_names)
    dte_labels = list(dte_counts.keys())
    dte_data = list(dte_counts.values())

    #新卒中途の数を前職履歴登録したかで集計
    profiles = EmployeeProfile.objects.annotate(pre_count=Count('pre_employment_histories'))
    mid_career_count = profiles.filter(pre_count__gt=0).count()
    new_graduate_count = profiles.filter(pre_count=0).count()
    bar_labels = ['新卒', '中途']
    bar_data = [new_graduate_count, mid_career_count]

    context = {
        'labels': json.dumps(labels, ensure_ascii=False),
        'data': data,
        'bar_labels': json.dumps(bar_labels, ensure_ascii=False),
        'bar_data': bar_data,
        'dte_labels': json.dumps(dte_labels, ensure_ascii=False),
        'dte_data': dte_data,
    }
    return render(request, 'stats/department_pie_chart.html', context)