from django.urls import path
from .views import (
    CreateAppointmentView,
    GetAppointmentDetailView,
    UpdateAppointmentView,
    DeleteAppointmentView,
    GetAppointmentsForPatientView,
    GetAppointmentsForDoctorView,
)

urlpatterns = [
    path('create/', CreateAppointmentView.as_view()),
    path('<int:appointment_id>/', GetAppointmentDetailView.as_view()),
    path('<int:appointment_id>/update/', UpdateAppointmentView.as_view()),
    path('<int:appointment_id>/cancel/', DeleteAppointmentView.as_view()),

    path('patient/<int:patient_id>/', GetAppointmentsForPatientView.as_view()),
    path('doctor/<int:doctor_id>/', GetAppointmentsForDoctorView.as_view()),
]
