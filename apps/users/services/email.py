from email.mime.image import MIMEImage
from email.utils import make_msgid
from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.mail.message import SafeMIMEMultipart
from django.template.loader import render_to_string


VERIFICATION_EMAIL_SUBJECT = 'KneeGuide | Email Verification Code'
LOGO_CONTENT_ID_PREFIX = 'kneeguide-logo'
LOGO_CONTENT_ID_DOMAIN = 'kneeguide.email'
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


class RelatedInlineImageEmail(EmailMultiAlternatives):
    """Build the client-friendly alternative/related MIME hierarchy.

    Django's default attachment pipeline puts ``multipart/alternative``
    inside a root ``multipart/related`` container. Some clients don't
    resolve a CID image from HTML nested at that level. This specialized
    message makes the HTML and image direct siblings inside ``related``,
    while keeping plain text as the first alternative.
    """

    def _create_message(self, msg):
        encoding = self.encoding or settings.DEFAULT_CHARSET
        alternative = SafeMIMEMultipart(
            _subtype='alternative', encoding=encoding
        )
        alternative.attach(msg)

        related = SafeMIMEMultipart(
            _subtype='related', encoding=encoding, type='text/html'
        )
        for item in self.alternatives:
            related.attach(
                self._create_mime_attachment(item.content, item.mimetype)
            )
        for attachment in self.attachments:
            related.attach(attachment)

        alternative.attach(related)
        return alternative


def build_otp_email(recipient_email, otp_code):
    logo_content_id = make_msgid(
        idstring=LOGO_CONTENT_ID_PREFIX,
        domain=LOGO_CONTENT_ID_DOMAIN,
    )
    context = {
        'otp_code': otp_code,
        'logo_content_id': logo_content_id[1:-1],
        **_expiry_context(),
    }
    text_body = render_to_string(
        'users/emails/verification_code.txt', context
    ).strip()
    html_body = render_to_string(
        'users/emails/verification_code.html', context
    )

    message = RelatedInlineImageEmail(
        subject=VERIFICATION_EMAIL_SUBJECT,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email],
    )
    message.attach_alternative(html_body, 'text/html')

    logo = MIMEImage(LOGO_PATH.read_bytes(), _subtype='png')
    logo.add_header('Content-ID', logo_content_id)
    logo.add_header('X-Attachment-Id', logo_content_id[1:-1])
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
