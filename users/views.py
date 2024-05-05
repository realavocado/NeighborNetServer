from django.http import HttpResponse, JsonResponse, HttpRequest
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from .forms import CustomUserCreationForm, CustomUserLoginForm
from django.contrib.auth import login, authenticate
from django.http import JsonResponse


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            errors = form.errors.as_json()
            return JsonResponse({"errors": errors}, status=400)
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
            else:
                return JsonResponse({"error": "Invalid username or password"}, status=401)
        else:
            errors = form.errors.as_json()
            return JsonResponse({"errors": errors}, status=400)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)


def is_logged_in(request):
    if request.user.is_authenticated:
        return JsonResponse({"is_login": True})
    else:
        return JsonResponse({"is_login": False})


def home(request):
    return render(request, 'home.html')
