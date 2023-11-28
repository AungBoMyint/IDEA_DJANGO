from rest_framework import permissions
from . import models
from django.shortcuts import get_object_or_404

class IsCurrentUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        student_id = view.kwargs.get("pk")
        student = get_object_or_404(models.Student,pk=student_id)
        return student.user == request.user
        