from django.http import HttpResponse
from django.http import JsonResponse
from .models import Friend, Neighbor, Friendrequest, UsersCustomuser
from message.utils import get_user_block
import json
import datetime

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
                    'full_name': friend.fid.first_name + ' ' + friend.fid.last_name,
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
                    'full_name': neigbor.nid.first_name + ' ' + neigbor.nid.last_name,
                    'image_url': neigbor.nid.image_url})

            # Get all friends of the current user
            return JsonResponse({'neighbors': user_neigbors}, status=200)

        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)
    return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)


def get_friend_request(request):
    # Get the current user's uid test
    if request.method == 'GET':
        if request.user.is_authenticated:
            uid = request.user.id
            user_requests = []
            requests = Friendrequest.objects.filter(
                receiver=uid, status='pending')
            for request in requests:
                # Add friend's uid and fid to the set
                user_requests.append({
                    'id': request.requester.id,
                    'username': request.requester.username,
                    'image_url': request.requester.image_url})

            # Get all friends of the current user
            return JsonResponse({'requests': user_requests}, status=200)

        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)
    return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)


def add_friend(request):
    # Get the current user's uid test
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            username = data.get('username', None)
            usr = UsersCustomuser.objects.filter(id=request.user.id).first()
            fsr = UsersCustomuser.objects.filter(username=username).first()
            if fsr and usr:
                # Add friend's Request
                fr = Friendrequest(
                    requester=usr, receiver=fsr, status='pending', request_date=datetime.datetime.now())
                fr.save()

                # Get all friends of the current user
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'error': 'user not found'}, status=404)
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)


def accept_friend(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            fid = data.get('id', None)
            usr = UsersCustomuser.objects.filter(id=request.user.id).first()
            fsr = UsersCustomuser.objects.filter(id=fid).first()
            if fsr and usr:
                # Add friend's uid and fid to the set
                
                friend = Friend(uid=usr, fid=fsr)
                friend.save()
                friend = Friend(fid=usr, uid=fsr)
                friend.save()

                Friendrequest.objects.filter(
                    receiver=request.user.id, requester=fsr.id, status='pending')\
                    .update(status='accepted')

                # Get all friends of the current user
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'error': 'user not found'}, status=404)
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)

def reject_friend(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            fid = data.get('id', None)
            usr = UsersCustomuser.objects.filter(id=request.user.id).first()
            fsr = UsersCustomuser.objects.filter(id=fid).first()
            if fsr and usr:
                # Add friend's uid and fid to the set
                Friendrequest.objects.filter(
                    receiver=request.user.id, requester=fsr.id, status='pending')\
                    .update(status='rejected')

                # Get all friends of the current user
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'error': 'user not found'}, status=404)
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


def follow_neighbor(request):
    # Get the current user's uid test
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            username = data.get('username', None)
            usr = UsersCustomuser.objects.filter(id=request.user.id).first()
            nsr = UsersCustomuser.objects.filter(username=username).first()
            if nsr and usr:
                if get_user_block(usr.id) != get_user_block(nsr.id):
                    return JsonResponse({'error': 'cannot not follow user in different block'}, status=400)
                # Add friend's uid and fid to the set
                neighbor = Neighbor(uid=usr, nid=nsr)
                neighbor.save()

                # Get all friends of the current user
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'error': 'user not found'}, status=404)
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


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
