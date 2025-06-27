from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import EmployeeCreationForm
from .forms import SignUpForm

def mymoe_home(request):
    if not request.user.is_authenticated:
        return redirect('home')
    return render(request, 'mymoe/index.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST) 
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('mymoe_home')
    else:
        form = SignUpForm()
    return render(request, 'employees/signup.html', {'form': form})