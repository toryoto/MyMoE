from django.shortcuts import render
from employees.models import Employee
from departments.models import Department
import json
from collections import Counter
from profiles.models import EmployeeProfile, PreEmploymentHistory
from django.contrib.auth import get_user_model
User = get_user_model()
from django.db.models import Count, Q

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

    # 部署ごとの新卒・中途採用者数の集計
    stacked_bar_labels = []
    stacked_bar_new_graduate_data = []
    stacked_bar_mid_career_data = []

    departments = Department.objects.all().order_by('name') # 部署名をソートして表示順を安定させる

    for dept in departments:
        # その部署に所属する社員で、前職履歴がない（新卒）社員の数をカウント
        new_graduates_in_dept = Employee.objects.filter(
            department=dept,
            employeeprofile__pre_employment_histories__isnull=True
        ).count()

        # その部署に所属する社員で、前職履歴がある（中途）社員の数をカウント
        mid_careers_in_dept = Employee.objects.filter(
            department=dept,
            employeeprofile__pre_employment_histories__isnull=False
        ).count()

        if new_graduates_in_dept > 0 or mid_careers_in_dept > 0:
            stacked_bar_labels.append(dept.name)
            stacked_bar_new_graduate_data.append(new_graduates_in_dept)
            stacked_bar_mid_career_data.append(mid_careers_in_dept)

    context = {
        'labels': json.dumps(labels, ensure_ascii=False),
        'data': data,
        'bar_labels': json.dumps(bar_labels, ensure_ascii=False),
        'bar_data': bar_data,
        'dte_labels': json.dumps(dte_labels, ensure_ascii=False),
        'dte_data': dte_data,
        'stacked_bar_labels': json.dumps(stacked_bar_labels, ensure_ascii=False),
        'stacked_bar_new_graduate_data': stacked_bar_new_graduate_data,
        'stacked_bar_mid_career_data': stacked_bar_mid_career_data,
    }
    return render(request, 'stats/department_pie_chart.html', context)