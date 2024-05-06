from .models import UserInBlock, UserFollowBlock, Block, Message 
import json
from django.db import connection

def get_user_block(uid):
    # return bid of block
    block = UserInBlock.objects.filter(uid=uid).first()
    if block:
        return block.bid.bid
    return None

def get_user_follow_block(uid):
    # return list of bid of block
    blocks = UserFollowBlock.objects.filter(uid=uid)
    if blocks:
        return [block.bid.bid for block in blocks]
    return None
    
def get_user_hood(uid):
    # return hid of hood
    bid = get_user_block(uid)
    if bid:
        hood = Block.objects.filter(bid=bid).first()
        return hood.hid.hid
    return None

def get_threads_tuples(threadObj, isWrite=False):
    # isWrite is a boolean value that indicates whether the user can send message in this thread
    serialized_threads = []
    for thread in threadObj:
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
            'isWrite': isWrite,
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

    return serialized_threads


# SQL version
def get_user_block_sql(uid):
    # return bid of block
    with connection.cursor() as cursor:
        cursor.execute("SELECT bid FROM user_in_block WHERE uid = %s LIMIT 1", [uid])
        row = cursor.fetchone()
        if row:
            return row[0]
    return None

def get_user_follow_block_sql(uid):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT bid FROM user_follow_block WHERE uid = %s",
            [uid]
        )
        rows = cursor.fetchall()
        if rows:
            return [row[0] for row in rows]
    return None

def get_user_hood_sql(uid):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT hid FROM block WHERE bid = (SELECT bid FROM user_in_block WHERE uid = %s)",
            [uid]
        )
        row = cursor.fetchone()
        if row:
            return row[0]
        return None


def find_username_sql(uid):
    sql = '''
        SELECT username
        FROM users_customuser
        WHERE id = %s
        '''
    with connection.cursor() as cursor:
        cursor.execute(sql, [uid])
        username = cursor.fetchone()
    return username[0] if username else None


def find_message_authorid_sql(mid):
    sql = '''
        SELECT author_id
        FROM message
        WHERE mid = %s
        '''
    with connection.cursor() as cursor:
        cursor.execute(sql, [mid])
        author_id = cursor.fetchone()
    return author_id[0] if author_id else None


def find_image_url_sql(uid):
    sql = '''
        SELECT image_url
        FROM users_customuser
        WHERE id = %s
        '''
    with connection.cursor() as cursor:
        cursor.execute(sql, [uid])
        image_url = cursor.fetchone()
    return image_url[0] if image_url else None


def get_threads_tuples_sql(threadObj, isWrite=False):
    # isWrite is a boolean value that indicates whether the user can send message in this thread
    serialized_threads = []
    for thread in threadObj:
        related_messages = []
        tid = thread[0]

        sql = '''
            SELECT *
            FROM message 
            WHERE tid = %s
            AND reply_to_mid IS NULL
            '''
        with connection.cursor() as cursor:
            cursor.execute(sql, [tid])
            first_message = cursor.fetchone()

        if not first_message:
            continue

        sql = '''
            SELECT *
            FROM message 
            WHERE tid = %s
            AND reply_to_mid IS NOT NULL
            ORDER BY timestamp DESC
            '''
        with connection.cursor() as cursor:
            cursor.execute(sql, [tid])
            reply_messages = cursor.fetchall()
        
            for message in reply_messages:
                related_messages.append({
                    'id': message[0],
                    'author_id': message[1],
                    'author': find_username_sql(message[1]),
                    'title': message[4],
                    'text': message[5],
                    'timestamp': message[6].strftime('%Y-%m-%d %H:%M:%S'),
                    'latitude': message[7],
                    'longitude': message[8],
                    'reply_to_username': find_username_sql(find_message_authorid_sql(message[3])) if message[3] else '',
                    'image_url': find_image_url_sql(find_message_authorid_sql(message[3])) if message[3] else '',
                # Add more fields as needed
            })

        # print(related_messages)
        # print(first_message)

        serialized_threads.append({
            # thread
            'tid': thread[0],
            'topic': thread[1],
            'subject': thread[2],
            'visibility': thread[4],
            'isWrite': isWrite,
            # first message
            'mid': first_message[0],
            'title': first_message[4],
            'text': first_message[5],
            'author_id': first_message[1],
            'author': find_username_sql(first_message[1]),
            'timestamp': first_message[6].strftime('%Y-%m-%d %H:%M:%S'),
            'latitude': first_message[7],
            'longitude': first_message[8],
            'image_url': find_image_url_sql(first_message[1]),
            # related messages
            'related_messages': json.dumps(related_messages),
        })

    return serialized_threads