from django_rest_passwordreset.signals import reset_password_token_created
from LeLuChat_ChatEngine import settings
from django.dispatch import receiver
from users.tasks import send_mail

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    send_mail.delay(reset_password_token.user.email, reset_password_token.user.name, reset_password_token.key)
