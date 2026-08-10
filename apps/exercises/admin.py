from django.contrib import admin
from .models import Exercise


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "assigned_to", "assigned_by", "created_at")
    list_filter = ("assigned_by", "assigned_to", "created_at")
    search_fields = ("title", "assigned_to__email", "assigned_by__email")
