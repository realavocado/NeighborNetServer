import re

from django.db.models import Q
from django.http import HttpResponse
from django.http import JsonResponse
from django.db import connection
from .models import Message, Thread, UsersCustomuser, \
    Block, Hood, \
    Threadvisibletoblock, Threadvisibletohood, Threadvisibletouser, UserInBlock
from userRela.models import Friend
from .utils import get_user_block, get_user_hood, get_threads_tuples, \
    get_user_follow_block, get_threads_tuples_sql, get_user_block_sql, \
    get_user_hood_sql, get_user_follow_block_sql
import json
import datetime
import pytz


# Create your views here.


def test(request):
    c = UsersCustomuser.objects.all()
    serialized_threads = []
    for i in c:
        serialized_threads.append({
            'id': i.id,
            'username': i.username,
            'image_url': i.image_url,
        })
    return JsonResponse({'message': serialized_threads}, safe=False)


def get_all_message(request):
    # Query all messages from the Message model
    # current_user_id = request.user.id
    # print(current_user_id)
    threads = Thread.objects.all()

    # Serialize the queryset into JSON
    serialized_threads = []
    for thread in threads:
        related_messages = []
        first_message = Message.objects.filter(
            tid=thread.tid, reply_to_mid__isnull=True).first()
        reply_messages = Message.objects.filter(
            tid=thread.tid).exclude(reply_to_mid__isnull=True)

        if not first_message:
            continue

        for message in reply_messages:
            related_messages.append({
                'id': message.mid,
                'author_id': message.author_id.id,
                'author': message.author_id.username,
                'title': message.title,
                'text': message.text,
                'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'latitude': message.latitude,
                'longitude': message.longitude,
                'reply_to_username': message.reply_to_mid.author_id.username if message.reply_to_mid else '',
                'image_url': message.author_id.image_url,
                # Add more fields as needed
            })

        # print(related_messages)
        # print(first_message)

        serialized_threads.append({
            # thread
            'tid': thread.tid,
            'topic': thread.topic,
            'subject': thread.subject,
            'visibility': thread.visibility,
            # first message
            'mid': first_message.mid,
            'title': first_message.title,
            'text': first_message.text,
            'author_id': first_message.author_id.id,
            'author': first_message.author_id.username,
            'timestamp': first_message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'latitude': first_message.latitude,
            'longitude': first_message.longitude,
            'image_url': first_message.author_id.image_url,
            # related messages
            'related_messages': json.dumps(related_messages),
        })

    # Return JSON response
    return JsonResponse({'message': serialized_threads}, safe=False)


def get_all_message_sql(request):
    sql = '''
    SELECT m.*, t.topic, t.subject, t.visibility, a.username, a.image_url
    FROM message m
    INNER JOIN thread t ON m.tid = t.tid
    INNER JOIN users_customuser a ON m.author_id = a.id
    WHERE m.reply_to_mid IS NULL
    ORDER BY m.mid DESC
    '''

    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()

    serialized_threads = []
    for row in rows:
        mid, tid, reply_to_mid, title, text, timestamp, latitude, longitude, author_id, topic, subject, visibility, username, image_url = row
        serialized_thread = {
            'tid': tid,
            'topic': topic,
            'subject': subject,
            'visibility': visibility,
            'mid': mid,
            'title': title,
            'text': text,
            'author_id': author_id,
            'author': username,
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'latitude': latitude,
            'longitude': longitude,
            'image_url': image_url,
            'related_messages': []  # Additional SQL required to populate this
        }
        serialized_threads.append(serialized_thread)

    return JsonResponse({'message': serialized_threads}, safe=False)


def get_message(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            # if True:
            # print('id',request.user.id)
            # print('username',request.user.username)
            userid = request.user.id
            # userid = 1

            serialized_threads = []

            # Query all threads that user write
            threads_writer = Thread.objects.filter(
                author_id=userid).order_by('-tid')
            serialized_threads += get_threads_tuples(threads_writer, True)

            # Query all threads that in user's block but not write by user
            if get_user_block(userid):
                threads_joinBlock = Thread.objects.filter(
                    visibility='block',
                    threadvisibletoblock__bid=get_user_block(userid)) \
                    .exclude(author_id=userid).order_by('-tid')
                serialized_threads += get_threads_tuples(
                    threads_joinBlock, True)

            # Query all threads that in user's hood but not write by user
            if get_user_hood(userid):
                threads_joinHood = Thread.objects.filter(
                    visibility='neighborhood',
                    threadvisibletohood__hid=get_user_hood(userid)) \
                    .exclude(author_id=userid).order_by('-tid')
                serialized_threads += get_threads_tuples(
                    threads_joinHood, True)

            # Query all threads that private to the user but not write by user
            threads_private = Thread.objects.filter(
                visibility='private',
                threadvisibletouser__uid=userid) \
                .exclude(author_id=userid).order_by('-tid')
            serialized_threads += get_threads_tuples(threads_private, True)

            # Query all threads that user follow other Block
            if get_user_follow_block(userid):
                threads_follow = Thread.objects.filter(
                    visibility='block',
                    threadvisibletoblock__bid__in=get_user_follow_block(userid)) \
                    .exclude(author_id=userid).order_by('-tid')
                serialized_threads += get_threads_tuples(threads_follow, False)

            # Return JSON response
            return JsonResponse({'message': serialized_threads}, safe=False)
        else:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
    else:
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)


def get_message_with_keywords(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            user_id = request.user.id
            try:
                # data = json.loads(request.body)
                keyword = request.GET.get('keyword', '')
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)

            if not keyword:
                return JsonResponse({'error': 'Missing "keyword" field'}, status=400)

            # query 1：private messages from another user
            messages_by_tvu = Message.objects.filter(
                tid__in=Threadvisibletouser.objects.filter(uid=user_id).values('tid'),
                text__icontains=keyword
            )

            # query 2：messages from the block
            messages_by_tvb = Message.objects.filter(
                tid__in=Threadvisibletoblock.objects.filter(
                    bid__in=UserInBlock.objects.filter(uid=user_id).values('bid')
                ).values('tid'),
                text__icontains=keyword
            )

            # query 4：messages from the hood
            messages_by_tvh = Message.objects.filter(
                tid__in=Threadvisibletohood.objects.filter(
                    hid__in=Block.objects.filter(
                        bid__in=UserInBlock.objects.filter(uid=user_id).values('bid')
                    ).values('hid')
                ).values('tid'),
                text__icontains=keyword
            )

            # query 4：messages from friends
            messages_from_friends = Message.objects.filter(
                tid__in=Thread.objects.filter(
                    author_id__in=Friend.objects.filter(uid=user_id).values('fid'),
                    visibility='friends'
                ).values('tid'),
                text__icontains=keyword
            )

            # union all query results
            messages = messages_by_tvu.union(
                messages_by_tvb,
                messages_by_tvh,
                messages_from_friends
            )

            message_list = list(messages.values())
            return JsonResponse(message_list, safe=False)
        else:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
    else:
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)


def post_message(request):
    eastern = pytz.timezone('America/New_York')
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            tid = data.get('tid', None)
            reply_to_mid = data.get('reply_to_mid', None)
            title = data.get('title', '')
            text = data.get('text', '')
            latitude = data.get('latitude', None)
            longitude = data.get('longitude', None)

            if tid:
                author_id = request.user.id
                usr = UsersCustomuser.objects.filter(id=author_id).first()
                if tid:
                    tid = Thread.objects.filter(tid=tid).first()
                if reply_to_mid:
                    reply_to_mid = Message.objects.filter(
                        mid=reply_to_mid).first()
                message = Message.objects.create(
                    title=title, text=text, latitude=latitude, longitude=longitude,
                    author_id=usr, reply_to_mid=reply_to_mid, tid=tid, timestamp=datetime.datetime.now(eastern))
                return JsonResponse(
                    {'id': message.mid, 'title': message.title, 'text': message.text, 'latitude': message.latitude,
                     'longitude': message.longitude, 'author_id': message.author_id.id,
                     'reply_to_mid': message.reply_to_mid.mid if message.reply_to_mid else None,
                     'tid': message.tid.tid if message.tid else None, 'created_at': message.timestamp})
            else:
                return JsonResponse({'error': 'Title and text are required'}, status=400)
        return JsonResponse({'error': 'User not authenticated'}, status=401)
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


def post_thread(request):
    eastern = pytz.timezone('America/New_York')
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            # create a new thread
            topic = data.get('title', '')
            subject = data.get('subject', '')
            author_id = request.user.id
            visibility = data.get('visibility', '')
            receiver_id = data.get('receiver', None)
            if visibility in ['friend', 'neighbor']:
                visibility = 'private'

            usr = UsersCustomuser.objects.filter(id=author_id).first()
            thread = Thread.objects.create(
                topic=topic, subject=subject, visibility=visibility, author_id=usr)

            if visibility == 'private' and receiver_id:
                receiver = UsersCustomuser.objects.filter(
                    id=receiver_id).first()
                tu = Threadvisibletouser.objects.create(
                    tid=thread, uid=receiver)
            if visibility == 'block':
                block = Block.objects.filter(
                    bid=get_user_block(author_id)).first()
                tb = Threadvisibletoblock.objects.create(tid=thread, bid=block)
            if visibility == 'neighborhood':
                hood = Hood.objects.filter(
                    hid=get_user_hood(author_id)).first()
                th = Threadvisibletohood.objects.create(tid=thread, hid=hood)

            # create a new message
            title = data.get('title', '')
            text = data.get('text', '')
            latitude = data.get('latitude', None)
            longitude = data.get('longitude', None)
            date = data.get('date', None)
            time = data.get('time', None)
            timestamp = datetime.datetime.now(eastern)
            if date and time:
                timestamp = datetime.datetime.strptime(
                    date + ' ' + time, '%Y-%m-%d %H:%M')
            message = Message.objects.create(
                title=title, text=text, latitude=latitude, longitude=longitude,
                author_id=usr, tid=thread, timestamp=timestamp)
            return JsonResponse(
                {'tid': thread.tid, 'topic': thread.topic, 'subject': thread.subject, 'visibility': thread.visibility,
                 'author_id': thread.author_id.id})
        return JsonResponse({'error': 'User not authenticated'}, status=401)
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


# SQL version
def get_message_sql(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            userid = request.user.id
            serialized_threads = []

            # SQL to get threads by the user
            sql = '''
            SELECT *
            FROM thread WHERE author_id = %s ORDER BY tid DESC
            '''
            with connection.cursor() as cursor:
                cursor.execute(sql, [userid])
                threads_writer = cursor.fetchall()
                serialized_threads += get_threads_tuples_sql(threads_writer, True)

            # print(serialized_threads)


            # Add more SQL queries for threads in user's block, hood, and private threads
            # Example for threads in user's block:
            block_id = get_user_block_sql(userid)
            if block_id:
                sql = '''
                SELECT * 
                FROM thread 
                INNER JOIN threadvisibletoblock ON thread.tid = threadvisibletoblock.tid
                WHERE visibility = 'block' 
                AND threadvisibletoblock.bid = %s 
                AND author_id != %s ORDER BY thread.tid DESC
                '''
                with connection.cursor() as cursor:
                    cursor.execute(sql, [block_id, userid])
                    threads_block = cursor.fetchall()
                    serialized_threads += get_threads_tuples_sql(threads_block, True)

            # Query all threads in the user's hood but not written by the user
            hood_id = get_user_hood_sql(userid)  # This should return the hood ID for the user
            if hood_id:
                sql_hood = '''
                SELECT *
                FROM thread
                JOIN threadvisibletohood ON thread.tid = threadvisibletohood.tid
                WHERE visibility = 'neighborhood' AND threadvisibletohood.hid = %s AND author_id != %s
                ORDER BY thread.tid DESC
                '''
                with connection.cursor() as cursor:
                    cursor.execute(sql_hood, [hood_id, userid])
                    threads_hood = cursor.fetchall()
                    serialized_threads += get_threads_tuples_sql(threads_hood, True)


            # Query all private threads visible to the user but not written by the user
            sql_private = '''
            SELECT *
            FROM thread
            JOIN threadvisibletouser ON thread.tid = threadvisibletouser.tid
            WHERE visibility = 'private' AND threadvisibletouser.uid = %s AND author_id != %s
            ORDER BY thread.tid DESC
            '''
            with connection.cursor() as cursor:
                cursor.execute(sql_private, [userid, userid])
                threads_private = cursor.fetchall()
                serialized_threads += get_threads_tuples_sql(threads_private, True)

            # Query all threads that user follows in other blocks
            if get_user_follow_block_sql(userid):
                print(tuple(get_user_follow_block_sql(userid)))
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT t.* 
                        FROM thread t
                        INNER JOIN threadvisibletoblock tb ON t.tid = tb.tid
                        WHERE t.visibility = 'block' 
                        AND tb.bid IN (
                            SELECT bid FROM user_follow_block WHERE uid = %s
                        )
                        AND t.author_id != %s 
                        ORDER BY t.tid DESC
                    """, [userid, userid])
                    
                    threads_follow = cursor.fetchall()
                    serialized_threads += get_threads_tuples_sql(threads_follow, False)

            return JsonResponse({'message': serialized_threads}, safe=False)
        else:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
    else:
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)


def get_message_with_keywords_sql(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            user_id = request.user.id
            keyword = request.GET.get('keyword', '')

            if not keyword:
                return JsonResponse({'error': 'Missing "keyword" field'}, status=400)

            query = """
            WITH
            messages_by_myself AS (
                SELECT m.*, u.username, u.image_url FROM Message m
                JOIN Users_Customuser u ON m.author_id = u.id
                WHERE m.author_id = %s AND (m.text ILIKE %s OR m.title ILIKE %s)
             ),
            messages_by_tvu AS (
                SELECT m.*, u.username, u.image_url FROM Message m
                JOIN Threadvisibletouser t ON m.tid = t.tid
                JOIN Users_Customuser u ON m.author_id = u.id
                WHERE t.uid = %s AND (m.text ILIKE %s OR m.title ILIKE %s)
            ),
            messages_by_tvb AS (
                SELECT m.*, u.username, u.image_url FROM Message m
                JOIN Threadvisibletoblock t ON m.tid = t.tid
                JOIN User_In_Block ub ON t.bid = ub.bid
                JOIN Users_Customuser u ON m.author_id = u.id
                WHERE ub.uid = %s AND (m.text ILIKE %s OR m.title ILIKE %s)
            ),
            messages_by_tvh AS (
                SELECT m.*, u.username, u.image_url FROM Message m
                JOIN Threadvisibletohood t ON m.tid = t.tid
                JOIN Block b ON t.hid = b.hid
                JOIN User_In_Block ub ON b.bid = ub.bid
                JOIN Users_Customuser u ON m.author_id = u.id
                WHERE ub.uid = %s AND (m.text ILIKE %s OR m.title ILIKE %s)
            ),
            messages_from_friends AS (
                SELECT m.*, u.username, u.image_url FROM Message m
                JOIN Thread t ON m.tid = t.tid
                JOIN Friend f ON t.author_id = f.fid
                JOIN Users_Customuser u ON m.author_id = u.id
                WHERE f.uid = %s AND t.visibility = 'friends' AND (m.text ILIKE %s OR m.title ILIKE %s)
            )
            SELECT * FROM messages_by_myself
            UNION
            SELECT * FROM messages_by_tvu
            UNION
            SELECT * FROM messages_by_tvb
            UNION
            SELECT * FROM messages_by_tvh
            UNION
            SELECT * FROM messages_from_friends;
            """

            # Preparing parameters for the query
            params = [user_id, f"%{keyword}%", f"%{keyword}%", user_id, f"%{keyword}%", f"%{keyword}%", user_id, f"%{keyword}%", f"%{keyword}%", user_id, f"%{keyword}%", f"%{keyword}%", user_id, f"%{keyword}%", f"%{keyword}%"]

            with connection.cursor() as cursor:
                cursor.execute(query, params)
                columns = [col[0] for col in cursor.description]
                message_list = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return JsonResponse(message_list, safe=False)
        else:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
    else:
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)


def post_message_sql(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            title = data.get('title', '')
            text = data.get('text', '')
            tid = data.get('tid', None)
            reply_to_mid = data.get('reply_to_mid', None)
            latitude = data.get('latitude', None)
            longitude = data.get('longitude', None)
            timestamp = datetime.datetime.now(pytz.timezone('America/New_York'))

            # check if the thread exists
            if tid:
                sql_tid = '''
                SELECT * FROM thread WHERE tid = %s
                '''
                with connection.cursor() as cursor:
                    cursor.execute(sql_tid, [tid])
                    thread = cursor.fetchone()
                    if not thread:
                        return JsonResponse({'error': 'Thread not found'}, status=404)
            else:
                return JsonResponse({'error': 'Thread ID is required'}, status=400)

            sql = '''
            INSERT INTO message (title, text, tid, reply_to_mid, latitude, longitude, author_id, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING mid
            '''
            with connection.cursor() as cursor:
                cursor.execute(sql, [title, text, tid, reply_to_mid, latitude, longitude, request.user.id, timestamp])
                mid = cursor.fetchone()

            return JsonResponse({'id': mid, 'title': title, 'text': text, 'latitude': latitude, 'longitude': longitude,
                                 'author_id': request.user.id, 'reply_to_mid': reply_to_mid, 'tid': tid,
                                 'timestamp': timestamp})
        else:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


def post_thread_sql(request):
    eastern = pytz.timezone('America/New_York')
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            topic = data.get('title', '')
            subject = data.get('subject', '')
            author_id = request.user.id
            visibility = data.get('visibility', '')
            receiver_id = data.get('receiver', None)
            title = data.get('title', '')
            text = data.get('text', '')
            latitude = data.get('latitude', None)
            longitude = data.get('longitude', None)
            date = data.get('date', None)
            time = data.get('time', None)

            timestamp = datetime.datetime.now(eastern)
            if date and time:
                timestamp = datetime.datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M')

            if visibility in ['friend', 'neighbor']:
                visibility = 'private'

            # Insert the new thread
            sql_thread = '''
            INSERT INTO thread (topic, subject, visibility, author_id)
            VALUES (%s, %s, %s, %s)
            RETURNING tid
            '''
            with connection.cursor() as cursor:
                cursor.execute(sql_thread, [topic, subject, visibility, author_id])
                tid = cursor.fetchone()[0]  # Get the thread ID from the INSERT

            # Handling visibility to specific user, block, or neighborhood
            if visibility == 'private' and receiver_id:
                sql_private = '''
                INSERT INTO threadvisibletouser (tid, uid)
                VALUES (%s, %s)
                '''
                with connection.cursor() as cursor:
                    cursor.execute(sql_private, [tid, receiver_id])

            if visibility == 'block':
                block_id = get_user_block_sql(author_id)  # Assuming this function fetches the block ID
                if block_id:
                    sql_block = '''
                    INSERT INTO threadvisibletoblock (tid, bid)
                    VALUES (%s, %s)
                    '''
                    with connection.cursor() as cursor:
                        cursor.execute(sql_block, [tid, block_id])

            if visibility == 'neighborhood':
                hood_id = get_user_hood_sql(author_id)  # Assuming this function fetches the hood ID
                if hood_id:
                    sql_hood = '''
                    INSERT INTO threadvisibletohood (tid, hid)
                    VALUES (%s, %s)
                    '''
                    with connection.cursor() as cursor:
                        cursor.execute(sql_hood, [tid, hood_id])

            # Create a new message
            sql_message = '''
            INSERT INTO message (title, text, latitude, longitude, author_id, tid, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING mid
            '''
            with connection.cursor() as cursor:
                cursor.execute(sql_message, [title, text, latitude, longitude, author_id, tid, timestamp])
                mid = cursor.fetchone()[0]  # Get the message ID from the INSERT

            return JsonResponse(
                {'tid': tid, 'topic': topic, 'subject': subject, 'visibility': visibility, 'author_id': author_id,
                 'mid': mid})
        else:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
