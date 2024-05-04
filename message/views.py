from django.http import HttpResponse
from django.http import JsonResponse
from .models import Message, Thread, UsersCustomuser, \
    Block, Hood, \
    Threadvisibletoblock, Threadvisibletohood, Threadvisibletouser
from .utils import get_user_block, get_user_hood, get_threads_tuples, \
    get_user_follow_block
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
                    threadvisibletoblock__bid=get_user_block(userid))\
                    .exclude(author_id=userid).order_by('-tid')
                serialized_threads += get_threads_tuples(
                    threads_joinBlock, True)

            # Query all threads that in user's hood but not write by user
            if get_user_hood(userid):
                threads_joinHood = Thread.objects.filter(
                    visibility='neighborhood',
                    threadvisibletohood__hid=get_user_hood(userid))\
                    .exclude(author_id=userid).order_by('-tid')
                serialized_threads += get_threads_tuples(
                    threads_joinHood, True)

            # Query all threads that private to the user but not write by user
            threads_private = Thread.objects.filter(
                visibility='private',
                threadvisibletouser__uid=userid)\
                .exclude(author_id=userid).order_by('-tid')
            serialized_threads += get_threads_tuples(threads_private, True)

            # Query all threads that user follow other Block
            if get_user_follow_block(userid):
                threads_follow = Thread.objects.filter(
                    visibility='block',
                    threadvisibletoblock__bid__in=get_user_follow_block(userid))\
                    .exclude(author_id=userid).order_by('-tid')
                serialized_threads += get_threads_tuples(threads_follow, False)

            # Return JSON response
            return JsonResponse({'message': serialized_threads}, safe=False)
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
                return JsonResponse({'id': message.mid, 'title': message.title, 'text': message.text, 'latitude': message.latitude, 'longitude': message.longitude, 'author_id': message.author_id.id, 'reply_to_mid': message.reply_to_mid.mid if message.reply_to_mid else None, 'tid': message.tid.tid if message.tid else None, 'created_at': message.timestamp})
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
            print('timestamp', timestamp)
            message = Message.objects.create(
                title=title, text=text, latitude=latitude, longitude=longitude,
                author_id=usr, tid=thread, timestamp=timestamp)
            return JsonResponse({'tid': thread.tid, 'topic': thread.topic, 'subject': thread.subject, 'visibility': thread.visibility, 'author_id': thread.author_id.id})
        return JsonResponse({'error': 'User not authenticated'}, status=401)
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
