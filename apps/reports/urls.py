from django.urls import path
from .views import (
    SubmitReportView,
    GetReportsForPatientView,
    PatientDashboardView,
    DoctorDashboardView,
    UpdateReportByDoctorView,   # ← مهم! أضفناه هنا
)

urlpatterns = [
    path('submit/', SubmitReportView.as_view()),
    path('patient/<int:patient_id>/', GetReportsForPatientView.as_view()),
    path('dashboard/<int:patient_id>/', PatientDashboardView.as_view()),
    path('doctor/dashboard/', DoctorDashboardView.as_view()),

    # Doctor manual update (rating, notes, status)
    path('<int:report_id>/update/', UpdateReportByDoctorView.as_view()),
]
