from .models import UsersCustomuser, Message

def get_username_by_id(user_id):
    user = UsersCustomuser.objects.get(id=user_id)
    return user.username

def get_user_id_by_mid(mid):
    mess = Message.objects.get(mid=mid)
    print(mess)
    return mess.author_id.id

def get_username_by_replymid(mid):
    userid = get_user_id_by_mid(mid)
    username = get_username_by_id(userid)
    return username