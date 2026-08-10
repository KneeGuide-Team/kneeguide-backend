from rest_framework import serializers
from .models import ExerciseReport
from apps.users.serializers import UserSerializer
from apps.exercises.serializers import ExerciseSerializer


class ExerciseReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseReport
        fields = '__all__'


class PatientSummarySerializer(serializers.Serializer):
    patient = UserSerializer()
    last_report = ExerciseReportSerializer()
    last_angle = serializers.FloatField()
    total_exercises = serializers.IntegerField()
