from django.http import HttpResponse
from django.http import JsonResponse
from .models import Friend, Neighbor, Friendrequest, UsersCustomuser
from message.utils import get_user_block
import json
import datetime
from django.db import connection

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


# SQL version
def get_all_friends_sql(request):
    # Check if the request method is GET
    if request.method == 'GET':
        # Check if the user is authenticated
        if request.user.is_authenticated:
            uid = request.user.id
            user_friends = []

            # Execute SQL query to fetch friends of the current user
            with connection.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT f.id, f.username, f.first_name, f.last_name, f.image_url
                    FROM users_customuser u
                    INNER JOIN friend ON u.id = friend.uid
                    INNER JOIN users_customuser f ON friend.fid = f.id
                    WHERE friend.uid = %s
                    ''',
                    [uid]
                )
                rows = cursor.fetchall()

                # Fetch and format the results
                for row in rows:
                    user_friends.append({
                        'id': row[0],
                        'username': row[1],
                        'full_name': row[2] + ' ' + row[3],
                        'image_url': row[4]
                    })

            # Return the list of friends as JSON response
            return JsonResponse({'friends': user_friends}, status=200)
        else:
            # Return error response if user is not authenticated
            return JsonResponse({'error': 'not authenticated user'}, status=401)
    else:
        # Return error response for non-GET requests
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)


def get_follow_neighbors_sql(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            uid = request.user.id

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT n.id, n.username, n.first_name, n.last_name, n.image_url
                    FROM users_customuser u
                    INNER JOIN neighbor ON u.id = neighbor.uid
                    INNER JOIN users_customuser n ON neighbor.nid = n.id
                    WHERE neighbor.uid = %s
                """, [uid])
                neighbors = cursor.fetchall()

            user_neighbors = []
            for neighbor in neighbors:
                user_neighbors.append({
                    'id': neighbor[0],
                    'username': neighbor[1],
                    'full_name': f"{neighbor[2]} {neighbor[3]}",
                    'image_url': neighbor[4]
                })

            return JsonResponse({'neighbors': user_neighbors}, status=200)

        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)
    return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)


def get_friend_request_sql(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            uid = request.user.id
            user_requests = []

            # Execute raw SQL query
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT id, username, image_url 
                    FROM friendrequest 
                    INNER JOIN users_customuser ON requester_id = id
                    WHERE receiver_id = %s AND status = 'pending'
                    """, [uid])
                rows = cursor.fetchall()
                for row in rows:
                    user_requests.append({
                        'id': row[0],
                        'username': row[1],
                        'image_url': row[2]
                    })

            return JsonResponse({'requests': user_requests}, status=200)

        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)
    return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)


def add_friend_sql(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            username = data.get('username', None)
            user_id = request.user.id
            
            # Fetch the current user's information
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users_customuser WHERE id = %s", [user_id])
                usr = cursor.fetchone()

            # Fetch the friend's information
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users_customuser WHERE username = %s", [username])
                fsr = cursor.fetchone()

            if fsr and usr:
                # Add friend's Request
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO friendrequest (requester_id, receiver_id, status, request_date) VALUES (%s, %s, %s, %s)",
                                   [usr[0], fsr[0], 'pending', datetime.datetime.now()])

                # Get all friends of the current user
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'error': 'user not found'}, status=404)
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)


def accept_friend_sql(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            fid = data.get('id', None)
            user_id = request.user.id
            
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM users_customuser WHERE id = %s", [user_id]
                )
                user = cursor.fetchone()
                
                cursor.execute(
                    "SELECT * FROM users_customuser WHERE id = %s", [fid]
                )
                friend = cursor.fetchone()
                
                if friend and user:
                    cursor.execute(
                        "INSERT INTO friend (uid, fid) VALUES (%s, %s)",
                        [user_id, fid]
                    )
                    cursor.execute(
                        "INSERT INTO friend (uid, fid) VALUES (%s, %s)",
                        [fid, user_id]
                    )
                    
                    cursor.execute(
                        "UPDATE friendrequest SET status = 'accepted' WHERE receiver_id = %s AND requester_id = %s AND status = 'pending'",
                        [user_id, fid]
                    )
                    
                    return JsonResponse({'status': 'success'})
                else:
                    return JsonResponse({'error': 'user not found'}, status=404)
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)


def reject_friend_sql(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            fid = data.get('id', None)
            usr_id = request.user.id

            # Get the cursor
            with connection.cursor() as cursor:
                # Update the status of the friend request
                cursor.execute(
                    "UPDATE friendrequest SET status = 'rejected' "
                    "WHERE receiver_id = %s AND requester_id = %s AND status = 'pending'",
                    [usr_id, fid]
                )

                # Check if any rows were affected
                if cursor.rowcount > 0:
                    # Return success response
                    return JsonResponse({'status': 'success'})
                else:
                    # No rows were updated, indicating either the request doesn't exist or it's not pending
                    return JsonResponse({'error': 'Friend request not found or already responded'}, status=404)
        else:
            return JsonResponse({'error': 'Not authenticated user'}, status=401)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


def follow_neighbor_sql(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            username = data.get('username', None)
            usr_id = request.user.id
            
            # Fetch the user's block
            with connection.cursor() as cursor:
                cursor.execute("SELECT bid FROM user_in_block WHERE uid = %s", [usr_id])
                usr_block = cursor.fetchone()[0] if cursor.rowcount > 0 else None
                if not usr_block:
                    return JsonResponse({'error': 'Username not found or this user not in your block'}, status=404)

            # Fetch the neighbor's block
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM users_customuser WHERE username = %s", [username])
                row = cursor.fetchone()
                if row:
                    nsr_id = row[0]
                    cursor.execute("SELECT bid FROM user_in_block WHERE uid = %s", [nsr_id])
                    nsr_block = cursor.fetchone()[0]
                else:
                    return JsonResponse({'error': 'user not found'}, status=404)

            if usr_block == nsr_block:
                # Check if the users are not already neighbors
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM neighbor WHERE uid = %s AND nid = %s", [usr_id, nsr_id])
                    count = cursor.fetchone()[0]
                
                if count == 0:
                    # Add the neighbor relationship
                    with connection.cursor() as cursor:
                        cursor.execute("INSERT INTO neighbor (uid, nid) VALUES (%s, %s)", [usr_id, nsr_id])
                    return JsonResponse({'status': 'success'})
                else:
                    return JsonResponse({'error': 'User is already a neighbor'}, status=400)
            else:
                return JsonResponse({'error': 'Cannot follow user in different block'}, status=400)
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
