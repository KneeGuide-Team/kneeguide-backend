from django.urls import path
from .views import CreateExerciseView, GetExercisesForPatientView

urlpatterns = [
    path('create/', CreateExerciseView.as_view()),
    path('patient/<int:patient_id>/', GetExercisesForPatientView.as_view()),
]
