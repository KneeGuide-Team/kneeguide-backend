from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import ExerciseReportSerializer
from .models import ExerciseReport
from .utils import analyze_motion


class IsDoctor(permissions.BasePermission):
    """
    يسمح فقط لمستخدم دوره Doctor
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, "role", None) == "doctor"
        )


class SubmitReportView(APIView):
    """
    حفظ تقرير التمرين مع تحليل الحركة.
    يمكن استخدامه من تطبيق المريض أو الدكتور،
    لكن لو المستخدم مريض، نجبر الحقل patient = request.user.id
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data.copy()

        # لو المستخدم مريض، يمنع يرفع تقرير لمريض آخر
        user = request.user
        if getattr(user, "role", None) == "patient":
            data["patient"] = user.id

        motion_data = data.get("motion_data", [])

        normal_angle = float(data.get("normal_angle", 135))

        max_angle, deviation, normal_angle, performance_status, duration = analyze_motion(
            motion_data,
            normal_angle
        )

        data["max_angle"] = max_angle
        data["deviation"] = deviation
        data["performance_status"] = performance_status
        data["duration_seconds"] = duration

        serializer = ExerciseReportSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Report saved successfully",
                "analysis": {
                    "max_angle": max_angle,
                    "deviation": deviation,
                    "status": performance_status,
                    "duration": duration
                }
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetReportsForPatientView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, patient_id):
        user = request.user

        # المريض ما يشوف إلا تقاريره
        if getattr(user, "role", None) == "patient" and user.id != patient_id and not user.is_staff and not user.is_superuser:
            return Response(
                {"detail": "You are not allowed to view other patients' reports."},
                status=status.HTTP_403_FORBIDDEN
            )

        reports = ExerciseReport.objects.filter(patient_id=patient_id).order_by('-created_at')
        serializer = ExerciseReportSerializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PatientDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, patient_id):
        from apps.exercises.models import Exercise
        from apps.exercises.serializers import ExerciseSerializer

        user = request.user

        # نفس حماية الخصوصية
        if getattr(user, "role", None) == "patient" and user.id != patient_id and not user.is_staff and not user.is_superuser:
            return Response(
                {"detail": "You are not allowed to view other patients' dashboard."},
                status=status.HTTP_403_FORBIDDEN
            )

        last_report = ExerciseReport.objects.filter(
            patient_id=patient_id
        ).order_by('-created_at').first()

        last_report_data = ExerciseReportSerializer(last_report).data if last_report else None
        last_angle = last_report.max_angle if last_report else None

        assigned_exercises = Exercise.objects.filter(assigned_to_id=patient_id)
        exercises_data = ExerciseSerializer(assigned_exercises, many=True).data

        return Response({
            "last_report": last_report_data,
            "last_angle": last_angle,
            "assigned_exercises": exercises_data
        }, status=status.HTTP_200_OK)


class DoctorDashboardView(APIView):
    """
    Dashboard للأطباء فقط – يشاهدون كل المرضى
    """
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    def get(self, request):
        from django.contrib.auth import get_user_model
        from apps.exercises.models import Exercise
        from apps.exercises.serializers import ExerciseSerializer

        User = get_user_model()

        patients = User.objects.filter(role="patient")
        dashboard_data = []

        for patient in patients:
            last_report = ExerciseReport.objects.filter(
                patient_id=patient.id
            ).order_by('-created_at').first()

            last_report_data = ExerciseReportSerializer(last_report).data if last_report else None
            last_angle = last_report.max_angle if last_report else None

            total_exercises = Exercise.objects.filter(assigned_to_id=patient.id).count()

            dashboard_data.append({
                "patient": {
                    "id": patient.id,
                    "first_name": patient.first_name,
                    "last_name": patient.last_name,
                    "email": patient.email,
                    "phone": patient.phone,
                },
                "last_report": last_report_data,
                "last_angle": last_angle,
                "total_exercises": total_exercises,
            })

        return Response(dashboard_data, status=status.HTTP_200_OK)

class UpdateReportByDoctorView(APIView):
    """
    يسمح للدكتور بتعديل:
    - rating
    - doctor_notes
    - status
    """

    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, report_id):
        try:
            report = ExerciseReport.objects.get(id=report_id)
        except ExerciseReport.DoesNotExist:
            return Response({"error": "Report not found"}, status=404)

        # فقط الدكتور مسموح
        if request.user.role != "doctor":
            return Response({"detail": "Not allowed"}, status=403)

        allowed_fields = ["rating", "doctor_notes", "status"]
        data = {k: v for k, v in request.data.items() if k in allowed_fields}

        if not data:
            return Response({"error": "No valid fields"}, status=400)

        for field, value in data.items():
            setattr(report, field, value)

        report.save()

        return Response({"message": "Report updated successfully"}, status=200)
