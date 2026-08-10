from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Appointment(models.Model):
    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="doctor_appointments"
    )
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="patient_appointments"
    )

    date = models.DateField()
    time = models.TimeField()

    reason = models.CharField(max_length=255, null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ("scheduled", "Scheduled"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="scheduled"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # ما عندنا field اسمه name في User، لذلك نستخدم email أو first/last_name
        doctor_name = f"{self.doctor.first_name} {self.doctor.last_name}".strip() or self.doctor.email
        patient_name = f"{self.patient.first_name} {self.patient.last_name}".strip() or self.patient.email
        return f"Appointment #{self.id} - {patient_name} with {doctor_name} on {self.date} {self.time}"
