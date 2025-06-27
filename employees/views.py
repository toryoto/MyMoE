from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.generic import ListView
from .forms import EmployeeCreationForm
from .models import Employee

def mymoe_home(request):
    if not request.user.is_authenticated:
        return redirect('home')
    return render(request, 'mymoe/index.html')

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
