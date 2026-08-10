from email.mime.image import MIMEImage
from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


VERIFICATION_EMAIL_SUBJECT = 'KneeGuide | Email Verification Code'
LOGO_CONTENT_ID = 'kneeguide-logo'
LOGO_PATH = (
    Path(__file__).resolve().parents[1]
    / 'static'
    / 'users'
    / 'email'
    / 'kneeguide-logo.png'
)


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
        'logo_content_id': LOGO_CONTENT_ID,
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

    logo = MIMEImage(LOGO_PATH.read_bytes(), _subtype='png')
    logo.add_header('Content-ID', f'<{LOGO_CONTENT_ID}>')
    logo.add_header(
        'Content-Disposition',
        'inline',
        filename='kneeguide-logo.png',
    )
    message.mixed_subtype = 'related'
    message.attach(logo)
    return message


def send_otp_email(recipient_email, otp_code):
    return build_otp_email(recipient_email, otp_code).send()
