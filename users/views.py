from django.http import HttpResponse, JsonResponse, HttpRequest
from django.shortcuts import render
from django.test import RequestFactory
from django.views.decorators.csrf import ensure_csrf_cookie
from .forms import CustomUserCreationForm, CustomUserLoginForm
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
import json

from .models import CustomUser


# Create your views here.
# def get_message(request):
#     return render(request, 'hello.html', {'name': 'Letian Jiang'})


def register(request):
    if request.method == 'POST':
        data = request.POST
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        bio = data.get('bio')
        address = data.get('address')

        if not (username and email and password):
            return JsonResponse({'error': 'username, email and password fields are required'}, status=400)

        if CustomUser.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username is already taken'}, status=400)

        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email is already registered'}, status=400)

        user = CustomUser.objects.create_user(username=username, email=email, password=password,
                                              first_name=first_name, last_name=last_name, bio=bio, address=address)
        user.save()

        # factory = RequestFactory()
        # login_request = factory.post('/users/login/', {'email': email, 'password': password})
        # login(login_request, user)

        return JsonResponse({'success': 'User registered successfully'}, status=201)

    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


@ensure_csrf_cookie
def set_csrf_token(request):
    response = HttpResponse("csrf_cookie set ")
    return response


def user_login(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({"message": "Login successful"}, status=200)
                # return redirect('home')
    else:
        form = CustomUserLoginForm()
    return render(request, 'registration/login.html', {'form': form})


def home(request):
    return render(request, 'home.html')
