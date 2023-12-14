from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

#This class inherits from Django's ModelBackend. It overrides certain methods to customize authentication behavior.
class CustomUserBackend(ModelBackend):
    #authenticate a user based on their email and password.
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(email=username)  # Change this to email if you use email for authentication
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
    #retrieving a user instance based on their user_id.
    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
