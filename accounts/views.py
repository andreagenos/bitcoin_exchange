from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .forms import RegisterForm


def sign_up(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'registration/register.html', {'form': form}) 
    
    if request.method == 'POST':
        form = RegisterForm(request.POST) 
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request, 'You have singed up successfully.')
            login(request, user)
            return redirect('http://127.0.0.1:8000/')
        else:
            return render(request, 'registration/register.html', {'form': form})

