from django.contrib import admin
from .models import ExerciseReport


@admin.register(ExerciseReport)
class ExerciseReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient",
        "exercise",
        "max_angle",
        "performance_status",
        "rating",
        "status",
        "created_at",
    )
    list_filter = ("performance_status", "rating", "status", "created_at")
    search_fields = ("patient__email", "exercise__title")
