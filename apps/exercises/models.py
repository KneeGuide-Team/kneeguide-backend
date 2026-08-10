from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Exercise(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    video_url = models.URLField(null=True, blank=True)  # رفع فيديو لاحقاً عبر Cloudinary
    repetitions = models.IntegerField(default=10)
    sets = models.IntegerField(default=3)
    notes = models.TextField(null=True, blank=True)

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='assigned_exercises'
    )

    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_exercises'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
