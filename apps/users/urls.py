from django.urls import path
from .views import (
    RegisterView,
    VerifyOTPView,
    ResendOTPView,
    LoginView,
    MeView,
    CheckEmailView,
)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('verify-otp/', VerifyOTPView.as_view()),
    path('resend-otp/', ResendOTPView.as_view()),
    path('login/', LoginView.as_view()),
    path('me/', MeView.as_view()),
    path('check-email/', CheckEmailView.as_view()),
]
