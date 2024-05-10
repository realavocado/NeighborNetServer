import json

from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from .forms import CustomUserCreationForm, CustomUserLoginForm
from django.contrib.auth import login, authenticate
from django.http import JsonResponse


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
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
                return JsonResponse({
                    "message": "Login successful",
                    "user": {
                        "userId": user.id,
                        "full_name": user.get_full_name(),
                        'username': user.username,
                        "email": user.email,
                        "address": user.address,
                        "bio": user.bio
                    }
                }, status=200)
            else:
                return JsonResponse({"error": "Invalid username or password"}, status=401)
        else:
            errors = form.errors.as_json()
            return JsonResponse({"errors": errors}, status=400)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)


def is_logged_in(request):
    if request.user.is_authenticated:
        return JsonResponse({
            "is_logged_in": True,
            "user": {
                "userId": request.user.id,
                "full_name": request.user.get_full_name(),
                'username': request.user.username,
                "email": request.user.email,
                "address": request.user.address,
                "bio": request.user.bio
            }
        })
    else:
        return JsonResponse({"is_logged_in": False})


def update_user_info(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)

        username = body_data.get('username')
        address = body_data.get('address')
        bio = body_data.get('bio')

        user = request.user

        user.username = username
        user.address = address
        user.bio = bio
        user.save()
        return JsonResponse({
            'success': 'User profile updated successfully',
            "user": {
                "userId": user.id,
                "full_name": user.get_full_name(),
                'username': user.username,
                "email": user.email,
                "address": user.address,
                "bio": user.bio
            }
        }, status=201)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)
