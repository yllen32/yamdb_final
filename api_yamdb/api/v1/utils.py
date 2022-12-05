from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import default_token_generator

from api_yamdb.settings import DEFAULT_FROM_EMAIL


def send_confirmation_mail(email, code):
    """Send confirmation mail to mentionde mail with confirmation code."""
    send_mail(
        'Confirmation code',
        'Application for registration on the yam_db service '
        'has been received from your email address. If it is not you, '
        f'ignore the message. There is your conformation code: {code}',
        DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )


def get_confirmation_code(user):
    """Generate confirmation code."""
    return default_token_generator.make_token(user)


def get_tokens_for_user(user):
    """Get token for user."""
    refresh = RefreshToken.for_user(user)

    return {
        'access': str(refresh.access_token),
    }
