from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import MyUser


class MyUserCreationForm(UserCreationForm):

    class Meta:
        model = MyUser
        fields = ("email", "name")


class MyUserChangeForm(UserChangeForm):

    class Meta:
        model = MyUser
        fields = ("email", "name")
