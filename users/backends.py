from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import MultipleObjectsReturned


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user_model = get_user_model()
        email = username.lower()
        try:
            user = user_model.objects.get(email=email)
            if user.check_password(password):
                return user
        except user_model.DoesNotExist:
            return None
        except MultipleObjectsReturned:
            return user_model.objects.filter(email=email).order_by('id').first()
        return None
