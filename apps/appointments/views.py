from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import Appointment
from .serializers import AppointmentSerializer
from apps.users.permissions import IsDoctor, IsPatient


# ===============================
#  🧩 OBJECT-LEVEL PERMISSION
# ===============================

class IsOwnerOrDoctor(permissions.BasePermission):
    """
    يسمح للمريض فقط بمشاهدة مواعيده
    ويسمح للدكتور فقط بمشاهدة/إدارة مواعيده
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated:
            return False

        # الدكتور يرى فقط مواعيده (doctor_id)
        if user.role == "doctor" and obj.doctor_id == user.id:
            return True

        # المريض يرى فقط مواعيده (patient_id)
        if user.role == "patient" and obj.patient_id == user.id:
            return True

        # السوبر أدمن دائماً مسموح
        return user.is_staff or user.is_superuser


# ===============================
#  🟢 CREATE — Doctor Only
# ===============================

class CreateAppointmentView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    def post(self, request):
        data = request.data.copy()

        # تأكيد أن الدكتور هو المنشئ الحقيقي
        data["doctor"] = request.user.id

        serializer = AppointmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Appointment created"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ===============================
#  🔍 GET APPOINTMENT DETAILS
# ===============================

class GetAppointmentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        if not IsOwnerOrDoctor().has_object_permission(request, self, appointment):
            return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ===============================
#  ✏️ UPDATE — Doctor Only
# ===============================

class UpdateAppointmentView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    def _update(self, request, appointment_id, partial):
        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        # الدكتور فقط يعدّل مواعيده
        if appointment.doctor_id != request.user.id:
            return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        serializer = AppointmentSerializer(appointment, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Appointment updated"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, appointment_id):
        return self._update(request, appointment_id, partial=False)

    def patch(self, request, appointment_id):
        return self._update(request, appointment_id, partial=True)


# ===============================
#  ❌ CANCEL — Doctor Only
# ===============================

class DeleteAppointmentView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    def delete(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        # الدكتور فقط يلغي مواعيده
        if appointment.doctor_id != request.user.id:
            return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        appointment.status = "cancelled"
        appointment.save()

        return Response({"message": "Appointment cancelled"}, status=status.HTTP_200_OK)


# ===============================
#  📄 Patient Appointments — Patient Only
# ===============================

class GetAppointmentsForPatientView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, patient_id):
        user = request.user

        # منع المريض من مشاهدة مواعيد غيره
        if user.role == "patient" and user.id != patient_id:
            return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        # الدكتور يشوف مواعيد مرضاه (اختياري)
        if user.role == "doctor":
            appointments = Appointment.objects.filter(doctor_id=user.id, patient_id=patient_id)
        else:
            appointments = Appointment.objects.filter(patient_id=patient_id)

        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ===============================
#  📅 Doctor Appointments — Doctor Only
# ===============================

class GetAppointmentsForDoctorView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    def get(self, request, doctor_id):
        # الدكتور لا يرى مواعيد غيره
        if request.user.id != doctor_id:
            return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        appointments = Appointment.objects.filter(doctor_id=doctor_id).order_by("date", "time")
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
