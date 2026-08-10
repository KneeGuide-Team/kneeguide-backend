from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "doctor", "patient", "date", "time", "status", "created_at")
    list_filter = ("status", "date", "doctor")
    search_fields = ("patient__email", "doctor__email")
