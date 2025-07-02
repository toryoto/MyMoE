from django.shortcuts import render
from employees.models import Employee
from departments.models import Department
from assignments.models import Client, Project
from profiles.models import Skill, EmployeeProfile
import json
from collections import Counter, defaultdict
from django.contrib.auth import get_user_model
from django.db.models import Count, Q

User = get_user_model()

def department_pie_chart(request):
    department_names = Employee.objects.filter(department__isnull=False).values_list('department__name', flat=True)
    department_counts = Counter(department_names)
    labels = list(department_counts.keys())
    data = list(department_counts.values())

    dte_names = Employee.objects.filter(dte__isnull=False).values_list('dte__name', flat=True)
    dte_counts = Counter(dte_names)
    dte_labels = list(dte_counts.keys())
    dte_data = list(dte_counts.values())

    profiles = EmployeeProfile.objects.annotate(pre_count=Count('pre_employment_histories'))
    mid_career_count = profiles.filter(pre_count__gt=0).count()
    new_graduate_count = profiles.filter(pre_count=0).count()
    bar_labels = ['新卒', '中途']
    bar_data = [new_graduate_count, mid_career_count]

    departments = Department.objects.all().order_by('name')
    stacked_bar_labels = []
    stacked_bar_new_graduate_data = []
    stacked_bar_mid_career_data = []

    for dept in departments:
        new_graduates_in_dept = Employee.objects.filter(
            department=dept,
            employeeprofile__pre_employment_histories__isnull=True
        ).count()

        mid_careers_in_dept = Employee.objects.filter(
            department=dept,
            employeeprofile__pre_employment_histories__isnull=False
        ).count()

        if new_graduates_in_dept > 0 or mid_careers_in_dept > 0:
            stacked_bar_labels.append(dept.name)
            stacked_bar_new_graduate_data.append(new_graduates_in_dept)
            stacked_bar_mid_career_data.append(mid_careers_in_dept)

    ml_heatmap_data = []
    ml_levels = [choice[0] for choice in Employee.ML_CHOICES]
    dept_names = []
    
    for dept in departments:
        if dept.employees.exists():
            dept_names.append(dept.name)
            dept_ml_data = []
            for ml_level in ml_levels:
                count = dept.employees.filter(ml=ml_level).count()
                dept_ml_data.append(count)
            ml_heatmap_data.append(dept_ml_data)

    industry_project_counts = Client.objects.values('industry').annotate(
        project_count=Count('projects')
    ).exclude(industry__isnull=True).exclude(industry='')
    
    industry_labels = []
    industry_data = []
    for item in industry_project_counts:
        # industry choicesから日本語名を取得
        industry_dict = dict(Client.INDUSTRY_CHOICES)
        industry_name = industry_dict.get(item['industry'], item['industry'])
        industry_labels.append(industry_name)
        industry_data.append(item['project_count'])

    skill_popularity = Skill.objects.annotate(
        employee_count=Count('employeeprofile')
    ).filter(employee_count__gt=0).order_by('-employee_count')[:5]
    
    skill_labels = []
    skill_data = []
    for skill in skill_popularity:
        skill_labels.append(skill.name)
        skill_data.append(skill.employee_count)

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
        'ml_heatmap_data': json.dumps(ml_heatmap_data, ensure_ascii=False),
        'ml_levels': json.dumps([choice[1] for choice in Employee.ML_CHOICES], ensure_ascii=False),
        'dept_names_heatmap': json.dumps(dept_names, ensure_ascii=False),
        'industry_labels': json.dumps(industry_labels, ensure_ascii=False),
        'industry_data': industry_data,
        'skill_labels': json.dumps(skill_labels, ensure_ascii=False),
        'skill_data': skill_data,
    }
    return render(request, 'stats/department_pie_chart.html', context)