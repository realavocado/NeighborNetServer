from django.http import HttpResponse
from django.http import JsonResponse
from .models import Friend, Neighbor, Friendrequest
import json

# Create your views here.


def get_all_friends(request):
    # Get the current user's uid test
    if request.method == 'GET':
        if request.user.is_authenticated:
            uid = request.user.id
            user_friends = []
            friends = Friend.objects.filter(uid=uid)
            for friend in friends:
            # Add friend's uid and fid to the set
                user_friends.append({
                    'id': friend.fid.id,
                    'username': friend.fid.username, 
                    'image_url': friend.fid.image_url})

            # Get all friends of the current user
            return JsonResponse({'friends': user_friends}, status=200)
        
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)
    return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)


def get_follow_neigbors(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            uid = request.user.id
            user_neigbors = []
            neigbors = Neighbor.objects.filter(uid=uid)
            for neigbor in neigbors:
                # Add friend's uid and fid to the set
                user_neigbors.append({
                    'id': neigbor.nid.id,
                    'username': neigbor.nid.username, 
                    'image_url': neigbor.nid.image_url})

            # Get all friends of the current user
            return JsonResponse({'neighbors': user_neigbors}, status=200)
        
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)
    return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)


def get_friend_request(request):
    # Get the current user's uid test
    uid = 1
    user_requests = []
    requests = Friendrequest.objects.filter(receiver=uid, status='pending')
    for request in requests:
        # Add friend's uid and fid to the set
        user_requests.append({
            'id': request.requester.id,
            'username': request.requester.username,
            'image_url': request.requester.image_url})

    # Get all friends of the current user
    return JsonResponse({'requests': user_requests})

def add_friend(request):
    # Get the current user's uid test
    uid = 1
    if request.method == 'POST':
        data = json.loads(request.body)
        fid = data['fid']
        # Add friend's uid and fid to the set
        friend = Friend(uid=uid, fid=fid)
        friend.save()

        # Get all friends of the current user
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'})

def follow_neighbor(request):
    # Get the current user's uid test
    uid = 1
    if request.method == 'POST':
        data = json.loads(request.body)
        nid = data['nid']
        # Add friend's uid and fid to the set
        neighbor = Neighbor(uid=uid, nid=nid)
        neighbor.save()

        # Get all friends of the current user
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'})

def remove_friend(request):
    # Get the current user's uid test
    uid = 1
    if request.method == 'POST':
        data = json.loads(request.body)
        fid = data['fid']
        # Add friend's uid and fid to the set
        friend = Friend.objects.filter(uid=uid, fid=fid)
        friend.delete()
        friend = Friend.objects.filter(uid=fid, fid=uid)
        friend.delete()

        # Get all friends of the current user
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'})

def unfollow_neighbor(request):
    # Get the current user's uid test
    uid = 1
    if request.method == 'POST':
        data = json.loads(request.body)
        nid = data['nid']
        # Add friend's uid and fid to the set
        neighbor = Neighbor.objects.filter(uid=uid, nid=nid)
        neighbor.delete()

        # Get all friends of the current user
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'})

def add_friend_request(request):
    # Get the current user's uid test
    uid = 1
    if request.method == 'POST':
        data = json.loads(request.body)
        fid = data['fid']
        # Add friend's uid and fid to the set
        request = Friendrequest(requester=uid, receiver=fid)
        request.save()

        # Get all friends of the current user
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'})

def get_all_neighbors(request):
    # Get the current user's uid test
    uid = 1
    bid = 1
    all_neighbors = []
    # neighbors = Neighbor.objects.filter(uid=uid)
    # for neighbor in neighbors:
    #     # Add friend's uid and fid to the set
    #     user_neighbors.append({
    #         'id': neighbor.nid.id,
    #         'username': neighbor.nid.username, 
    #         'image_url': neighbor.nid.image_url})

    # Get all friends of the current user
    return JsonResponse({'neighbors': all_neighbors})
