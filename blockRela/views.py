from django.http import HttpResponse
from django.http import JsonResponse
from .models import Block, UsersCustomuser, \
    BlockUserStatusChange, UserFollowBlock, UserInBlock, Blockjoinapprove
from message.utils import get_user_block
import datetime
import json
from django.db import connection


def get_all_blocks(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            user_blocks = []
            blocks = Block.objects.all()
            for block in blocks:
                user_blocks.append({
                    'id': block.bid,
                    'name': block.block_name, })
            return JsonResponse({'blocks': user_blocks}, status=200)
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)
    return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)


def now_block(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            bk = UserInBlock.objects.filter(uid=request.user.id).first()
            if bk is None:
                return JsonResponse({'status': False, 'message': 'not in any block'}, status=200)
            else:
                return JsonResponse({'status': True, 'message': 'in block', 'block_name': bk.bid.block_name, 'bid': bk.bid.bid}, status=200)
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)
    return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)


def all_follow_block(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            user_blocks = []
            blocks = UserFollowBlock.objects.filter(uid=request.user.id)
            for block in blocks:
                user_blocks.append({
                    'id': block.bid.bid,
                    'name': block.bid.block_name, })
            return JsonResponse({'blocks': user_blocks}, status=200)
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)
    return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)


def follow_block(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            block_name = data.get('block_name', None)
            bk = Block.objects.get(block_name=block_name)
            block = BlockUserStatusChange.objects.filter(
                bid=bk.bid, uid=request.user.id).first()
            if block is None:
                usr = UsersCustomuser.objects.filter(
                    id=request.user.id).first()
                block = BlockUserStatusChange.objects.create(
                    bid=bk, uid=usr, status='follow', date=datetime.date.today())
                bf = UserFollowBlock.objects.create(
                    bid=bk, uid=usr, date_followed=datetime.date.today())
            else:
                if block.status == 'follow':
                    return JsonResponse({'status': 'denied', 'message': 'already followed block'}, status=200)
                elif block.status == 'join':
                    return JsonResponse({'status': 'denied', 'message': 'already joined block'}, status=200)
                elif block.status == 'pending':
                    return JsonResponse({'status': 'denied', 'message': 'You have already ask for join!'}, status=200)
            return JsonResponse({'status': 'success', 'message': 'success followed block'}, status=200)
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


def apply_block(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            block_name = data.get('block_name', None)
            bk = Block.objects.get(block_name=block_name)
            # check if user already in block
            bk_join = UserInBlock.objects.filter(uid=request.user.id).first()
            if bk_join:
                return JsonResponse({'status': 'denied', 'message': 'already in block'}, status=200)
            # check if user already apply for join
            bk_pending = BlockUserStatusChange.objects.filter(
                uid=request.user.id, status='pending').exclude(bid=bk.bid)
            if bk_pending:
                return JsonResponse({'status': 'denied', 'message': 'already apply for join another block'}, status=200)

            # check user status
            block = BlockUserStatusChange.objects.filter(
                bid=bk.bid, uid=request.user.id).first()
            if block is None:
                usr = UsersCustomuser.objects.filter(
                    id=request.user.id).first()
                block = BlockUserStatusChange.objects.create(
                    bid=bk, uid=usr, status='pending', date=datetime.date.today())
                user_join_block(request.user.id, bk.bid)
            else:
                if block.status == 'follow':
                    block.status = 'pending'
                    block.date = datetime.date.today()
                    block.save()
                    user_join_block(request.user.id, bk.bid)
                    return JsonResponse({'status': 'success', 'message': 'You followed block before, Now you want to join it'}, status=200)
                elif block.status == 'join':
                    return JsonResponse({'status': 'denied', 'message': 'already joined block'}, status=200)
                elif block.status == 'pending':
                    return JsonResponse({'status': 'denied', 'message': 'You have already ask for join!'}, status=200)
                elif block.status == 'leave':
                    block.status = 'pending'
                    block.date = datetime.date.today()
                    block.save()
                    user_join_block(request.user.id, bk.bid)
                    return JsonResponse({'status': 'success', 'message': 'You left block before, Now you want to join it'}, status=200)
            return JsonResponse({'status': 'success', 'message': 'success applied block'}, status=200)
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


def leave_block(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            bid = get_user_block(request.user.id)
            if not bid:
                return JsonResponse({'status': 'denied', 'message': 'not in any block'}, status=200)

            left_bk = Block.objects.get(bid=bid)
            bs = BlockUserStatusChange.objects.filter(
                bid=bid, uid=request.user.id).first()

            if bs is None:
                return JsonResponse({'status': 'denied', 'message': 'no data in database'}, status=200)
            if bs.status == 'follow':
                return JsonResponse({'status': 'denied', 'message': 'you are following this block, not in block'}, status=200)
            elif bs.status == 'join':
                bs.status = 'leave'
                bs.date = datetime.date.today()
                bs.save()
                UserInBlock.objects.filter(
                    bid=bid, uid=request.user.id).delete()
            else:
                return JsonResponse({'status': 'denied', 'message': 'not in block'}, status=200)
            return JsonResponse({'status': 'success', 'message': 'success leave block'}, status=200)
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


def get_block_requests(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            user_requests = []
            blocks = BlockUserStatusChange.objects.filter(
                status='pending', bid=get_user_block(request.user.id))
            for block in blocks:
                # check if request.user have approved this user
                if Blockjoinapprove.objects.filter(bid=block.bid, uid=block.uid.id, approve_uid=request.user.id).first():
                    continue
                user_requests.append({
                    'id': block.uid.id,
                    'username': block.uid.username,
                    'image_url': block.uid.image_url, })
            return JsonResponse({'requests': user_requests}, status=200)
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)
    return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)


# check if user can join in block
def check_join(uid, bid):
    user_already_in_block = UserInBlock.objects.filter(bid=bid)
    user_approve = Blockjoinapprove.objects.filter(bid=bid, uid=uid)
    print('user_already_in_block', user_already_in_block.count())
    print('user_approve', user_approve.count())
    # no user in block now, uid can join
    if not user_already_in_block:
        return True
    # user num less than 3
    if user_already_in_block.count() < 3:
        if user_approve.count() == user_already_in_block.count():
            return True
        return False
    # user num more than 3
    if user_approve.count() >= 3:
        return True
    return False


def user_join_block(uid, bid):
    if check_join(uid, bid):
        user = UsersCustomuser.objects.filter(id=uid).first()
        block = Block.objects.filter(bid=bid).first()
        UserInBlock.objects.create(
            bid=block, uid=user, date_joined=datetime.date.today())
        bu = BlockUserStatusChange.objects.filter(
            bid=bid, uid=uid).first()
        bu.status = 'join'
        bu.date = datetime.date.today()
        bu.save()
        Blockjoinapprove.objects.filter(bid=bid, uid=uid).delete()


def approve_block_request(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            uid = data.get('id', None)
            bid = get_user_block(request.user.id)

            user = UsersCustomuser.objects.filter(id=uid).first()
            approve_user = UsersCustomuser.objects.filter(
                id=request.user.id).first()
            block = Block.objects.filter(bid=bid).first()
            if user is None or block is None:
                return JsonResponse({'status': 'denied', 'message': 'user or block not exist'}, status=200)
            approve = Blockjoinapprove.objects.filter(
                bid=bid, uid=uid, approve_uid=request.user.id).first()
            if approve is None:
                Blockjoinapprove.objects.create(
                    bid=block, uid=user, approve_uid=approve_user)
                user_join_block(uid, bid)
                return JsonResponse({'status': 'success', 'message': 'success approved'}, status=200)
            user_join_block(uid, bid)
            return JsonResponse({'status': 'denied', 'message': 'already approved'}, status=200)
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)


# SQL version
def get_all_blocks_sql(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            with connection.cursor() as cursor:
                cursor.execute("SELECT bid, block_name FROM block")
                rows = cursor.fetchall()
                user_blocks = [{'id': row[0], 'name': row[1]} for row in rows]
                return JsonResponse({'blocks': user_blocks}, status=200)
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)
    return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)


def now_block_sql(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            with connection.cursor() as cursor:
                cursor.execute("SELECT block.bid, block_name FROM user_in_block INNER JOIN block ON user_in_block.bid = block.bid WHERE uid = %s LIMIT 1", [request.user.id])
                row = cursor.fetchone()
                if row is None:
                    return JsonResponse({'status': False, 'message': 'not in any block'}, status=200)
                else:
                    return JsonResponse({'status': True, 'message': 'in block', 'block_name': row[1], 'bid': row[0]}, status=200)
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)
    return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)


def all_follow_block_sql(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT bf.bid, b.block_name FROM user_follow_block bf INNER JOIN block b ON bf.bid = b.bid WHERE bf.uid = %s",
                    [request.user.id]
                )
                rows = cursor.fetchall()
                user_blocks = [{'id': row[0], 'name': row[1]} for row in rows]
                return JsonResponse({'blocks': user_blocks}, status=200)
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)
    return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)


def follow_block_sql(request):
    print(request.method)
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            block_name = data.get('block_name', None)
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM block WHERE block_name = %s
                """, [block_name])
                bk = cursor.fetchone()

            
            if bk:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT * FROM block_user_status_change 
                        WHERE bid = %s AND uid = %s
                    """, [bk[0], request.user.id])
                    block = cursor.fetchone()
                
                if not block:
                    
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute("""
                            INSERT INTO block_user_status_change (bid, uid, status, date) 
                            VALUES (%s, %s, 'follow', %s)
                        """, [bk[0], request.user.id, datetime.date.today()])
                    except Exception as e:
                        print(e)
                    

                    print('block', block)
                    
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO user_follow_block (bid, uid, date_followed) 
                            VALUES (%s, %s, %s)
                        """, [bk[0], request.user.id, datetime.date.today()])
                    
                    return JsonResponse({'status': 'success', 'message': 'success followed block'}, status=200)
                else:
                    if block[3] == 'follow':
                        return JsonResponse({'status': 'denied', 'message': 'already followed block'}, status=200)
                    elif block[3] == 'join':
                        return JsonResponse({'status': 'denied', 'message': 'already joined block'}, status=200)
                    elif block[3] == 'pending':
                        return JsonResponse({'status': 'denied', 'message': 'You have already asked for join!'}, status=200)
            else:
                return JsonResponse({'error': 'Block not found'}, status=404)
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


def apply_block_sql(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            block_name = data.get('block_name', None)
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM block WHERE block_name = %s", [block_name])
                bk = cursor.fetchone()
                if bk:
                    # check if user already in block
                    cursor.execute("SELECT * FROM user_in_block WHERE uid = %s", [request.user.id])
                    bk_join = cursor.fetchone()
                    if bk_join:
                        return JsonResponse({'status': 'denied', 'message': 'already in block'}, status=200)
                    
                    # check if user already applied to join another block
                    cursor.execute("SELECT * FROM block_user_status_change WHERE uid = %s AND status = 'pending' AND bid != %s", [request.user.id, bk[0]])
                    bk_pending = cursor.fetchone()
                    if bk_pending:
                        return JsonResponse({'status': 'denied', 'message': 'already applied to join another block'}, status=200)

                    # check user status
                    cursor.execute("SELECT * FROM block_user_status_change WHERE bid = %s AND uid = %s", [bk[0], request.user.id])
                    block = cursor.fetchone()
                    if not block:
                        cursor.execute("INSERT INTO block_user_status_change (bid, uid, status, date) VALUES (%s, %s, %s, %s)", [bk[0], request.user.id, 'pending', datetime.date.today()])
                        user_join_block(request.user.id, bk[0])
                    else:
                        if block[3] == 'follow':
                            cursor.execute("UPDATE block_user_status_change SET status = 'pending', date = %s WHERE bid = %s AND uid = %s", [datetime.date.today(), bk[0], request.user.id])
                            user_join_block(request.user.id, bk[0])
                            return JsonResponse({'status': 'success', 'message': 'You followed block before, Now you want to join it'}, status=200)
                        elif block[3] == 'join':
                            return JsonResponse({'status': 'denied', 'message': 'already joined block'}, status=200)
                        elif block[3] == 'pending':
                            return JsonResponse({'status': 'denied', 'message': 'You have already asked to join!'}, status=200)
                        elif block[3] == 'leave':
                            cursor.execute("UPDATE block_user_status_change SET status = 'pending', date = %s WHERE bid = %s AND uid = %s", [datetime.date.today(), bk[0], request.user.id])
                            user_join_block(request.user.id, bk[0])
                            return JsonResponse({'status': 'success', 'message': 'You left block before, Now you want to join it'}, status=200)
                    return JsonResponse({'status': 'success', 'message': 'Successfully applied to join block'}, status=200)
                else:
                    return JsonResponse({'error': 'Block not found'}, status=404)
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


def leave_block_sql(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT bid FROM user_in_block WHERE uid = %s", [request.user.id]
                )
                row = cursor.fetchone()
                if not row:
                    return JsonResponse({'status': 'denied', 'message': 'not in any block'}, status=200)
                
                bid = row[0]

                cursor.execute(
                    "SELECT status FROM block_user_status_change WHERE bid = %s AND uid = %s", [bid, request.user.id]
                )
                bs_row = cursor.fetchone()
                if not bs_row:
                    return JsonResponse({'status': 'denied', 'message': 'no data in database'}, status=200)

                bs_status = bs_row[0]
                if bs_status == 'follow':
                    return JsonResponse({'status': 'denied', 'message': 'you are following this block, not in block'}, status=200)
                elif bs_status == 'join':
                    cursor.execute(
                        "UPDATE block_user_status_change SET status = 'leave', date = %s WHERE bid = %s AND uid = %s", [datetime.date.today(), bid, request.user.id]
                    )
                    cursor.execute(
                        "DELETE FROM user_in_block WHERE bid = %s AND uid = %s", [bid, request.user.id]
                    )
                elif bs_status == 'pending':
                    return JsonResponse({'status': 'denied', 'message': 'not in block, now status is pending'}, status=200)
                else:
                    return JsonResponse({'status': 'denied', 'message': 'not in block'}, status=200)
                return JsonResponse({'status': 'success', 'message': 'success leave block'}, status=200)
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


def get_block_requests_sql(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            user_requests = []

            # Raw SQL query to fetch block requests
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 
                        DISTINCT u.id,
                        u.username,
                        u.image_url
                    FROM 
                        users_customuser u
                    INNER JOIN 
                        block_user_status_change b ON u.id = b.uid
                    LEFT JOIN 
                        blockjoinapprove a ON b.bid = a.bid AND u.id = a.uid
                    WHERE 
                        b.status = 'pending'
                    AND 
                        b.bid = %s
                    AND 
                        (a.auto_id IS NULL OR a.approve_uid != %s)
                    """,
                    [get_user_block(request.user.id), request.user.id]
                )
                rows = cursor.fetchall()

                for row in rows:
                    user_requests.append({
                        'id': row[0],
                        'username': row[1],
                        'image_url': row[2],
                    })

            return JsonResponse({'requests': user_requests}, status=200)
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)
    return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)


def approve_block_request_sql(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            uid = data.get('id', None)
            bid = get_user_block(request.user.id)

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * 
                    FROM users_customuser 
                    WHERE id = %s
                    """,
                    [uid]
                )
                user = cursor.fetchone()

                cursor.execute(
                    """
                    SELECT * 
                    FROM block 
                    WHERE bid = %s
                    """,
                    [bid]
                )
                block = cursor.fetchone()

                cursor.execute(
                    """
                    SELECT * 
                    FROM blockjoinapprove 
                    WHERE bid = %s AND uid = %s AND approve_uid = %s
                    """,
                    [bid, uid, request.user.id]
                )
                approve = cursor.fetchone()

                if user is None or block is None:
                    return JsonResponse({'status': 'denied', 'message': 'user or block not exist'}, status=200)

                if approve is None:
                    cursor.execute(
                        """
                        INSERT INTO blockjoinapprove (bid, uid, approve_uid)
                        VALUES (%s, %s, %s)
                        """,
                        [bid, uid, request.user.id]
                    )
                    user_join_block(uid, bid)
                    return JsonResponse({'status': 'success', 'message': 'success approved'}, status=200)

                user_join_block(uid, bid)
                return JsonResponse({'status': 'denied', 'message': 'already approved'}, status=200)
        else:
            return JsonResponse({'error': 'not authenticated user'}, status=401)
