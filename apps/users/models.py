from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import date


class User(AbstractUser):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    )

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    dob = models.DateField(null=True, blank=True)

    specialization = models.CharField(max_length=255, blank=True)
    is_available = models.BooleanField(default=True)

    assigned_doctor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patients"
    )

    # لتتبع آخر نشاط للمستخدم (للـ auto logout بعد 5 دقائق سكون)
    last_activity = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    @property
    def age(self):
        if not self.dob:
            return None
        today = date.today()
        return today.year - self.dob.year - (
            (today.month, today.day) < (self.dob.month, self.dob.day)
        )


class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otp_codes")
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    # عدد المحاولات الخاطئة
    attempts = models.IntegerField(default=0)

    def is_expired(self):
        return (
            timezone.now() - self.created_at
        ).total_seconds() > settings.OTP_EXPIRY_MINUTES * 60

    def __str__(self):
        return f"OTP for {self.user.email} - {self.code}"
