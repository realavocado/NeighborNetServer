from .models import UsersCustomuser

def get_username_by_id(user_id):
    user = UsersCustomuser.objects.get(id=user_id)
    return user.username