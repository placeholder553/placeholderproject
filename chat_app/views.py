from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.http import HttpResponse

def main_view(request):
    template = loader.get_template('base.html')
    return HttpResponse(template.render())

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat', recipient_username=user.username)
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})
 
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('chat', recipient_username=user.username)
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})
    
    
    
@login_required(login_url='login')
def chat_view(request, recipient_username):
    return render(request, 'chat.html', {'recipient_username': recipient_username})