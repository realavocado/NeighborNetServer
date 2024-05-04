from django.http import HttpResponse
from django.http import JsonResponse
# from .models import Message, Thread
import json

def follow_block(request):
    return JsonResponse({'message': 'follow_block'})

def apply_block(request):
    return JsonResponse({'message': 'apply_block'})

def leave_block(request):
    return JsonResponse({'message': 'leave_block'})

def get_block_requests(request):
    return JsonResponse({'message': 'get_block_requests'})

def approve_block_request(request):
    return JsonResponse({'message': 'approve_block_request'})
