from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def get_message_with_keyword(request):
    return render(request, 'hello.html', {'name': 'Letian Jiang'})
    # return HttpResponse("Hello, world. You're at the polls list.")
