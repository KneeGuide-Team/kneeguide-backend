from django.db import models
from django.contrib.auth import get_user_model
from apps.exercises.models import Exercise

User = get_user_model()


class ExerciseReport(models.Model):

    RATING_CHOICES = (
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('poor', 'Poor'),
    )

    STATUS_CHOICES = (
        ('completed', 'Completed'),
        ('missed', 'Missed'),
    )

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    exercise = models.ForeignKey(Exercise, on_delete=models.SET_NULL, null=True, related_name='reports')

    # Motion analysis
    motion_data = models.JSONField()   # [{timestamp, angle}]

    max_angle = models.FloatField(null=True, blank=True)
    normal_angle = models.FloatField(default=135)
    deviation = models.FloatField(null=True, blank=True)
    performance_status = models.CharField(max_length=50, null=True, blank=True)

    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(default=0)

    # Manual doctor evaluation
    rating = models.CharField(max_length=20, choices=RATING_CHOICES, null=True, blank=True)
    doctor_notes = models.TextField(null=True, blank=True)

    # Exercise status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.patient.email}"
