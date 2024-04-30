from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def get_message(request):
    return render(request, 'hello.html', {'name': 'Letian Jiang'})
