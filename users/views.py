from django.middleware.csrf import get_token
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from .forms import CustomUserCreationForm, CustomUserLoginForm


# Create your views here.
def get_message(request):
    return render(request, 'hello.html', {'name': 'Letian Jiang'})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@ensure_csrf_cookie
def set_csrf_token(request):
    response = HttpResponse("csrf_cookie set ")
    return response


# @csrf_exempt
# @ensure_csrf_cookie
def user_login(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                # return render(request, 'home.html')
                return JsonResponse({"message": "Login successful"}, status=200)
                # return redirect('home')
    else:
        form = CustomUserLoginForm()
    return render(request, 'registration/login.html', {'form': form})


def home(request):
    return render(request, 'home.html')
