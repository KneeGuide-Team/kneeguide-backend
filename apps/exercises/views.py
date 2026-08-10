from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Exercise
from .serializers import ExerciseSerializer


class IsDoctor(permissions.BasePermission):
    """
    يسمح فقط للمستخدم اللي دوره Doctor
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            getattr(request.user, "role", None) == "doctor"
        )


class CreateExerciseView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    def post(self, request):
        data = request.data.copy()

        # اجباراً: من أنشأ التمرين هو الدكتور الحالي
        data["assigned_by"] = request.user.id

        serializer = ExerciseSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Exercise created successfully"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetExercisesForPatientView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, patient_id):
        user = request.user

        # لو المستخدم مريض، ما يسمح له يشوف إلا تمارينه فقط
        if getattr(user, "role", None) == "patient" and user.id != patient_id and not user.is_staff and not user.is_superuser:
            return Response(
                {"detail": "You are not allowed to view other patients' exercises."},
                status=status.HTTP_403_FORBIDDEN
            )

        # الدكتور أو السوبر يوزر مسموح لهم يشوفوا أي مريض
        exercises = Exercise.objects.filter(assigned_to_id=patient_id).order_by("-created_at")
        serializer = ExerciseSerializer(exercises, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
