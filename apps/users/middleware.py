from datetime import timedelta
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication


class LastActivityMiddleware:
    """
    Middleware يقوم بتحديث آخر نشاط للمستخدم عند كل طلب API.
    - يقرأ المستخدم من JWT
    - إذا التوكن صالح → يحدث last_activity فقط
    - لا يرجع 401 ولا يغلق الجلسة (نسخة Development)
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt = JWTAuthentication()

    def __call__(self, request):
        # نحاول جلب المستخدم من التوكن
        try:
            auth_result = self.jwt.authenticate(request)
            if auth_result:
                user, _ = auth_result
                user.last_activity = timezone.now()
                user.save(update_fields=["last_activity"])
        except Exception:
            pass

        return self.get_response(request)
