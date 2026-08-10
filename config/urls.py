from django.contrib import admin
from django.urls import path, include  # ← مهم جداً

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/exercises/', include('apps.exercises.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/appointments/', include('apps.appointments.urls')),

]
