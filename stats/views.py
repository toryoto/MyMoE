from django.shortcuts import render
from employees.models import Employee
from departments.models import Department
import json
from collections import Counter

def department_pie_chart(request):
    # NullでないDepartmentに属する社員を集計
    department_names = Employee.objects.filter(department__isnull=False).values_list('department__name', flat=True)
    department_counts = Counter(department_names)

    labels = list(department_counts.keys())
    data = list(department_counts.values())

    context = {
        'labels': json.dumps(labels, ensure_ascii=False),
        'data': data,
    }
    return render(request, 'stats/department_pie_chart.html', context)