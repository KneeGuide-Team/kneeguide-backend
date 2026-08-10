from rest_framework.permissions import BasePermission


class IsDoctor(BasePermission):
    """
    يسمح فقط للمستخدمين اللي role = doctor
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "doctor")


class IsPatient(BasePermission):
    """
    يسمح فقط للمستخدمين اللي role = patient
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "patient")
