from .models import UserInBlock, UserFollowBlock, Block, Message 
import json

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