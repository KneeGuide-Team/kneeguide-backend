from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


VERIFICATION_EMAIL_SUBJECT = 'KneeGuide | Email Verification Code'


def _expiry_context():
    minutes = settings.OTP_EXPIRY_MINUTES
    english = f'{minutes} minute' if minutes == 1 else f'{minutes} minutes'
    if minutes == 1:
        arabic = 'دقيقة واحدة'
    elif minutes == 2:
        arabic = 'دقيقتين'
    else:
        arabic = f'{minutes} دقائق'
    return {
        'otp_expiry_minutes': minutes,
        'otp_expiry_english': english,
        'otp_expiry_arabic': arabic,
    }


def build_otp_email(recipient_email, otp_code):
    context = {
        'otp_code': otp_code,
        'email_logo_url': settings.EMAIL_LOGO_URL,
        **_expiry_context(),
    }
    text_body = render_to_string(
        'users/emails/verification_code.txt', context
    ).strip()
    html_body = render_to_string(
        'users/emails/verification_code.html', context
    )

    message = EmailMultiAlternatives(
        subject=VERIFICATION_EMAIL_SUBJECT,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email],
    )
    message.attach_alternative(html_body, 'text/html')
    return message


def send_otp_email(recipient_email, otp_code):
    return build_otp_email(recipient_email, otp_code).send()
