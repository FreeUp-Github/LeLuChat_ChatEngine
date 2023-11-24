from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import time

@shared_task
def send_mail(email, name, key):
    context = {
        'current_user': email,
        'name': name,
        'email': email,
        'reset_password_url': "{}?token={}".format(settings.FRONTEND_RESET_PASSWORD_URL, key)
    }

    # render email text
    email_html_message = render_to_string('email/password_reset_email.html', context)
    email_plaintext_message = render_to_string('email/password_reset_email.txt', context)

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="LeLeChat"),
        # message:
        email_html_message,
        # from:
        "noreply@LeLuChat.com",
        # to:
        [email]
    )
    msg.attach_alternative(email_plaintext_message, "text/plain")
    msg.send()
