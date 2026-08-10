"""Backward-compatible user utilities.

The canonical OTP email implementation lives in ``services.email``.
"""

from .services.email import send_otp_email

__all__ = ['send_otp_email']
